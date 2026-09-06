from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum


class QueueState(StrEnum):
    QUEUED = "queued"
    DOWNLOADING = "downloading"
    COMPLETED = "completed"
    FAILED = "failed"
    REMOVED = "removed"
    UNKNOWN = "unknown"


@dataclass(slots=True)
class QueueItem:
    client_id: str
    title: str
    downloader: str
    state: QueueState = QueueState.QUEUED
    progress: float = 0.0
    added_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    message: str = ""

    def update(self, state: QueueState, *, progress: float | None = None, message: str | None = None) -> None:
        self.state = state
        if progress is not None:
            self.progress = min(max(float(progress), 0.0), 100.0)
        if message is not None:
            self.message = message
        self.updated_at = datetime.now(timezone.utc)


@dataclass(slots=True, frozen=True)
class HistoryEvent:
    kind: str
    timestamp: datetime
    message: str
    client_id: str | None = None
    show_key: str | None = None
    episode_key: str | None = None


@dataclass(slots=True)
class ActivityStore:
    """In-process queue/history model used until persistent job storage lands."""

    queue: dict[str, QueueItem] = field(default_factory=dict)
    history: list[HistoryEvent] = field(default_factory=list)
    max_history: int = 5000

    def add(self, item: QueueItem) -> None:
        self.queue[item.client_id] = item
        self.record("queued", f"Queued {item.title}", client_id=item.client_id)

    def reconcile(self, client_id: str, state: QueueState, *, progress: float | None = None, message: str = "") -> QueueItem:
        item = self.queue.get(client_id)
        if item is None:
            item = QueueItem(client_id=client_id, title=client_id, downloader="unknown", state=QueueState.UNKNOWN)
            self.queue[client_id] = item
        item.update(state, progress=progress, message=message)
        self.record("queue-state", f"{client_id} -> {state.value}: {message}".rstrip(), client_id=client_id)
        return item

    def remove(self, client_id: str, *, message: str = "") -> bool:
        item = self.queue.pop(client_id, None)
        if item is None:
            return False
        self.record("removed", message or f"Removed {item.title}", client_id=client_id)
        return True

    def record(
        self,
        kind: str,
        message: str,
        *,
        client_id: str | None = None,
        show_key: str | None = None,
        episode_key: str | None = None,
    ) -> None:
        self.history.append(
            HistoryEvent(
                kind=kind,
                timestamp=datetime.now(timezone.utc),
                message=message,
                client_id=client_id,
                show_key=show_key,
                episode_key=episode_key,
            )
        )
        overflow = len(self.history) - self.max_history
        if overflow > 0:
            del self.history[:overflow]

    def active(self) -> list[QueueItem]:
        return sorted(self.queue.values(), key=lambda item: item.added_at)

    def recent_history(self, limit: int = 100) -> list[HistoryEvent]:
        return list(reversed(self.history[-max(limit, 0) :]))
