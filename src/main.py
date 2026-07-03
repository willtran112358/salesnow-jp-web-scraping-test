"""CLI entrypoint for SalesNow scraping test."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

if __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.ai_extractor import extract_with_ai
from src.browser_fetcher import fetch_rendered_html
from src.companies import load_companies
from src.config import RESULT
from src.discover import collect_page_texts, discover_profile_urls
from src.extractor import extract_from_html, to_japanese_record
from src.fetcher import Fetcher
from src.indeed_scraper import run_task_b
from src.pdf_extractor import extract_from_pdf_url


def _log(message: str) -> None:
    encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
    try:
        print(message, flush=True)
    except UnicodeEncodeError:
        sys.stdout.buffer.write((message + "\n").encode(encoding, errors="replace"))
        sys.stdout.buffer.flush()


def run_task_a() -> list[dict[str, str]]:
    companies = load_companies()
    records: list[dict[str, str]] = []

    RESULT.mkdir(parents=True, exist_ok=True)

    with Fetcher(delay=0.8) as fetcher:
        for company in companies:
            _log(f"[Task A] {company.get('name_en', company['name'])} ...")
            profile_urls = discover_profile_urls(
                fetcher,
                company["url"],
                profile_urls=company.get("profile_urls"),
            )
            html_pages: list[tuple[str, str]] = []
            for url in profile_urls:
                text, final_url = fetcher.get_text(url)
                if text:
                    html_pages.append((final_url or url, text))

            if company.get("use_browser"):
                for url in profile_urls[:2]:
                    rendered = fetch_rendered_html(url)
                    if rendered:
                        html_pages.append((url, rendered))

            for pdf_url in company.get("pdf_urls", []):
                pdf_data = extract_from_pdf_url(pdf_url)
                plain_from_pdf = "\n".join(f"{k}: {v}" for k, v in pdf_data.items() if v)
                if plain_from_pdf:
                    html_pages.append((pdf_url, f"<html><body>{plain_from_pdf}</body></html>"))

            plain_text = collect_page_texts(fetcher, [u for u, _ in html_pages] or profile_urls)
            if company.get("pdf_urls"):
                from src.pdf_extractor import fetch_pdf_text

                for pdf_url in company["pdf_urls"]:
                    pdf_text = fetch_pdf_text(pdf_url)
                    if pdf_text:
                        plain_text += f"\n\n--- PDF: {pdf_url} ---\n{pdf_text}"
            extracted, source_url = extract_with_ai(
                company_name=company["name"],
                company_url=company["url"],
                html_pages=html_pages,
                plain_text=plain_text,
            )
            record = to_japanese_record(company, extracted, source_url)
            records.append(record)
            _log(
                f"  -> address={bool(record['本社住所'])}, "
                f"rep={bool(record['代表氏名'])}, "
                f"capital={bool(record['資本金'])}, "
                f"founded={bool(record['設立年月'])}"
            )

    json_path = RESULT / "companies.json"
    csv_path = RESULT / "companies.csv"

    json_path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")

    fieldnames = ["企業名", "URL", "取得元ページ", "本社住所", "代表氏名", "資本金", "設立年月"]
    with csv_path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    _log(f"\nSaved {len(records)} records to {json_path} and {csv_path}")
    return records


def main() -> None:
    parser = argparse.ArgumentParser(description="SalesNow JP web scraping test runner")
    parser.add_argument("--task", choices=["a", "b", "all"], default="all")
    args = parser.parse_args()

    if args.task in ("a", "all"):
        run_task_a()
    if args.task in ("b", "all"):
        _log("\n[Task B] Indeed Vietnam ...")
        report = run_task_b()
        _log(f"  -> {report['summary']}")


if __name__ == "__main__":
    main()
