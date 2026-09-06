"""TV Manager v12 modernization foundation.

This package is intentionally additive to the legacy SickChill codebase. It
provides stable domain, migration, adapter, search, persistence, orchestration,
queue/history, scheduler, API, and service primitives while the new runtime is
introduced and validated.
"""

from .adapters import AdapterHealth, DownloaderAdapter, DownloadRequest, DownloadSubmission, HealthState, ProviderAdapter, SearchRequest
from .api import TVManagerAPI, create_wsgi_app
from .compat import CallableDownloaderAdapter, CallableProviderAdapter
from .domain import DownloadCandidate, Episode, EpisodeStatus, QualityProfile, Show
from .downloaders import QBittorrentAdapter, SABnzbdAdapter
from .orchestration import ProviderSearchResult, SearchJournal, SearchOrchestrator, SearchRun
from .persistence import SQLiteShowRepository
from .providers import NewznabProviderAdapter, TorznabProviderAdapter, infer_quality
from .queue import ActivityStore, HistoryEvent, QueueItem, QueueState
from .runtime import PersistentActivityStore, SQLiteRuntimeStore, SearchHistoryRecord
from .scheduler import JobSnapshot, SchedulerEngine, SQLiteJobStore
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
    "JobSnapshot",
    "LibraryService",
    "NewznabProviderAdapter",
    "PersistentActivityStore",
    "ProviderAdapter",
    "ProviderSearchResult",
    "QBittorrentAdapter",
    "QualityProfile",
    "QueueItem",
    "QueueState",
    "SABnzbdAdapter",
    "SQLiteJobStore",
    "SQLiteRuntimeStore",
    "SQLiteShowRepository",
    "SchedulerEngine",
    "SearchDecision",
    "SearchHistoryRecord",
    "SearchJournal",
    "SearchOrchestrator",
    "SearchReason",
    "SearchRequest",
    "SearchRun",
    "Show",
    "ShowRepository",
    "TVManagerAPI",
    "TorznabProviderAdapter",
    "choose_candidate",
    "create_wsgi_app",
    "evaluate_candidate",
    "infer_quality",
]

__version__ = "12.0.0-dev.4"
