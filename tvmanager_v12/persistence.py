from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict
from datetime import date
from pathlib import Path

from .domain import Episode, EpisodeStatus, Show


class SQLiteShowRepository:
    """Small native-v12 repository with explicit schema ownership.

    This does not mutate the legacy SickChill database. It is intended for the
    v12 runtime and can be populated from migration/compatibility services.
    """

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as db:
            db.execute(
                """
                CREATE TABLE IF NOT EXISTS v12_shows (
                    indexer TEXT NOT NULL,
                    indexer_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    PRIMARY KEY (indexer, indexer_id)
                )
                """
            )
            db.execute("CREATE INDEX IF NOT EXISTS idx_v12_shows_title ON v12_shows(title)")

    @staticmethod
    def _episode_payload(episode: Episode) -> dict[str, object]:
        data = asdict(episode)
        data["status"] = episode.status.value
        data["airdate"] = episode.airdate.isoformat() if episode.airdate else None
        return data

    @classmethod
    def _serialize(cls, show: Show) -> str:
        return json.dumps(
            {
                "title": show.title,
                "indexer": show.indexer,
                "indexer_id": str(show.indexer_id),
                "episodes": [cls._episode_payload(episode) for episode in show.episodes],
                "paused": show.paused,
                "anime": show.anime,
                "sports": show.sports,
                "air_by_date": show.air_by_date,
                "scene": show.scene,
                "root_dir": show.root_dir,
                "quality_profile": show.quality_profile,
                "legacy_id": show.legacy_id,
            },
            sort_keys=True,
        )

    @staticmethod
    def _deserialize(payload: str) -> Show:
        data = json.loads(payload)
        episodes = []
        for raw in data.pop("episodes", []):
            raw["status"] = EpisodeStatus(raw.get("status", EpisodeStatus.UNKNOWN.value))
            raw["airdate"] = date.fromisoformat(raw["airdate"]) if raw.get("airdate") else None
            episodes.append(Episode(**raw))
        data["episodes"] = episodes
        return Show(**data)

    def all(self) -> list[Show]:
        with self._connect() as db:
            rows = db.execute("SELECT payload FROM v12_shows ORDER BY title COLLATE NOCASE").fetchall()
        return [self._deserialize(row["payload"]) for row in rows]

    def get(self, indexer: str, indexer_id: str) -> Show | None:
        with self._connect() as db:
            row = db.execute(
                "SELECT payload FROM v12_shows WHERE lower(indexer)=lower(?) AND indexer_id=?",
                (indexer.strip(), str(indexer_id).strip()),
            ).fetchone()
        return self._deserialize(row["payload"]) if row else None

    def save(self, show: Show) -> None:
        payload = self._serialize(show)
        with self._connect() as db:
            db.execute(
                """
                INSERT INTO v12_shows(indexer, indexer_id, title, payload)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(indexer, indexer_id) DO UPDATE SET
                    title=excluded.title,
                    payload=excluded.payload
                """,
                (show.indexer.casefold().strip(), str(show.indexer_id).strip(), show.title, payload),
            )

    def delete(self, indexer: str, indexer_id: str) -> bool:
        with self._connect() as db:
            cursor = db.execute(
                "DELETE FROM v12_shows WHERE lower(indexer)=lower(?) AND indexer_id=?",
                (indexer.strip(), str(indexer_id).strip()),
            )
        return cursor.rowcount > 0

    def count(self) -> int:
        with self._connect() as db:
            return int(db.execute("SELECT COUNT(*) FROM v12_shows").fetchone()[0])
