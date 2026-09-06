from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Protocol, runtime_checkable

from .domain import Episode, EpisodeStatus, Show


@runtime_checkable
class ShowRepository(Protocol):
    def all(self) -> list[Show]: ...
    def get(self, indexer: str, indexer_id: str) -> Show | None: ...
    def save(self, show: Show) -> None: ...
    def delete(self, indexer: str, indexer_id: str) -> bool: ...


@dataclass(slots=True)
class InMemoryShowRepository:
    """Reference repository used by tests and the first API/service layer."""

    _shows: dict[tuple[str, str], Show] = field(default_factory=dict)

    @staticmethod
    def _key(indexer: str, indexer_id: str) -> tuple[str, str]:
        return indexer.casefold().strip(), str(indexer_id).strip()

    def all(self) -> list[Show]:
        return sorted(self._shows.values(), key=lambda show: show.title.casefold())

    def get(self, indexer: str, indexer_id: str) -> Show | None:
        return self._shows.get(self._key(indexer, indexer_id))

    def save(self, show: Show) -> None:
        self._shows[self._key(show.indexer, show.indexer_id)] = show

    def delete(self, indexer: str, indexer_id: str) -> bool:
        return self._shows.pop(self._key(indexer, indexer_id), None) is not None


@dataclass(slots=True)
class LibraryService:
    repository: ShowRepository

    def list_shows(self, *, include_paused: bool = True) -> list[Show]:
        shows = self.repository.all()
        return shows if include_paused else [show for show in shows if not show.paused]

    def wanted_episodes(self) -> list[tuple[Show, Episode]]:
        wanted: list[tuple[Show, Episode]] = []
        for show in self.repository.all():
            if show.paused:
                continue
            wanted.extend((show, episode) for episode in show.episodes if episode.status in {EpisodeStatus.UNKNOWN, EpisodeStatus.WANTED, EpisodeStatus.FAILED})
        return wanted

    def set_episode_status(self, indexer: str, indexer_id: str, season: int, number: int, status: EpisodeStatus) -> Episode:
        show = self.repository.get(indexer, indexer_id)
        if show is None:
            raise LookupError(f"show not found: {indexer}:{indexer_id}")
        episode = show.episode(season, number)
        if episode is None:
            raise LookupError(f"episode not found: S{season:02d}E{number:02d}")
        episode.status = status
        self.repository.save(show)
        return episode

    def upsert(self, shows: Iterable[Show]) -> int:
        count = 0
        for show in shows:
            self.repository.save(show)
            count += 1
        return count
