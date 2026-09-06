"""TV Manager v12 modernization foundation.

This package is intentionally additive to the legacy SickChill codebase. It
provides stable domain, migration, adapter, search-decision, and service
primitives that can be exercised without changing legacy runtime behavior
while the new service/API/UI are introduced.
"""

from .adapters import AdapterHealth, DownloaderAdapter, DownloadRequest, DownloadSubmission, HealthState, ProviderAdapter, SearchRequest
from .domain import DownloadCandidate, Episode, EpisodeStatus, QualityProfile, Show
from .search import CandidateDecision, DecisionState, FailedDownloadSuppression, SearchDecision, SearchReason, choose_candidate, evaluate_candidate
from .service import InMemoryShowRepository, LibraryService, ShowRepository

__all__ = [
    "AdapterHealth",
    "CandidateDecision",
    "DecisionState",
    "DownloaderAdapter",
    "DownloadCandidate",
    "DownloadRequest",
    "DownloadSubmission",
    "Episode",
    "EpisodeStatus",
    "FailedDownloadSuppression",
    "HealthState",
    "InMemoryShowRepository",
    "LibraryService",
    "ProviderAdapter",
    "QualityProfile",
    "SearchDecision",
    "SearchReason",
    "SearchRequest",
    "Show",
    "ShowRepository",
    "choose_candidate",
    "evaluate_candidate",
]

__version__ = "12.0.0-dev.2"
