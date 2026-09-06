from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from tvmanager_v12.adapters import DownloadSubmission
from tvmanager_v12.api import TVManagerAPI
from tvmanager_v12.compat import CallableDownloaderAdapter, CallableProviderAdapter
from tvmanager_v12.domain import DownloadCandidate, Episode, EpisodeStatus, QualityProfile, Show
from tvmanager_v12.orchestration import SearchOrchestrator
from tvmanager_v12.persistence import SQLiteShowRepository
from tvmanager_v12.providers import NewznabProviderAdapter
from tvmanager_v12.queue import QueueItem, QueueState
from tvmanager_v12.runtime import PersistentActivityStore, SQLiteRuntimeStore
from tvmanager_v12.scheduler import SchedulerEngine, SQLiteJobStore
from tvmanager_v12.service import LibraryService


def _show() -> Show:
    return Show(
        title="Example Show",
        indexer="tvdb",
        indexer_id="42",
        episodes=[Episode(1, 1, "Pilot", date(2026, 9, 1), EpisodeStatus.WANTED)],
        quality_profile="HD",
    )


def test_persistent_activity_survives_restart(tmp_path):
    store = SQLiteRuntimeStore(tmp_path / "runtime.db")
    activity = PersistentActivityStore(store)
    activity.add(QueueItem("abc", "Example.Show.S01E01.1080p", "client"))
    activity.reconcile("abc", QueueState.DOWNLOADING, progress=47.5, message="working")

    restarted = PersistentActivityStore(SQLiteRuntimeStore(tmp_path / "runtime.db"))
    assert restarted.queue["abc"].state == QueueState.DOWNLOADING
    assert restarted.queue["abc"].progress == 47.5
    assert restarted.recent_history(2)[0].client_id == "abc"


def test_search_orchestration_persists_decision_and_queue(tmp_path):
    runtime = SQLiteRuntimeStore(tmp_path / "runtime.db")
    activity = PersistentActivityStore(runtime)
    show = _show()
    episode = show.episodes[0]
    profile = QualityProfile("HD", allowed=("720p", "1080p"), preferred=("1080p",))
    provider = CallableProviderAdapter(
        "provider",
        search_fn=lambda request: (
            DownloadCandidate(
                f"{request.show.title}.S01E01.1080p.WEB-DL",
                "provider",
                "1080p",
                seeders=30,
                protocol="torrent",
                download_url="magnet:?xt=urn:btih:abc",
                guid="abc",
            ),
        ),
    )
    downloader = CallableDownloaderAdapter(
        "client",
        submit_fn=lambda request: DownloadSubmission(True, client_id="abc", message="queued"),
    )
    orchestrator = SearchOrchestrator(
        [provider],
        downloader=downloader,
        activity=activity,
        persistent_recorder=runtime.record_search,
    )

    run = orchestrator.run(show, episode, profile, auto_submit=True)

    assert run.submitted is True
    assert runtime.load_queue()[0].client_id == "abc"
    searches = runtime.recent_searches()
    assert searches[0].chosen_title is not None
    assert searches[0].payload["decisions"][0]["state"] == "accepted"


def test_scheduler_is_restart_safe_and_records_failure(tmp_path):
    path = tmp_path / "runtime.db"
    store = SQLiteJobStore(path)
    now = datetime(2026, 9, 6, 10, 0, tzinfo=timezone.utc)
    store.register("ok", 60, start_at=now)
    store.register("bad", 60, start_at=now)
    calls: list[str] = []

    def ok():
        calls.append("ok")

    def bad():
        raise RuntimeError("boom")

    outcomes = SchedulerEngine(store, {"ok": ok, "bad": bad}).tick(now)
    snapshots = {item.name: item for item in SQLiteJobStore(path).list()}

    assert sorted(name for name, _, _ in outcomes) == ["bad", "ok"]
    assert calls == ["ok"]
    assert snapshots["ok"].last_success is True
    assert snapshots["bad"].last_success is False
    assert snapshots["bad"].failure_count == 1
    assert "boom" in snapshots["bad"].last_error


def test_scheduler_expired_lease_can_be_recovered(tmp_path):
    store = SQLiteJobStore(tmp_path / "runtime.db")
    now = datetime(2026, 9, 6, 10, 0, tzinfo=timezone.utc)
    store.register("search", 60, start_at=now)
    assert store.acquire("search", lease_seconds=5, now=now)
    assert store.due(now + timedelta(seconds=2)) == []
    assert [job.name for job in store.due(now + timedelta(seconds=6))] == ["search"]


class _StaticNewznab(NewznabProviderAdapter):
    def _request(self, params):
        xml = b"""<?xml version='1.0'?><rss xmlns:newznab='http://www.newznab.com/DTD/2010/feeds/attributes/'><channel><item><title>Example.Show.S01E01.1080p.WEB-DL</title><link>https://indexer/item.nzb</link><guid>guid-1</guid><newznab:attr name='size' value='12345'/></item></channel></rss>"""
        return xml, 1


def test_newznab_adapter_returns_downloadable_candidate():
    provider = _StaticNewznab("indexer", "https://indexer.invalid")
    request_show = _show()
    request = __import__("tvmanager_v12.adapters", fromlist=["SearchRequest"]).SearchRequest(
        request_show,
        request_show.episodes[0],
        "Example Show S01E01",
    )
    candidate = provider.search(request)[0]
    assert candidate.protocol == "nzb"
    assert candidate.quality == "1080p"
    assert candidate.download_url == "https://indexer/item.nzb"
    assert candidate.guid == "guid-1"
    assert candidate.size_bytes == 12345


def test_v1_api_exposes_status_library_jobs_and_episode_update(tmp_path):
    show_db = SQLiteShowRepository(tmp_path / "shows.db")
    show_db.save(_show())
    library = LibraryService(show_db)
    runtime = SQLiteRuntimeStore(tmp_path / "runtime.db")
    jobs = SQLiteJobStore(tmp_path / "runtime.db")
    jobs.register("recent-search", 300)
    api = TVManagerAPI(library, runtime, jobs)

    code, status = api.dispatch("GET", "/api/v1/status", {})
    assert int(code) == 200
    assert status["development_version"] == "12.0.0-dev.4"
    assert status["shows"] == 1

    code, payload = api.dispatch(
        "POST",
        "/api/v1/episode/status",
        {},
        {"indexer": "tvdb", "indexer_id": "42", "season": 1, "number": 1, "status": "skipped"},
    )
    assert int(code) == 200
    assert payload["episode"]["status"] == "skipped"
