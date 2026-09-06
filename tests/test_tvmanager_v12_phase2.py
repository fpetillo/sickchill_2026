from datetime import datetime, timedelta, timezone

from tvmanager_v12.adapters import AdapterHealth, HealthState
from tvmanager_v12.domain import DownloadCandidate, Episode, EpisodeStatus, QualityProfile, Show
from tvmanager_v12.search import DecisionState, FailedDownloadSuppression, choose_candidate
from tvmanager_v12.service import InMemoryShowRepository, LibraryService


def test_search_decision_explains_rejections_and_selection():
    profile = QualityProfile("HD", allowed=("720p", "1080p"), preferred=("1080p",))
    candidates = [
        DownloadCandidate("Show.S01E01.1080p.WEB-DL", "alpha", "1080p", seeders=20),
        DownloadCandidate("Show.S01E01.720p.CAM", "beta", "720p", seeders=300),
        DownloadCandidate("Show.S01E01.2160p.WEB-DL", "gamma", "2160p", seeders=500),
    ]
    decision = choose_candidate(candidates, profile, rejected_words=("cam",))
    assert decision.chosen == candidates[0]
    assert decision.accepted_count == 1
    assert decision.candidates[1].state == DecisionState.REJECTED
    assert decision.candidates[1].reasons[0].code == "rejected-word"
    assert decision.candidates[2].reasons[0].code == "quality-not-allowed"


def test_failed_download_suppression_expires():
    candidate = DownloadCandidate("Show.S01E01.1080p.WEB-DL", "alpha", "1080p")
    start = datetime(2026, 9, 6, tzinfo=timezone.utc)
    suppression = FailedDownloadSuppression(ttl=timedelta(hours=1))
    suppression.suppress(candidate, now=start)
    assert suppression.is_suppressed(candidate, now=start + timedelta(minutes=59))
    assert not suppression.is_suppressed(candidate, now=start + timedelta(hours=1))


def test_library_service_excludes_paused_show_from_wanted_queue():
    active = Show("Active", "tvdb", "1", episodes=[Episode(1, 1, status=EpisodeStatus.WANTED)])
    paused = Show("Paused", "tvdb", "2", paused=True, episodes=[Episode(1, 1, status=EpisodeStatus.WANTED)])
    repo = InMemoryShowRepository()
    service = LibraryService(repo)
    service.upsert((paused, active))
    wanted = service.wanted_episodes()
    assert wanted == [(active, active.episodes[0])]
    assert [show.title for show in service.list_shows()] == ["Active", "Paused"]


def test_adapter_health_timestamp_is_timezone_aware():
    health = AdapterHealth.now("provider", HealthState.HEALTHY, latency_ms=12)
    assert health.state == HealthState.HEALTHY
    assert health.latency_ms == 12
    assert health.checked_at.tzinfo is not None
