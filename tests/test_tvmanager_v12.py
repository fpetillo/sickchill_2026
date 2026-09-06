from __future__ import annotations

import sqlite3
from pathlib import Path

from tvmanager_v12.domain import DownloadCandidate, Episode, EpisodeStatus, QualityProfile, Show
from tvmanager_v12.migration import export_sickchill_database


def test_quality_profile_candidate_scoring() -> None:
    profile = QualityProfile(
        name="HD preferred",
        allowed=("720p", "1080p"),
        preferred=("1080p",),
        cutoff="1080p",
    )
    candidate = DownloadCandidate(
        title="Example.Show.S01E01.1080p.WEB-DL",
        provider="example",
        quality="1080p",
        seeders=42,
    )
    assert candidate.score(profile, required_words=("WEB-DL",)) > 0
    assert candidate.score(profile, rejected_words=("WEB-DL",)) == -1


def test_show_missing_episode_tracking() -> None:
    show = Show(title="Example", indexer="tvdb", indexer_id="123")
    show.episodes.extend(
        [
            Episode(1, 1, status=EpisodeStatus.DOWNLOADED),
            Episode(1, 2, status=EpisodeStatus.WANTED),
            Episode(1, 3, status=EpisodeStatus.FAILED),
        ]
    )
    assert [episode.key for episode in show.missing()] == ["S01E02", "S01E03"]


def test_migration_export_is_read_only_and_preserves_rows(tmp_path: Path) -> None:
    database = tmp_path / "sickbeard.db"
    with sqlite3.connect(database) as connection:
        connection.execute("CREATE TABLE tv_shows (show_id INTEGER PRIMARY KEY, show_name TEXT, indexer_id INTEGER)")
        connection.execute("CREATE TABLE tv_episodes (episode_id INTEGER PRIMARY KEY, showid INTEGER, season INTEGER, episode INTEGER, status INTEGER)")
        connection.execute("INSERT INTO tv_shows VALUES (1, 'Example Show', 12345)")
        connection.execute("INSERT INTO tv_episodes VALUES (10, 1, 1, 1, 4)")
        connection.execute("PRAGMA user_version = 44")

    manifest = export_sickchill_database(database)

    assert manifest.sqlite_user_version == 44
    assert manifest.counts["tv_shows"] == 1
    assert manifest.counts["tv_episodes"] == 1
    shows = next(table.rows for table in manifest.tables if table.name == "tv_shows")
    assert shows[0]["show_name"] == "Example Show"
