from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from typing import Callable

from .adapters import AdapterHealth, DownloadRequest, DownloadSubmission, HealthState


@dataclass(slots=True)
class SABnzbdAdapter:
    name: str
    base_url: str
    api_key: str
    timeout: float = 15.0
    opener: Callable[..., object] = field(default=urllib.request.urlopen, repr=False)

    def _call(self, params: dict[str, str]) -> tuple[dict[str, object], int]:
        query = {"output": "json", "apikey": self.api_key, **params}
        url = self.base_url.rstrip("/") + "/api?" + urllib.parse.urlencode(query)
        request = urllib.request.Request(url, headers={"User-Agent": "TVManager/12"})
        started = time.perf_counter()
        response = self.opener(request, timeout=self.timeout)
        try:
            payload = json.loads(response.read().decode("utf-8"))
        finally:
            close = getattr(response, "close", None)
            if callable(close):
                close()
        return payload, int((time.perf_counter() - started) * 1000)

    def health(self) -> AdapterHealth:
        try:
            payload, latency = self._call({"mode": "version"})
            version = str(payload.get("version", "")).strip()
            if not version:
                return AdapterHealth.now(self.name, HealthState.DEGRADED, latency_ms=latency, message="SABnzbd responded without a version.")
            return AdapterHealth.now(self.name, HealthState.HEALTHY, latency_ms=latency, message=f"SABnzbd {version}")
        except Exception as exc:
            return AdapterHealth.now(self.name, HealthState.UNAVAILABLE, message=f"{type(exc).__name__}: {exc}")

    def submit(self, request: DownloadRequest) -> DownloadSubmission:
        url = request.candidate.download_url
        if not url:
            return DownloadSubmission(False, message="Candidate does not contain a download URL.")
        params = {"mode": "addurl", "name": url}
        if request.category:
            params["cat"] = request.category
        if request.paused:
            params["priority"] = "-2"
        try:
            payload, _ = self._call(params)
        except Exception as exc:
            return DownloadSubmission(False, message=f"{type(exc).__name__}: {exc}")
        status = bool(payload.get("status"))
        ids = payload.get("nzo_ids") or []
        client_id = str(ids[0]) if isinstance(ids, list) and ids else None
        return DownloadSubmission(status, client_id=client_id, message="Submitted to SABnzbd." if status else str(payload))

    def delete(self, client_id: str, *, delete_data: bool = False) -> bool:
        try:
            payload, _ = self._call({"mode": "queue", "name": "delete", "value": client_id, "del_files": "1" if delete_data else "0"})
        except Exception:
            return False
        return bool(payload.get("status", True))


@dataclass(slots=True)
class QBittorrentAdapter:
    name: str
    base_url: str
    username: str = ""
    password: str = ""
    timeout: float = 15.0
    opener: Callable[..., object] = field(default=urllib.request.urlopen, repr=False)
    _cookie: str = field(default="", init=False, repr=False)

    def _request(self, path: str, *, data: dict[str, str] | None = None) -> tuple[bytes, int, object]:
        body = urllib.parse.urlencode(data or {}).encode("utf-8") if data is not None else None
        headers = {"User-Agent": "TVManager/12", "Referer": self.base_url.rstrip("/") + "/"}
        if self._cookie:
            headers["Cookie"] = self._cookie
        request = urllib.request.Request(self.base_url.rstrip("/") + path, data=body, headers=headers)
        started = time.perf_counter()
        response = self.opener(request, timeout=self.timeout)
        payload = response.read()
        latency = int((time.perf_counter() - started) * 1000)
        return payload, latency, response

    def _login(self) -> None:
        if not self.username:
            return
        payload, _, response = self._request("/api/v2/auth/login", data={"username": self.username, "password": self.password})
        text = payload.decode("utf-8", errors="replace").strip()
        if text != "Ok.":
            raise RuntimeError(f"qBittorrent login failed: {text or 'empty response'}")
        cookie = ""
        headers = getattr(response, "headers", None)
        if headers is not None:
            cookie = headers.get("Set-Cookie", "")
        self._cookie = cookie.split(";", 1)[0] if cookie else ""
        close = getattr(response, "close", None)
        if callable(close):
            close()

    def health(self) -> AdapterHealth:
        try:
            self._login()
            payload, latency, response = self._request("/api/v2/app/version")
            version = payload.decode("utf-8", errors="replace").strip()
            close = getattr(response, "close", None)
            if callable(close):
                close()
            if not version:
                return AdapterHealth.now(self.name, HealthState.DEGRADED, latency_ms=latency, message="qBittorrent responded without a version.")
            return AdapterHealth.now(self.name, HealthState.HEALTHY, latency_ms=latency, message=f"qBittorrent {version}")
        except Exception as exc:
            return AdapterHealth.now(self.name, HealthState.UNAVAILABLE, message=f"{type(exc).__name__}: {exc}")

    def submit(self, request: DownloadRequest) -> DownloadSubmission:
        url = request.candidate.download_url
        if not url:
            return DownloadSubmission(False, message="Candidate does not contain a torrent or magnet URL.")
        try:
            self._login()
            form = {"urls": url, "paused": "true" if request.paused else "false"}
            if request.category:
                form["category"] = request.category
            payload, _, response = self._request("/api/v2/torrents/add", data=form)
            text = payload.decode("utf-8", errors="replace").strip()
            close = getattr(response, "close", None)
            if callable(close):
                close()
            accepted = text == "Ok."
            return DownloadSubmission(accepted, client_id=request.candidate.guid, message="Submitted to qBittorrent." if accepted else text)
        except Exception as exc:
            return DownloadSubmission(False, message=f"{type(exc).__name__}: {exc}")

    def delete(self, client_id: str, *, delete_data: bool = False) -> bool:
        try:
            self._login()
            payload, _, response = self._request(
                "/api/v2/torrents/delete",
                data={"hashes": client_id, "deleteFiles": "true" if delete_data else "false"},
            )
            text = payload.decode("utf-8", errors="replace").strip()
            close = getattr(response, "close", None)
            if callable(close):
                close()
            return text in {"", "Ok."}
        except Exception:
            return False
