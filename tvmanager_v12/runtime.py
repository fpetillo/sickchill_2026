from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from .queue import HistoryEvent, QueueItem, QueueState


def _dt(value: datetime | str | None) -> datetime:
    if isinstance(value, datetime):
        return value
    if value:
        return datetime.fromisoformat(str(value))
    return datetime.now(timezone.utc)


@dataclass(slots=True, frozen=True)
class SearchHistoryRecord:
    id: int
    started_at: datetime
    completed_at: datetime
    show_key: str
    episode_key: str
    query: str
    chosen_title: str | None
    chosen_provider: str | None
    submitted: bool
    client_id: str | None
    payload: dict[str, Any]


class SQLiteRuntimeStore:
    """Restart-safe queue, history, search, and scheduler persistence for v12.

    Runtime data is intentionally stored in a v12-owned SQLite database rather
    than modifying legacy SickChill tables. WAL mode and short transactions keep
    the store suitable for background jobs and API reads in the same process.
    """

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.path, timeout=15)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        return db

    def _initialize(self) -> None:
        with self._connect() as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.executescript(
                """
                CREATE TABLE IF NOT EXISTS v12_queue (
                    client_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    downloader TEXT NOT NULL,
                    state TEXT NOT NULL,
                    progress REAL NOT NULL DEFAULT 0,
                    added_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    message TEXT NOT NULL DEFAULT ''
                );
                CREATE TABLE IF NOT EXISTS v12_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    kind TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    message TEXT NOT NULL,
                    client_id TEXT,
                    show_key TEXT,
                    episode_key TEXT
                );
                CREATE INDEX IF NOT EXISTS idx_v12_history_time ON v12_history(timestamp DESC);
                CREATE INDEX IF NOT EXISTS idx_v12_history_client ON v12_history(client_id);
                CREATE TABLE IF NOT EXISTS v12_search_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    started_at TEXT NOT NULL,
                    completed_at TEXT NOT NULL,
                    show_key TEXT NOT NULL,
                    episode_key TEXT NOT NULL,
                    query TEXT NOT NULL,
                    chosen_title TEXT,
                    chosen_provider TEXT,
                    submitted INTEGER NOT NULL DEFAULT 0,
                    client_id TEXT,
                    payload TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_v12_search_time ON v12_search_history(completed_at DESC);
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
                );
                """
            )

    def save_queue_item(self, item: QueueItem) -> None:
        with self._connect() as db:
            db.execute(
                """
                INSERT INTO v12_queue(client_id,title,downloader,state,progress,added_at,updated_at,message)
                VALUES(?,?,?,?,?,?,?,?)
                ON CONFLICT(client_id) DO UPDATE SET
                    title=excluded.title, downloader=excluded.downloader,
                    state=excluded.state, progress=excluded.progress,
                    updated_at=excluded.updated_at, message=excluded.message
                """,
                (
                    item.client_id,
                    item.title,
                    item.downloader,
                    item.state.value,
                    item.progress,
                    item.added_at.isoformat(),
                    item.updated_at.isoformat(),
                    item.message,
                ),
            )

    def delete_queue_item(self, client_id: str) -> bool:
        with self._connect() as db:
            cursor = db.execute("DELETE FROM v12_queue WHERE client_id=?", (client_id,))
        return cursor.rowcount > 0

    def load_queue(self) -> list[QueueItem]:
        with self._connect() as db:
            rows = db.execute("SELECT * FROM v12_queue ORDER BY added_at").fetchall()
        return [
            QueueItem(
                client_id=row["client_id"],
                title=row["title"],
                downloader=row["downloader"],
                state=QueueState(row["state"]),
                progress=float(row["progress"]),
                added_at=_dt(row["added_at"]),
                updated_at=_dt(row["updated_at"]),
                message=row["message"],
            )
            for row in rows
        ]

    def record_history(self, event: HistoryEvent) -> int:
        with self._connect() as db:
            cursor = db.execute(
                """INSERT INTO v12_history(kind,timestamp,message,client_id,show_key,episode_key)
                   VALUES(?,?,?,?,?,?)""",
                (
                    event.kind,
                    event.timestamp.isoformat(),
                    event.message,
                    event.client_id,
                    event.show_key,
                    event.episode_key,
                ),
            )
            return int(cursor.lastrowid)

    def recent_history(self, limit: int = 100) -> list[HistoryEvent]:
        with self._connect() as db:
            rows = db.execute(
                "SELECT * FROM v12_history ORDER BY id DESC LIMIT ?", (max(int(limit), 0),)
            ).fetchall()
        return [
            HistoryEvent(
                kind=row["kind"],
                timestamp=_dt(row["timestamp"]),
                message=row["message"],
                client_id=row["client_id"],
                show_key=row["show_key"],
                episode_key=row["episode_key"],
            )
            for row in rows
        ]

    def prune_history(self, keep: int = 5000) -> int:
        keep = max(int(keep), 0)
        with self._connect() as db:
            cursor = db.execute(
                "DELETE FROM v12_history WHERE id NOT IN (SELECT id FROM v12_history ORDER BY id DESC LIMIT ?)",
                (keep,),
            )
        return max(cursor.rowcount, 0)

    def record_search(self, run: Any) -> int:
        chosen = getattr(run.decision, "chosen", None)
        payload = {
            "providers": [
                {
                    "provider": result.provider,
                    "error": result.error,
                    "skipped": result.skipped,
                    "candidates": [asdict(candidate) for candidate in result.candidates],
                }
                for result in run.providers
            ],
            "decisions": [
                {
                    "candidate": asdict(item.candidate),
                    "state": item.state.value,
                    "score": item.score,
                    "reasons": [asdict(reason) for reason in item.reasons],
                }
                for item in run.decision.candidates
            ],
            "submission_message": run.submission_message,
        }
        with self._connect() as db:
            cursor = db.execute(
                """
                INSERT INTO v12_search_history(
                    started_at,completed_at,show_key,episode_key,query,
                    chosen_title,chosen_provider,submitted,client_id,payload
                ) VALUES(?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    run.started_at.isoformat(),
                    run.completed_at.isoformat(),
                    run.show_key,
                    run.episode_key,
                    run.query,
                    chosen.title if chosen else None,
                    chosen.provider if chosen else None,
                    int(run.submitted),
                    run.client_id,
                    json.dumps(payload, sort_keys=True),
                ),
            )
            return int(cursor.lastrowid)

    def recent_searches(self, limit: int = 50) -> list[SearchHistoryRecord]:
        with self._connect() as db:
            rows = db.execute(
                "SELECT * FROM v12_search_history ORDER BY id DESC LIMIT ?", (max(int(limit), 0),)
            ).fetchall()
        return [
            SearchHistoryRecord(
                id=int(row["id"]),
                started_at=_dt(row["started_at"]),
                completed_at=_dt(row["completed_at"]),
                show_key=row["show_key"],
                episode_key=row["episode_key"],
                query=row["query"],
                chosen_title=row["chosen_title"],
                chosen_provider=row["chosen_provider"],
                submitted=bool(row["submitted"]),
                client_id=row["client_id"],
                payload=json.loads(row["payload"]),
            )
            for row in rows
        ]

    def initialize_queue(self, items: Iterable[QueueItem]) -> None:
        for item in items:
            self.save_queue_item(item)


class PersistentActivityStore:
    """ActivityStore-compatible facade that survives process restarts."""

    def __init__(self, store: SQLiteRuntimeStore, *, max_history: int = 5000) -> None:
        self.store = store
        self.max_history = max_history
        self.queue: dict[str, QueueItem] = {item.client_id: item for item in store.load_queue()}

    @property
    def history(self) -> list[HistoryEvent]:
        return list(reversed(self.store.recent_history(self.max_history)))

    def add(self, item: QueueItem) -> None:
        self.queue[item.client_id] = item
        self.store.save_queue_item(item)
        self.record("queued", f"Queued {item.title}", client_id=item.client_id)

    def reconcile(
        self,
        client_id: str,
        state: QueueState,
        *,
        progress: float | None = None,
        message: str = "",
    ) -> QueueItem:
        item = self.queue.get(client_id)
        if item is None:
            item = QueueItem(
                client_id=client_id,
                title=client_id,
                downloader="unknown",
                state=QueueState.UNKNOWN,
            )
            self.queue[client_id] = item
        item.update(state, progress=progress, message=message)
        self.store.save_queue_item(item)
        self.record(
            "queue-state",
            f"{client_id} -> {state.value}: {message}".rstrip(),
            client_id=client_id,
        )
        return item

    def remove(self, client_id: str, *, message: str = "") -> bool:
        item = self.queue.pop(client_id, None)
        if item is None:
            return False
        self.store.delete_queue_item(client_id)
        self.record("removed", message or f"Removed {item.title}", client_id=client_id)
        return True

    def record(
        self,
        kind: str,
        message: str,
        *,
        client_id: str | None = None,
        show_key: str | None = None,
        episode_key: str | None = None,
    ) -> None:
        self.store.record_history(
            HistoryEvent(
                kind=kind,
                timestamp=datetime.now(timezone.utc),
                message=message,
                client_id=client_id,
                show_key=show_key,
                episode_key=episode_key,
            )
        )
        self.store.prune_history(self.max_history)

    def active(self) -> list[QueueItem]:
        return sorted(self.queue.values(), key=lambda item: item.added_at)

    def recent_history(self, limit: int = 100) -> list[HistoryEvent]:
        return self.store.recent_history(limit)
