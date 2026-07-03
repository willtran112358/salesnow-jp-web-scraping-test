"""PDF text extraction for company profiles."""

from __future__ import annotations

from io import BytesIO
from typing import Optional

import httpx

from .config import DEFAULT_HEADERS
from .extractor import extract_from_text


def fetch_pdf_text(url: str) -> Optional[str]:
    try:
        with httpx.Client(headers=DEFAULT_HEADERS, follow_redirects=True, verify=False, timeout=60) as client:
            response = client.get(url)
            if response.status_code >= 400:
                return None
            from pypdf import PdfReader

            reader = PdfReader(BytesIO(response.content))
            return "\n".join((page.extract_text() or "") for page in reader.pages)
    except Exception:
        return None


def extract_from_pdf_url(url: str) -> dict[str, Optional[str]]:
    text = fetch_pdf_text(url)
    if not text:
        return {
            "head_office_address": None,
            "representative_name": None,
            "capital_stock": None,
            "establishment_date": None,
        }
    return extract_from_text(text)
