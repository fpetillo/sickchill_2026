from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import date, datetime
from http import HTTPStatus
from typing import Any, Callable, Iterable
from urllib.parse import parse_qs

from .domain import EpisodeStatus
from .runtime import SQLiteRuntimeStore
from .scheduler import SchedulerEngine, SQLiteJobStore
from .service import LibraryService


def _jsonable(value: Any) -> Any:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if hasattr(value, "value") and value.__class__.__module__ == "enum":
        return value.value
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if hasattr(value, "__dataclass_fields__"):
        return _jsonable(asdict(value))
    return value


@dataclass(slots=True)
class TVManagerAPI:
    library: LibraryService
    runtime: SQLiteRuntimeStore
    jobs: SQLiteJobStore
    scheduler: SchedulerEngine | None = None
    api_token: str | None = None

    def status(self) -> dict[str, Any]:
        shows = self.library.list_shows()
        wanted = self.library.wanted_episodes()
        return {
            "service": "tv-manager",
            "api_version": "v1",
            "development_version": "12.0.0-dev.4",
            "shows": len(shows),
            "wanted_episodes": len(wanted),
            "queue_items": len(self.runtime.load_queue()),
            "jobs": len(self.jobs.list()),
        }

    def dispatch(self, method: str, path: str, query: dict[str, list[str]], body: dict[str, Any] | None = None) -> tuple[int, dict[str, Any]]:
        if path == "/api/v1/status" and method == "GET":
            return HTTPStatus.OK, self.status()

        if path == "/api/v1/library" and method == "GET":
            include_paused = query.get("include_paused", ["true"])[0].casefold() != "false"
            return HTTPStatus.OK, {"items": _jsonable(self.library.list_shows(include_paused=include_paused))}

        if path == "/api/v1/wanted" and method == "GET":
            items = [
                {"show": _jsonable(show), "episode": _jsonable(episode)}
                for show, episode in self.library.wanted_episodes()
            ]
            return HTTPStatus.OK, {"items": items}

        if path == "/api/v1/queue" and method == "GET":
            return HTTPStatus.OK, {"items": _jsonable(self.runtime.load_queue())}

        if path == "/api/v1/history" and method == "GET":
            limit = int(query.get("limit", ["100"])[0])
            return HTTPStatus.OK, {"items": _jsonable(self.runtime.recent_history(limit))}

        if path == "/api/v1/search/history" and method == "GET":
            limit = int(query.get("limit", ["50"])[0])
            return HTTPStatus.OK, {"items": _jsonable(self.runtime.recent_searches(limit))}

        if path == "/api/v1/jobs" and method == "GET":
            return HTTPStatus.OK, {"items": _jsonable(self.jobs.list())}

        if path == "/api/v1/jobs/run-due" and method == "POST":
            if self.scheduler is None:
                return HTTPStatus.SERVICE_UNAVAILABLE, {"error": "scheduler-not-configured"}
            return HTTPStatus.OK, {"outcomes": self.scheduler.tick()}

        if path == "/api/v1/episode/status" and method == "POST":
            data = body or {}
            required = ("indexer", "indexer_id", "season", "number", "status")
            missing = [name for name in required if name not in data]
            if missing:
                return HTTPStatus.BAD_REQUEST, {"error": "missing-fields", "fields": missing}
            try:
                episode = self.library.set_episode_status(
                    str(data["indexer"]),
                    str(data["indexer_id"]),
                    int(data["season"]),
                    int(data["number"]),
                    EpisodeStatus(str(data["status"])),
                )
            except (LookupError, ValueError) as exc:
                return HTTPStatus.BAD_REQUEST, {"error": str(exc)}
            return HTTPStatus.OK, {"episode": _jsonable(episode)}

        return HTTPStatus.NOT_FOUND, {"error": "not-found", "path": path}

    def authorized(self, environ: dict[str, Any]) -> bool:
        if not self.api_token:
            return True
        header = str(environ.get("HTTP_AUTHORIZATION", ""))
        return header == f"Bearer {self.api_token}"


def create_wsgi_app(api: TVManagerAPI) -> Callable[..., Iterable[bytes]]:
    """Return a dependency-free WSGI app for the v1 API.

    This makes the API usable immediately behind an existing WSGI server while
    keeping the domain/service layer independent of a specific web framework.
    """

    def app(environ: dict[str, Any], start_response: Callable[..., Any]) -> Iterable[bytes]:
        if not api.authorized(environ):
            payload = json.dumps({"error": "unauthorized"}).encode("utf-8")
            start_response("401 Unauthorized", [("Content-Type", "application/json"), ("Content-Length", str(len(payload)))])
            return [payload]

        method = str(environ.get("REQUEST_METHOD", "GET")).upper()
        path = str(environ.get("PATH_INFO", "/"))
        query = parse_qs(str(environ.get("QUERY_STRING", "")))
        body: dict[str, Any] | None = None
        if method in {"POST", "PUT", "PATCH"}:
            try:
                length = int(environ.get("CONTENT_LENGTH") or 0)
                raw = environ["wsgi.input"].read(length) if length else b""
                body = json.loads(raw.decode("utf-8")) if raw else {}
                if not isinstance(body, dict):
                    raise ValueError("JSON body must be an object")
            except Exception as exc:
                payload = json.dumps({"error": "invalid-json", "message": str(exc)}).encode("utf-8")
                start_response("400 Bad Request", [("Content-Type", "application/json"), ("Content-Length", str(len(payload)))])
                return [payload]

        try:
            status, data = api.dispatch(method, path, query, body)
        except (TypeError, ValueError) as exc:
            status, data = HTTPStatus.BAD_REQUEST, {"error": "invalid-request", "message": str(exc)}
        payload = json.dumps(_jsonable(data), sort_keys=True).encode("utf-8")
        start_response(
            f"{int(status)} {HTTPStatus(int(status)).phrase}",
            [("Content-Type", "application/json; charset=utf-8"), ("Content-Length", str(len(payload)))],
        )
        return [payload]

    return app
