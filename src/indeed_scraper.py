"""Task B: Indeed Vietnam bot-protected scraping attempt."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

from .config import DEFAULT_HEADERS, PROMPTS, RESULT


INDEED_URL = "https://vn.indeed.com/jobs?q=remote"


def _save_prompt(name: str, content: str) -> None:
    PROMPTS.mkdir(parents=True, exist_ok=True)
    (PROMPTS / name).write_text(content, encoding="utf-8")


def scrape_indeed_httpx() -> dict[str, Any]:
    result: dict[str, Any] = {
        "method": "httpx",
        "success": False,
        "status_code": None,
        "blocked_signals": [],
        "job_count": 0,
        "sample_jobs": [],
        "html_length": 0,
        "error": None,
    }
    try:
        with httpx.Client(
            headers=DEFAULT_HEADERS,
            follow_redirects=True,
            verify=False,
            timeout=30,
        ) as client:
            response = client.get(INDEED_URL)
            result["status_code"] = response.status_code
            html = response.text
            result["html_length"] = len(html)

            lower = html.lower()
            for signal in ("captcha", "challenge", "cf-browser-verification", "access denied", "verify you are human"):
                if signal in lower:
                    result["blocked_signals"].append(signal)

            if response.status_code in (403, 429, 503):
                result["blocked_signals"].append(f"http_{response.status_code}")

            titles = re.findall(r'jobTitle["\']?\s*[:=]\s*["\']([^"\']+)["\']', html)
            if not titles:
                titles = re.findall(r'<h2[^>]*class="[^"]*jobTitle[^"]*"[^>]*>.*?<span[^>]*>([^<]+)</span>', html, re.I | re.S)
            if not titles:
                titles = re.findall(r"<a[^>]*data-jk=[^>]*><span>([^<]+)</span>", html)

            result["job_count"] = len(titles)
            result["sample_jobs"] = titles[:10]
            result["success"] = len(titles) > 0 and not result["blocked_signals"]
    except Exception as exc:
        result["error"] = str(exc)
    return result


def scrape_indeed_playwright() -> dict[str, Any]:
    result: dict[str, Any] = {
        "method": "playwright",
        "success": False,
        "blocked_signals": [],
        "job_count": 0,
        "sample_jobs": [],
        "page_title": None,
        "error": None,
    }
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent=DEFAULT_HEADERS["User-Agent"],
                locale="vi-VN",
            )
            page = context.new_page()
            page.goto(INDEED_URL, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(3000)
            result["page_title"] = page.title()
            content = page.content()
            lower = content.lower()
            for signal in ("captcha", "challenge", "verify you are human", "just a moment"):
                if signal in lower:
                    result["blocked_signals"].append(signal)

            jobs = page.locator("h2.jobTitle span, a.jcs-JobTitle span")
            count = jobs.count()
            titles = [jobs.nth(i).inner_text().strip() for i in range(min(count, 15))]
            if not titles:
                titles = page.locator('[data-testid="job-title"]').all_inner_texts()[:15]

            result["job_count"] = len(titles)
            result["sample_jobs"] = titles
            result["success"] = len(titles) > 0 and not result["blocked_signals"]
            browser.close()
    except Exception as exc:
        result["error"] = str(exc)
    return result


def run_task_b() -> dict[str, Any]:
    _save_prompt(
        "task_b_indeed_prompt.txt",
        f"Target: {INDEED_URL}\n"
        "Goal: collect remote job listings (title, company, location, salary if visible).\n"
        "Approaches: httpx static fetch, then Playwright headless browser.\n",
    )

    httpx_result = scrape_indeed_httpx()
    playwright_result = scrape_indeed_playwright()

    report = {
        "target_url": INDEED_URL,
        "scraped_at": datetime.now(timezone.utc).isoformat(),
        "bot_protection_observed": sorted(
            set(httpx_result.get("blocked_signals", []) + playwright_result.get("blocked_signals", []))
        ),
        "approaches": [httpx_result, playwright_result],
        "summary": "",
    }

    if playwright_result["success"]:
        report["summary"] = "Playwright retrieved job titles successfully."
    elif httpx_result["success"]:
        report["summary"] = "httpx retrieved job data without browser automation."
    elif playwright_result.get("job_count", 0) > 0:
        report["summary"] = "Partial data retrieved via Playwright despite protection signals."
    else:
        report["summary"] = "Indeed blocked or limited automated access; documented approaches in report.md."

    RESULT.mkdir(parents=True, exist_ok=True)
    output_path = RESULT / "indeed_remote_jobs.json"
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    _save_prompt(
        "task_b_indeed_response.txt",
        json.dumps(report, ensure_ascii=False, indent=2),
    )
    return report
