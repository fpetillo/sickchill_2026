"""TV Manager v12 modernization foundation.

This package is intentionally additive to the legacy SickChill codebase. It
provides stable domain, migration, adapter, search, persistence, orchestration,
queue/history, and service primitives while the new runtime is introduced.
"""

from .adapters import AdapterHealth, DownloaderAdapter, DownloadRequest, DownloadSubmission, HealthState, ProviderAdapter, SearchRequest
from .compat import CallableDownloaderAdapter, CallableProviderAdapter
from .domain import DownloadCandidate, Episode, EpisodeStatus, QualityProfile, Show
from .orchestration import ProviderSearchResult, SearchJournal, SearchOrchestrator, SearchRun
from .persistence import SQLiteShowRepository
from .queue import ActivityStore, HistoryEvent, QueueItem, QueueState
from .search import CandidateDecision, DecisionState, FailedDownloadSuppression, SearchDecision, SearchReason, choose_candidate, evaluate_candidate
from .service import InMemoryShowRepository, LibraryService, ShowRepository

__all__ = [
    "ActivityStore",
    "AdapterHealth",
    "CallableDownloaderAdapter",
    "CallableProviderAdapter",
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
    "HistoryEvent",
    "InMemoryShowRepository",
    "LibraryService",
    "ProviderAdapter",
    "ProviderSearchResult",
    "QualityProfile",
    "QueueItem",
    "QueueState",
    "SQLiteShowRepository",
    "SearchDecision",
    "SearchJournal",
    "SearchOrchestrator",
    "SearchReason",
    "SearchRequest",
    "SearchRun",
    "Show",
    "ShowRepository",
    "choose_candidate",
    "evaluate_candidate",
]

__version__ = "12.0.0-dev.3"
