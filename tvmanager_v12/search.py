from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import StrEnum
from hashlib import sha256
from typing import Iterable

from .domain import DownloadCandidate, QualityProfile


class DecisionState(StrEnum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    SUPPRESSED = "suppressed"


@dataclass(slots=True, frozen=True)
class SearchReason:
    code: str
    message: str
    weight: int = 0


@dataclass(slots=True, frozen=True)
class CandidateDecision:
    candidate: DownloadCandidate
    state: DecisionState
    score: int
    reasons: tuple[SearchReason, ...] = ()

    @property
    def accepted(self) -> bool:
        return self.state == DecisionState.ACCEPTED


@dataclass(slots=True, frozen=True)
class SearchDecision:
    chosen: DownloadCandidate | None
    candidates: tuple[CandidateDecision, ...]

    @property
    def accepted_count(self) -> int:
        return sum(item.accepted for item in self.candidates)


@dataclass(slots=True)
class FailedDownloadSuppression:
    """Time-bounded fingerprint suppression for repeatedly failed releases."""

    ttl: timedelta = timedelta(days=14)
    _items: dict[str, datetime] = field(default_factory=dict)

    @staticmethod
    def fingerprint(candidate: DownloadCandidate) -> str:
        normalized = "|".join((candidate.provider.strip().casefold(), candidate.title.strip().casefold(), candidate.protocol.strip().casefold()))
        return sha256(normalized.encode("utf-8")).hexdigest()

    def suppress(self, candidate: DownloadCandidate, *, now: datetime | None = None) -> str:
        stamp = now or datetime.now(timezone.utc)
        fingerprint = self.fingerprint(candidate)
        self._items[fingerprint] = stamp + self.ttl
        return fingerprint

    def is_suppressed(self, candidate: DownloadCandidate, *, now: datetime | None = None) -> bool:
        stamp = now or datetime.now(timezone.utc)
        self.prune(now=stamp)
        expiry = self._items.get(self.fingerprint(candidate))
        return expiry is not None and expiry > stamp

    def release(self, candidate: DownloadCandidate) -> None:
        self._items.pop(self.fingerprint(candidate), None)

    def prune(self, *, now: datetime | None = None) -> int:
        stamp = now or datetime.now(timezone.utc)
        expired = [key for key, expiry in self._items.items() if expiry <= stamp]
        for key in expired:
            del self._items[key]
        return len(expired)


def evaluate_candidate(candidate: DownloadCandidate, profile: QualityProfile, *, required_words: Iterable[str] = (), rejected_words: Iterable[str] = (), suppression: FailedDownloadSuppression | None = None) -> CandidateDecision:
    reasons: list[SearchReason] = []
    if suppression and suppression.is_suppressed(candidate):
        return CandidateDecision(candidate, DecisionState.SUPPRESSED, -1, (SearchReason("failed-release", "Previously failed release is temporarily suppressed."),))

    haystack = candidate.title.casefold()
    required = tuple(word.strip().casefold() for word in required_words if word.strip())
    rejected = tuple(word.strip().casefold() for word in rejected_words if word.strip())
    missing = [word for word in required if word not in haystack]
    if missing:
        return CandidateDecision(candidate, DecisionState.REJECTED, -1, (SearchReason("required-word-missing", f"Missing required words: {', '.join(missing)}"),))
    blocked = [word for word in rejected if word in haystack]
    if blocked:
        return CandidateDecision(candidate, DecisionState.REJECTED, -1, (SearchReason("rejected-word", f"Contains rejected words: {', '.join(blocked)}"),))

    quality_rank = profile.rank(candidate.quality)
    if quality_rank < 0:
        return CandidateDecision(candidate, DecisionState.REJECTED, -1, (SearchReason("quality-not-allowed", f"Quality {candidate.quality!r} is not allowed by profile {profile.name!r}."),))

    if candidate.quality in profile.preferred:
        reasons.append(SearchReason("preferred-quality", f"{candidate.quality} is a preferred quality.", quality_rank * 1000))
    else:
        reasons.append(SearchReason("allowed-quality", f"{candidate.quality} is allowed.", quality_rank * 1000))
    seeder_score = min(max(candidate.seeders or 0, 0), 500)
    if seeder_score:
        reasons.append(SearchReason("seeders", f"{candidate.seeders} seeders contributed to ranking.", seeder_score))
    if candidate.score_adjustment:
        reasons.append(SearchReason("score-adjustment", "Provider or rule score adjustment applied.", candidate.score_adjustment))
    score = quality_rank * 1000 + seeder_score + candidate.score_adjustment
    return CandidateDecision(candidate, DecisionState.ACCEPTED, score, tuple(reasons))


def choose_candidate(candidates: Iterable[DownloadCandidate], profile: QualityProfile, *, required_words: Iterable[str] = (), rejected_words: Iterable[str] = (), suppression: FailedDownloadSuppression | None = None) -> SearchDecision:
    decisions = tuple(evaluate_candidate(candidate, profile, required_words=required_words, rejected_words=rejected_words, suppression=suppression) for candidate in candidates)
    accepted = [item for item in decisions if item.accepted]
    accepted.sort(key=lambda item: (item.score, item.candidate.seeders or 0, item.candidate.provider.casefold(), item.candidate.title.casefold()), reverse=True)
    return SearchDecision(chosen=accepted[0].candidate if accepted else None, candidates=decisions)
