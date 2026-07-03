"""Shared configuration."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
RESULT = ROOT / "result"
PROMPTS = ROOT / "prompts"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/131.0.0.0 Safari/537.36"
)

DEFAULT_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
}

PROFILE_LINK_KEYWORDS = (
    "会社概要",
    "会社案内",
    "会社プロフィール",
    "企業概要",
    "company profile",
    "company overview",
    "about us",
    "outline",
    "profile",
    "overview",
)

# Fallback profile paths tried when link discovery is weak.
PROFILE_PATH_CANDIDATES = (
    "/company/outline/",
    "/company/profile/",
    "/corporate/profile/",
    "/corporate/about/outline.html",
    "/corporate/outline/",
    "/about/company/",
    "/company/",
    "/jp/corporate/profile/",
    "/jp/company/profile/",
    "/corporate/company/",
    "/about/company/profile/",
    "/company_info/profile/",
    "/corporate/about/company/",
)

FIELD_LABELS = {
    "head_office_address": (
        "本社所在地",
        "本社住所",
        "所在地",
        "本社",
        "住所",
        "head office",
        "address",
    ),
    "representative_name": (
        "代表者",
        "代表取締役",
        "代表取締役社長",
        "代表取締役会長",
        "代表",
        "representative",
        "president",
        "ceo",
    ),
    "capital_stock": (
        "資本金",
        "capital",
    ),
    "establishment_date": (
        "設立",
        "設立年月日",
        "設立年月",
        "創業",
        "founded",
        "establishment",
    ),
}
