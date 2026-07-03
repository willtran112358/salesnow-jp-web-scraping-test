"""Discover company profile pages by following links from the seed URL."""

from __future__ import annotations

import re
from typing import Iterable
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from .config import PROFILE_LINK_KEYWORDS, PROFILE_PATH_CANDIDATES
from .fetcher import Fetcher, normalize_url, same_domain


def _score_link(text: str, href: str) -> int:
    combined = f"{text} {href}".lower()
    score = 0
    for keyword in PROFILE_LINK_KEYWORDS:
        if keyword.lower() in combined:
            score += 10
    if re.search(r"(outline|profile|company|corporate|about)", href, re.I):
        score += 3
    if re.search(r"(recruit|ir|news|recipe|product|shop|contact|english)", href, re.I):
        score -= 5
    return score


def discover_profile_urls(
    fetcher: Fetcher,
    seed_url: str,
    max_pages: int = 6,
    profile_urls: list[str] | None = None,
) -> list[str]:
    seen: set[str] = set()
    candidates: list[tuple[int, str]] = []

    def add(url: str, score: int) -> None:
        if url in seen:
            return
        seen.add(url)
        candidates.append((score, url))

    for url in profile_urls or []:
        add(url, 100)

    homepage_text, final_url = fetcher.get_text(seed_url)
    base = final_url or seed_url
    if homepage_text:
        soup = BeautifulSoup(homepage_text, "lxml")
        for anchor in soup.find_all("a", href=True):
            href = anchor["href"]
            if not same_domain(base, href):
                continue
            text = anchor.get_text(" ", strip=True)
            url = normalize_url(base, href)
            score = _score_link(text, href)
            if score > 0:
                add(url, score)

    parsed = urlparse(base)
    origin = f"{parsed.scheme}://{parsed.netloc}"
    for path in PROFILE_PATH_CANDIDATES:
        add(origin + path, 5)

    # Umios root redirects; ensure JP corporate path.
    if "umios.com" in parsed.netloc:
        add("https://www.umios.com/jp/corporate/profile/", 20)

    ranked = sorted(candidates, key=lambda item: item[0], reverse=True)
    return [url for _, url in ranked[:max_pages]]


def collect_page_texts(fetcher: Fetcher, urls: Iterable[str]) -> str:
    chunks: list[str] = []
    for url in urls:
        text, _ = fetcher.get_text(url)
        if not text:
            continue
        soup = BeautifulSoup(text, "lxml")
        for tag in soup(["script", "style", "noscript", "svg"]):
            tag.decompose()
        body = soup.get_text("\n", strip=True)
        chunks.append(f"--- URL: {url} ---\n{body}")
    return "\n\n".join(chunks)
