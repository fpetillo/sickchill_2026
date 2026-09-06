from __future__ import annotations

import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Callable

from .adapters import AdapterHealth, HealthState, ProviderAdapter, SearchRequest
from .domain import DownloadCandidate


def infer_quality(title: str) -> str:
    """Conservative quality inference used until the full release parser lands."""
    text = title.casefold()
    for marker, quality in (
        ("2160p", "2160p"),
        ("1080p", "1080p"),
        ("720p", "720p"),
        ("480p", "480p"),
        ("web-dl", "WEB-DL"),
        ("webrip", "WEBRip"),
        ("bluray", "BluRay"),
        ("hdtv", "HDTV"),
    ):
        if marker in text:
            return quality
    return "unknown"


@dataclass(slots=True)
class _HTTPXMLProvider(ProviderAdapter):
    name: str
    base_url: str
    api_key: str = ""
    timeout: float = 15.0
    user_agent: str = "TVManager/12"
    opener: Callable[..., object] = field(default=urllib.request.urlopen, repr=False)

    def _request(self, params: dict[str, str]) -> tuple[bytes, int]:
        query = dict(params)
        if self.api_key:
            query["apikey"] = self.api_key
        url = self.base_url.rstrip("/") + "/api?" + urllib.parse.urlencode(query)
        request = urllib.request.Request(url, headers={"User-Agent": self.user_agent, "Accept": "application/rss+xml, application/xml, text/xml"})
        started = time.perf_counter()
        response = self.opener(request, timeout=self.timeout)
        try:
            payload = response.read()
        finally:
            close = getattr(response, "close", None)
            if callable(close):
                close()
        return payload, int((time.perf_counter() - started) * 1000)

    def health(self) -> AdapterHealth:
        try:
            payload, latency = self._request({"t": "caps"})
            if not payload:
                return AdapterHealth.now(self.name, HealthState.DEGRADED, latency_ms=latency, message="Provider returned an empty capabilities document.")
            ET.fromstring(payload)
            return AdapterHealth.now(self.name, HealthState.HEALTHY, latency_ms=latency, message="Capabilities endpoint responded successfully.")
        except Exception as exc:
            return AdapterHealth.now(self.name, HealthState.UNAVAILABLE, message=f"{type(exc).__name__}: {exc}")

    @staticmethod
    def _attr(item: ET.Element, name: str) -> str | None:
        for element in item.iter():
            if element.tag.endswith("attr") and element.attrib.get("name") == name:
                return element.attrib.get("value")
        return None

    @classmethod
    def _candidate(cls, item: ET.Element, *, provider: str, protocol: str) -> DownloadCandidate | None:
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        if not title or not link:
            return None
        size_raw = cls._attr(item, "size") or item.findtext("size")
        seeders_raw = cls._attr(item, "seeders")
        try:
            size = int(size_raw) if size_raw else None
        except (TypeError, ValueError):
            size = None
        try:
            seeders = int(seeders_raw) if seeders_raw else None
        except (TypeError, ValueError):
            seeders = None
        return DownloadCandidate(
            title=title,
            provider=provider,
            quality=infer_quality(title),
            size_bytes=size,
            seeders=seeders,
            protocol=protocol,
            score_adjustment=0,
        )


@dataclass(slots=True)
class NewznabProviderAdapter(_HTTPXMLProvider):
    """Concrete Newznab search adapter using the standard tvsearch API."""

    categories: tuple[str, ...] = ("5000",)

    def search(self, request: SearchRequest) -> tuple[DownloadCandidate, ...]:
        params = {"t": "tvsearch", "q": request.query, "o": "xml"}
        if self.categories:
            params["cat"] = ",".join(self.categories)
        payload, _ = self._request(params)
        root = ET.fromstring(payload)
        results: list[DownloadCandidate] = []
        for item in root.findall(".//item"):
            candidate = self._candidate(item, provider=self.name, protocol="nzb")
            if candidate:
                results.append(candidate)
        return tuple(results)


@dataclass(slots=True)
class TorznabProviderAdapter(_HTTPXMLProvider):
    """Concrete Torznab search adapter using standard RSS/newznab attributes."""

    categories: tuple[str, ...] = ("5000",)

    def search(self, request: SearchRequest) -> tuple[DownloadCandidate, ...]:
        params = {"t": "tvsearch", "q": request.query, "o": "xml"}
        if self.categories:
            params["cat"] = ",".join(self.categories)
        payload, _ = self._request(params)
        root = ET.fromstring(payload)
        results: list[DownloadCandidate] = []
        for item in root.findall(".//item"):
            candidate = self._candidate(item, provider=self.name, protocol="torrent")
            if candidate:
                results.append(candidate)
        return tuple(results)
