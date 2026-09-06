from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Callable, Sequence

from .adapters import (
    AdapterHealth,
    DownloadRequest,
    DownloadSubmission,
    HealthState,
    SearchRequest,
)
from .domain import DownloadCandidate


@dataclass(slots=True)
class CallableProviderAdapter:
    """Wrap a legacy/provider callable behind the v12 ProviderAdapter contract."""

    name: str
    search_fn: Callable[[SearchRequest], Sequence[DownloadCandidate]]
    health_fn: Callable[[], tuple[bool, str]] | None = None

    def health(self) -> AdapterHealth:
        started = perf_counter()
        try:
            ok, message = self.health_fn() if self.health_fn else (True, "adapter callable available")
            state = HealthState.HEALTHY if ok else HealthState.DEGRADED
        except Exception as exc:  # adapter boundary intentionally contains provider failures
            state, message = HealthState.UNAVAILABLE, str(exc)
        return AdapterHealth.now(self.name, state, latency_ms=int((perf_counter() - started) * 1000), message=message)

    def search(self, request: SearchRequest) -> Sequence[DownloadCandidate]:
        return tuple(self.search_fn(request))


@dataclass(slots=True)
class CallableDownloaderAdapter:
    """Wrap legacy download-client functions while returning normalized v12 results."""

    name: str
    submit_fn: Callable[[DownloadRequest], DownloadSubmission]
    delete_fn: Callable[[str, bool], bool] | None = None
    health_fn: Callable[[], tuple[bool, str]] | None = None

    def health(self) -> AdapterHealth:
        started = perf_counter()
        try:
            ok, message = self.health_fn() if self.health_fn else (True, "adapter callable available")
            state = HealthState.HEALTHY if ok else HealthState.DEGRADED
        except Exception as exc:
            state, message = HealthState.UNAVAILABLE, str(exc)
        return AdapterHealth.now(self.name, state, latency_ms=int((perf_counter() - started) * 1000), message=message)

    def submit(self, request: DownloadRequest) -> DownloadSubmission:
        try:
            return self.submit_fn(request)
        except Exception as exc:
            return DownloadSubmission(False, message=f"{self.name} submission failed: {exc}")

    def delete(self, client_id: str, *, delete_data: bool = False) -> bool:
        if self.delete_fn is None:
            return False
        try:
            return bool(self.delete_fn(client_id, delete_data))
        except Exception:
            return False
