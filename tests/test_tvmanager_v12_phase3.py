from __future__ import annotations

from datetime import date

from tvmanager_v12.adapters import DownloadSubmission
from tvmanager_v12.compat import CallableDownloaderAdapter, CallableProviderAdapter
from tvmanager_v12.domain import DownloadCandidate, Episode, EpisodeStatus, QualityProfile, Show
from tvmanager_v12.orchestration import SearchOrchestrator
from tvmanager_v12.persistence import SQLiteShowRepository
from tvmanager_v12.queue import ActivityStore, QueueItem, QueueState


def _show() -> Show:
    return Show(
        title="Example Show",
        indexer="tvdb",
        indexer_id="42",
        episodes=[Episode(1, 1, "Pilot", date(2026, 9, 1), EpisodeStatus.WANTED)],
        quality_profile="HD",
    )


def test_sqlite_repository_round_trip(tmp_path):
    repo = SQLiteShowRepository(tmp_path / "tvmanager.db")
    show = _show()
    repo.save(show)

    loaded = repo.get("TVDB", "42")
    assert loaded is not None
    assert loaded.title == "Example Show"
    assert loaded.episodes[0].key == "S01E01"
    assert loaded.episodes[0].status == EpisodeStatus.WANTED
    assert repo.count() == 1


def test_search_orchestrator_skips_unavailable_and_submits_best_candidate():
    show = _show()
    episode = show.episodes[0]
    profile = QualityProfile("HD", allowed=("720p", "1080p"), preferred=("1080p",))

    healthy = CallableProviderAdapter(
        "healthy",
        search_fn=lambda request: (
            DownloadCandidate(f"{request.show.title}.S01E01.720p", "healthy", "720p", seeders=200, protocol="torrent"),
            DownloadCandidate(f"{request.show.title}.S01E01.1080p", "healthy", "1080p", seeders=20, protocol="torrent"),
        ),
    )
    down = CallableDownloaderAdapter(
        "downloader",
        submit_fn=lambda request: DownloadSubmission(True, client_id="abc123", message="queued"),
    )

    run = SearchOrchestrator([healthy], downloader=down).run(show, episode, profile, auto_submit=True)

    assert run.decision.chosen is not None
    assert run.decision.chosen.quality == "1080p"
    assert run.submitted is True
    assert run.client_id == "abc123"
    assert run.providers[0].error is None


def test_activity_store_recovers_unknown_client_and_history():
    activity = ActivityStore()
    activity.add(QueueItem("one", "Example.Show.S01E01", "client"))
    activity.reconcile("one", QueueState.DOWNLOADING, progress=50)
    recovered = activity.reconcile("missing", QueueState.COMPLETED, progress=100, message="found during reconciliation")

    assert activity.queue["one"].progress == 50
    assert recovered.state == QueueState.COMPLETED
    assert recovered.downloader == "unknown"
    assert len(activity.recent_history()) == 3
