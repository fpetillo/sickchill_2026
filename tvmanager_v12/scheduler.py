from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Callable


@dataclass(slots=True, frozen=True)
class JobSnapshot:
    name: str
    interval_seconds: int
    enabled: bool
    next_run: datetime
    last_started: datetime | None
    last_finished: datetime | None
    last_success: bool | None
    last_error: str
    lease_until: datetime | None
    run_count: int
    failure_count: int


class SQLiteJobStore:
    """Persistent scheduler state with crash-safe leases."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.path, timeout=15)
        db.row_factory = sqlite3.Row
        return db

    def _initialize(self) -> None:
        with self._connect() as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.execute(
                """
                CREATE TABLE IF NOT EXISTS v12_jobs (
                    name TEXT PRIMARY KEY,
                    interval_seconds INTEGER NOT NULL,
                    enabled INTEGER NOT NULL DEFAULT 1,
                    next_run TEXT NOT NULL,
                    last_started TEXT,
                    last_finished TEXT,
                    last_success INTEGER,
                    last_error TEXT NOT NULL DEFAULT '',
                    lease_until TEXT,
                    run_count INTEGER NOT NULL DEFAULT 0,
                    failure_count INTEGER NOT NULL DEFAULT 0
                )
                """
            )

    @staticmethod
    def _parse(value: str | None) -> datetime | None:
        return datetime.fromisoformat(value) if value else None

    def register(self, name: str, interval_seconds: int, *, enabled: bool = True, start_at: datetime | None = None) -> None:
        if interval_seconds <= 0:
            raise ValueError("interval_seconds must be positive")
        next_run = start_at or datetime.now(timezone.utc)
        with self._connect() as db:
            db.execute(
                """
                INSERT INTO v12_jobs(name,interval_seconds,enabled,next_run)
                VALUES(?,?,?,?)
                ON CONFLICT(name) DO UPDATE SET
                    interval_seconds=excluded.interval_seconds,
                    enabled=excluded.enabled
                """,
                (name, int(interval_seconds), int(enabled), next_run.isoformat()),
            )

    def set_enabled(self, name: str, enabled: bool) -> None:
        with self._connect() as db:
            cursor = db.execute("UPDATE v12_jobs SET enabled=? WHERE name=?", (int(enabled), name))
        if cursor.rowcount == 0:
            raise LookupError(f"job not found: {name}")

    def list(self) -> list[JobSnapshot]:
        with self._connect() as db:
            rows = db.execute("SELECT * FROM v12_jobs ORDER BY name").fetchall()
        return [self._snapshot(row) for row in rows]

    def due(self, now: datetime | None = None) -> list[JobSnapshot]:
        stamp = now or datetime.now(timezone.utc)
        with self._connect() as db:
            rows = db.execute(
                """
                SELECT * FROM v12_jobs
                WHERE enabled=1 AND next_run<=? AND (lease_until IS NULL OR lease_until<=?)
                ORDER BY next_run, name
                """,
                (stamp.isoformat(), stamp.isoformat()),
            ).fetchall()
        return [self._snapshot(row) for row in rows]

    def acquire(self, name: str, *, lease_seconds: int = 300, now: datetime | None = None) -> bool:
        stamp = now or datetime.now(timezone.utc)
        lease_until = stamp + timedelta(seconds=max(int(lease_seconds), 1))
        with self._connect() as db:
            cursor = db.execute(
                """
                UPDATE v12_jobs
                SET lease_until=?, last_started=?
                WHERE name=? AND enabled=1 AND next_run<=?
                  AND (lease_until IS NULL OR lease_until<=?)
                """,
                (lease_until.isoformat(), stamp.isoformat(), name, stamp.isoformat(), stamp.isoformat()),
            )
        return cursor.rowcount == 1

    def complete(self, name: str, *, success: bool, error: str = "", now: datetime | None = None) -> None:
        stamp = now or datetime.now(timezone.utc)
        with self._connect() as db:
            row = db.execute("SELECT interval_seconds FROM v12_jobs WHERE name=?", (name,)).fetchone()
            if row is None:
                raise LookupError(f"job not found: {name}")
            next_run = stamp + timedelta(seconds=int(row["interval_seconds"]))
            db.execute(
                """
                UPDATE v12_jobs SET
                    next_run=?, last_finished=?, last_success=?, last_error=?, lease_until=NULL,
                    run_count=run_count+1,
                    failure_count=failure_count+?
                WHERE name=?
                """,
                (next_run.isoformat(), stamp.isoformat(), int(success), error, int(not success), name),
            )

    def release_expired_leases(self, now: datetime | None = None) -> int:
        stamp = now or datetime.now(timezone.utc)
        with self._connect() as db:
            cursor = db.execute(
                "UPDATE v12_jobs SET lease_until=NULL WHERE lease_until IS NOT NULL AND lease_until<=?",
                (stamp.isoformat(),),
            )
        return max(cursor.rowcount, 0)

    def _snapshot(self, row: sqlite3.Row) -> JobSnapshot:
        last_success = row["last_success"]
        return JobSnapshot(
            name=row["name"],
            interval_seconds=int(row["interval_seconds"]),
            enabled=bool(row["enabled"]),
            next_run=self._parse(row["next_run"]) or datetime.now(timezone.utc),
            last_started=self._parse(row["last_started"]),
            last_finished=self._parse(row["last_finished"]),
            last_success=None if last_success is None else bool(last_success),
            last_error=row["last_error"],
            lease_until=self._parse(row["lease_until"]),
            run_count=int(row["run_count"]),
            failure_count=int(row["failure_count"]),
        )


@dataclass(slots=True)
class SchedulerEngine:
    store: SQLiteJobStore
    handlers: dict[str, Callable[[], object]]
    lease_seconds: int = 300

    def tick(self, now: datetime | None = None) -> list[tuple[str, bool, str]]:
        """Run each due job once; one failing job cannot stop the scheduler."""
        stamp = now or datetime.now(timezone.utc)
        outcomes: list[tuple[str, bool, str]] = []
        self.store.release_expired_leases(stamp)
        for job in self.store.due(stamp):
            handler = self.handlers.get(job.name)
            if handler is None:
                outcomes.append((job.name, False, "No handler registered"))
                continue
            if not self.store.acquire(job.name, lease_seconds=self.lease_seconds, now=stamp):
                continue
            try:
                handler()
            except Exception as exc:
                message = f"{type(exc).__name__}: {exc}"
                self.store.complete(job.name, success=False, error=message)
                outcomes.append((job.name, False, message))
            else:
                self.store.complete(job.name, success=True)
                outcomes.append((job.name, True, ""))
        return outcomes
