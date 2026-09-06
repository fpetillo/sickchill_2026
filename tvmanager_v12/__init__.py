"""TV Manager v12 modernization foundation.

This package is intentionally additive to the legacy SickChill codebase.  It
provides stable domain and migration primitives that can be exercised without
changing legacy runtime behavior while the new service/API/UI are introduced.
"""

from .domain import DownloadCandidate, Episode, EpisodeStatus, QualityProfile, Show

__all__ = [
    "DownloadCandidate",
    "Episode",
    "EpisodeStatus",
    "QualityProfile",
    "Show",
]

__version__ = "12.0.0-dev.1"
