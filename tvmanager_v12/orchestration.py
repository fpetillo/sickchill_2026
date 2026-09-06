from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Iterable, Sequence

from .adapters import DownloadRequest, DownloaderAdapter, HealthState, ProviderAdapter, SearchRequest
from .domain import DownloadCandidate, Episode, QualityProfile, Show
from .search import FailedDownloadSuppression, SearchDecision, choose_candidate


@dataclass(slots=True, frozen=True)
class ProviderSearchResult:
    provider: str
    candidates: tuple[DownloadCandidate, ...] = ()
    error: str | None = None
    skipped: bool = False


@dataclass(slots=True, frozen=True)
class SearchRun:
    started_at: datetime
    completed_at: datetime
    show_key: str
    episode_key: str
    query: str
    providers: tuple[ProviderSearchResult, ...]
    decision: SearchDecision
    submitted: bool = False
    submission_message: str = ""
    client_id: str | None = None


@dataclass(slots=True)
class SearchJournal:
    max_entries: int = 1000
    entries: list[SearchRun] = field(default_factory=list)

    def append(self, run: SearchRun) -> None:
        self.entries.append(run)
        overflow = len(self.entries) - self.max_entries
        if overflow > 0:
            del self.entries[:overflow]

    def recent(self, limit: int = 50) -> list[SearchRun]:
        return list(reversed(self.entries[-max(limit, 0) :]))


@dataclass(slots=True)
class SearchOrchestrator:
    providers: Sequence[ProviderAdapter]
    downloader: DownloaderAdapter | None = None
    suppression: FailedDownloadSuppression = field(default_factory=FailedDownloadSuppression)
    journal: SearchJournal = field(default_factory=SearchJournal)

    def run(
        self,
        show: Show,
        episode: Episode,
        profile: QualityProfile,
        *,
        query: str | None = None,
        required_words: Iterable[str] = (),
        rejected_words: Iterable[str] = (),
        manual: bool = False,
        auto_submit: bool = False,
        category: str | None = None,
    ) -> SearchRun:
        started = datetime.now(timezone.utc)
        search_query = query or f"{show.title} {episode.key}"
        request = SearchRequest(show=show, episode=episode, query=search_query, manual=manual)
        provider_results: list[ProviderSearchResult] = []
        candidates: list[DownloadCandidate] = []

        for provider in self.providers:
            health = provider.health()
            if health.state == HealthState.UNAVAILABLE:
                provider_results.append(ProviderSearchResult(provider.name, error=health.message, skipped=True))
                continue
            try:
                found = tuple(provider.search(request))
                candidates.extend(found)
                provider_results.append(ProviderSearchResult(provider.name, candidates=found))
            except Exception as exc:
                provider_results.append(ProviderSearchResult(provider.name, error=str(exc)))

        decision = choose_candidate(
            candidates,
            profile,
            required_words=required_words,
            rejected_words=rejected_words,
            suppression=self.suppression,
        )
        submitted = False
        submission_message = ""
        client_id = None

        if auto_submit and decision.chosen is not None:
            if self.downloader is None:
                submission_message = "No downloader configured."
            elif self.downloader.health().state == HealthState.UNAVAILABLE:
                submission_message = "Downloader is unavailable."
            else:
                result = self.downloader.submit(DownloadRequest(decision.chosen, category=category))
                submitted = result.accepted
                submission_message = result.message
                client_id = result.client_id

        run = SearchRun(
            started_at=started,
            completed_at=datetime.now(timezone.utc),
            show_key=f"{show.indexer}:{show.indexer_id}",
            episode_key=episode.key,
            query=search_query,
            providers=tuple(provider_results),
            decision=decision,
            submitted=submitted,
            submission_message=submission_message,
            client_id=client_id,
        )
        self.journal.append(run)
        return run
