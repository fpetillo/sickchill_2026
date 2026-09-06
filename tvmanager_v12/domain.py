from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import StrEnum
from typing import Iterable


class EpisodeStatus(StrEnum):
    UNKNOWN = "unknown"
    WANTED = "wanted"
    SNATCHED = "snatched"
    DOWNLOADED = "downloaded"
    SKIPPED = "skipped"
    IGNORED = "ignored"
    ARCHIVED = "archived"
    FAILED = "failed"


@dataclass(slots=True, frozen=True)
class QualityProfile:
    name: str
    allowed: tuple[str, ...]
    preferred: tuple[str, ...] = ()
    cutoff: str | None = None

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("quality profile name cannot be empty")
        if not self.allowed:
            raise ValueError("quality profile must allow at least one quality")
        unknown_preferred = set(self.preferred) - set(self.allowed)
        if unknown_preferred:
            raise ValueError(f"preferred qualities must also be allowed: {sorted(unknown_preferred)}")
        if self.cutoff is not None and self.cutoff not in self.allowed:
            raise ValueError("cutoff quality must be part of allowed qualities")

    def rank(self, quality: str) -> int:
        """Return a deterministic desirability score for candidate comparison."""
        if quality not in self.allowed:
            return -1
        if quality in self.preferred:
            return 10_000 + (len(self.preferred) - self.preferred.index(quality))
        return len(self.allowed) - self.allowed.index(quality)


@dataclass(slots=True)
class Episode:
    season: int
    number: int
    title: str = ""
    airdate: date | None = None
    status: EpisodeStatus = EpisodeStatus.UNKNOWN
    quality: str | None = None
    location: str | None = None
    legacy_id: int | None = None

    def __post_init__(self) -> None:
        if self.season < 0 or self.number < 0:
            raise ValueError("season and episode numbers must be non-negative")

    @property
    def key(self) -> str:
        return f"S{self.season:02d}E{self.number:02d}"


@dataclass(slots=True)
class Show:
    title: str
    indexer: str
    indexer_id: str
    episodes: list[Episode] = field(default_factory=list)
    paused: bool = False
    anime: bool = False
    sports: bool = False
    air_by_date: bool = False
    scene: bool = False
    root_dir: str | None = None
    quality_profile: str | None = None
    legacy_id: int | None = None

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("show title cannot be empty")
        if not str(self.indexer_id).strip():
            raise ValueError("indexer_id cannot be empty")

    def episode(self, season: int, number: int) -> Episode | None:
        return next((ep for ep in self.episodes if ep.season == season and ep.number == number), None)

    def missing(self) -> list[Episode]:
        return [ep for ep in self.episodes if ep.status in {EpisodeStatus.UNKNOWN, EpisodeStatus.WANTED, EpisodeStatus.FAILED}]


@dataclass(slots=True, frozen=True)
class DownloadCandidate:
    title: str
    provider: str
    quality: str
    size_bytes: int | None = None
    seeders: int | None = None
    protocol: str = "unknown"
    score_adjustment: int = 0

    def score(self, profile: QualityProfile, required_words: Iterable[str] = (), rejected_words: Iterable[str] = ()) -> int:
        haystack = self.title.casefold()
        required = [word.casefold() for word in required_words if word.strip()]
        rejected = [word.casefold() for word in rejected_words if word.strip()]
        if any(word not in haystack for word in required):
            return -1
        if any(word in haystack for word in rejected):
            return -1
        quality_score = profile.rank(self.quality)
        if quality_score < 0:
            return -1
        seeder_score = min(max(self.seeders or 0, 0), 500)
        return quality_score * 1000 + seeder_score + self.score_adjustment
