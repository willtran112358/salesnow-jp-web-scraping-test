"""Optional Playwright rendering for JavaScript-heavy pages."""

from __future__ import annotations

from typing import Optional

from .config import DEFAULT_HEADERS


def fetch_rendered_html(url: str, wait_ms: int = 3000) -> Optional[str]:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return None

    launch_kwargs: dict = {"headless": True}
    for channel in ("msedge", "chrome"):
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(channel=channel, **launch_kwargs)
                context = browser.new_context(user_agent=DEFAULT_HEADERS["User-Agent"], locale="ja-JP")
                page = context.new_page()
                page.goto(url, wait_until="networkidle", timeout=90000)
                page.wait_for_timeout(wait_ms)
                html = page.content()
                browser.close()
                return html
        except Exception:
            continue

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(**launch_kwargs)
            context = browser.new_context(user_agent=DEFAULT_HEADERS["User-Agent"], locale="ja-JP")
            page = context.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=90000)
            page.wait_for_timeout(wait_ms)
            html = page.content()
            browser.close()
            return html
    except Exception:
        return None
