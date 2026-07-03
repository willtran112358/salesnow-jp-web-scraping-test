"""HTTP fetch utilities."""

from __future__ import annotations

import time
from typing import Optional
from urllib.parse import urljoin, urlparse

import httpx

try:
    import certifi
except ImportError:  # pragma: no cover
    certifi = None

from .config import DEFAULT_HEADERS


def _build_client() -> httpx.Client:
    verify: bool | str = True
    if certifi is not None:
        verify = certifi.where()
    return httpx.Client(
        headers=DEFAULT_HEADERS,
        timeout=30.0,
        follow_redirects=True,
        verify=verify,
    )


class Fetcher:
    def __init__(self, timeout: float = 30.0, delay: float = 1.0) -> None:
        self.timeout = timeout
        self.delay = delay
        self._client = _build_client()
        self._insecure_client: Optional[httpx.Client] = None

    def close(self) -> None:
        self._client.close()
        if self._insecure_client is not None:
            self._insecure_client.close()

    def __enter__(self) -> "Fetcher":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def _get_client(self, url: str) -> httpx.Client:
        return self._client

    def get(self, url: str) -> Optional[httpx.Response]:
        time.sleep(self.delay)
        for client in (self._client, self._insecure_client):
            if client is None:
                continue
            try:
                response = client.get(url, timeout=self.timeout)
                if response.status_code >= 400:
                    return None
                return response
            except httpx.HTTPError:
                continue

        if self._insecure_client is None:
            self._insecure_client = httpx.Client(
                headers=DEFAULT_HEADERS,
                timeout=self.timeout,
                follow_redirects=True,
                verify=False,
            )
        try:
            response = self._insecure_client.get(url)
            if response.status_code >= 400:
                return None
            return response
        except httpx.HTTPError:
            return None

    def get_text(self, url: str) -> tuple[Optional[str], Optional[str]]:
        response = self.get(url)
        if response is None:
            return None, None
        encoding = response.encoding or "utf-8"
        try:
            text = response.text
        except Exception:
            text = response.content.decode(encoding, errors="replace")
        return text, str(response.url)


def same_domain(base_url: str, candidate: str) -> bool:
    base = urlparse(base_url)
    parsed = urlparse(urljoin(base_url, candidate))
    return parsed.netloc == "" or parsed.netloc == base.netloc


def normalize_url(base_url: str, href: str) -> str:
    return urljoin(base_url, href.split("#")[0].strip())
