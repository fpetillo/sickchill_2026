from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from typing import Protocol, Sequence, runtime_checkable

from .domain import DownloadCandidate, Episode, Show


class HealthState(StrEnum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    UNKNOWN = "unknown"


@dataclass(slots=True, frozen=True)
class AdapterHealth:
    name: str
    state: HealthState
    checked_at: datetime
    latency_ms: int | None = None
    message: str = ""

    @classmethod
    def now(cls, name: str, state: HealthState, *, latency_ms: int | None = None, message: str = "") -> "AdapterHealth":
        return cls(name=name, state=state, checked_at=datetime.now(timezone.utc), latency_ms=latency_ms, message=message)


@dataclass(slots=True, frozen=True)
class SearchRequest:
    show: Show
    episode: Episode
    query: str
    manual: bool = False


@dataclass(slots=True, frozen=True)
class DownloadRequest:
    candidate: DownloadCandidate
    destination: str | None = None
    category: str | None = None
    paused: bool = False


@dataclass(slots=True, frozen=True)
class DownloadSubmission:
    accepted: bool
    client_id: str | None = None
    message: str = ""


@runtime_checkable
class ProviderAdapter(Protocol):
    name: str

    def health(self) -> AdapterHealth:
        """Return a cheap, non-destructive provider health check."""

    def search(self, request: SearchRequest) -> Sequence[DownloadCandidate]:
        """Return normalized download candidates for one episode search."""


@runtime_checkable
class DownloaderAdapter(Protocol):
    name: str

    def health(self) -> AdapterHealth:
        """Return a cheap, non-destructive downloader health check."""

    def submit(self, request: DownloadRequest) -> DownloadSubmission:
        """Submit one candidate and return a normalized acknowledgement."""

    def delete(self, client_id: str, *, delete_data: bool = False) -> bool:
        """Remove a previously submitted item if the downloader supports it."""
