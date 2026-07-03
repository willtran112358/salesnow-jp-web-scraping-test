"""AI-assisted extraction layer (prompt + structured parsing)."""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from .config import PROMPTS
from .extractor import extract_from_html, extract_from_text


EXTRACTION_PROMPT_TEMPLATE = """あなたは日本の上場企業ウェブサイトから企業情報を抽出するアシスタントです。
以下のテキストから、指定された4項目のみをJSON形式で抽出してください。
推測や補完はせず、テキストに明示されている情報だけを使ってください。
見つからない項目は空文字 "" にしてください。

抽出項目:
- head_office_address（本社住所）
- representative_name（代表氏名）
- capital_stock（資本金）
- establishment_date（設立年月）

企業名: {company_name}
URL: {company_url}

--- ページテキスト ---
{page_text}
--- ここまで ---

出力形式（JSONのみ）:
{{
  "head_office_address": "",
  "representative_name": "",
  "capital_stock": "",
  "establishment_date": ""
}}
"""


def build_prompt(company_name: str, company_url: str, page_text: str, max_chars: int = 12000) -> str:
    trimmed = page_text[:max_chars]
    if len(page_text) > max_chars:
        trimmed += "\n...[truncated]..."
    return EXTRACTION_PROMPT_TEMPLATE.format(
        company_name=company_name,
        company_url=company_url,
        page_text=trimmed,
    )


def _parse_json_response(content: str) -> Optional[dict[str, str]]:
    match = re.search(r"\{[^{}]*\}", content, re.DOTALL)
    if not match:
        return None
    try:
        data = json.loads(match.group())
        return {k: str(v).strip() for k, v in data.items()}
    except json.JSONDecodeError:
        return None


def extract_with_ai(
    company_name: str,
    company_url: str,
    html_pages: list[tuple[str, str]],
    plain_text: str,
    prompts_dir: Path = PROMPTS,
) -> tuple[dict[str, Optional[str]], str]:
    """Return extracted fields and the profile URL used as primary source."""
    prompts_dir.mkdir(parents=True, exist_ok=True)

    merged: dict[str, Optional[str]] = {
        "head_office_address": None,
        "representative_name": None,
        "capital_stock": None,
        "establishment_date": None,
    }
    primary_url = company_url

    for url, html in html_pages:
        parsed = extract_from_html(html)
        for key, value in parsed.items():
            if value and not merged.get(key):
                merged[key] = value
                primary_url = url

    text_parsed = extract_from_text(plain_text)
    for key, value in text_parsed.items():
        if value and not merged.get(key):
            merged[key] = value

    prompt = build_prompt(company_name, company_url, plain_text)
    slug = re.sub(r"[^\w\-]+", "_", company_name)[:40]
    prompt_path = prompts_dir / f"task_a_{slug}.txt"
    prompt_path.write_text(prompt, encoding="utf-8")

    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        try:
            from openai import OpenAI

            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
                messages=[
                    {"role": "system", "content": "Extract corporate data and return JSON only."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0,
            )
            content = response.choices[0].message.content or ""
            ai_data = _parse_json_response(content)
            response_path = prompts_dir / f"task_a_{slug}_response.txt"
            response_path.write_text(content, encoding="utf-8")
            if ai_data:
                for key in merged:
                    if ai_data.get(key):
                        merged[key] = ai_data[key]
        except Exception as exc:
            fallback_path = prompts_dir / f"task_a_{slug}_response.txt"
            fallback_path.write_text(
                f"OpenAI call failed; used rule-based extraction.\nError: {exc}\n\n"
                f"Rule-based result:\n{json.dumps(merged, ensure_ascii=False, indent=2)}",
                encoding="utf-8",
            )
    else:
        response_path = prompts_dir / f"task_a_{slug}_response.txt"
        response_path.write_text(
            "OPENAI_API_KEY not set. Used rule-based HTML/text extraction (same prompt saved for review).\n\n"
            f"Extracted:\n{json.dumps(merged, ensure_ascii=False, indent=2)}\n\n"
            f"Generated at: {datetime.now(timezone.utc).isoformat()}",
            encoding="utf-8",
        )

    return merged, primary_url
