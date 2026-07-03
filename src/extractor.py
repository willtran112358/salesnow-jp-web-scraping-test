"""Extract corporate profile fields from HTML or plain text."""

from __future__ import annotations

import re
from typing import Any, Optional

from bs4 import BeautifulSoup, Tag

from .config import FIELD_LABELS


def _normalize_label(value: str) -> str:
    return re.sub(r"\s+", "", value).lower()


def _label_matches(label: str, aliases: tuple[str, ...]) -> bool:
    normalized = _normalize_label(label)
    for alias in aliases:
        alias_norm = _normalize_label(alias)
        if normalized == alias_norm or alias_norm in normalized:
            return True
    return False


def _clean_value(value: str) -> str:
    value = re.sub(r"\s+", " ", value).strip()
    value = value.replace("\u3000", " ")
    return value


def _clean_address(value: str) -> str:
    value = _clean_value(value)
    value = re.split(r"\s*(?:MAP|アクセス情報|電車の場合|お車の場合)", value)[0].strip()
    return value


def _clean_representative(value: str) -> str:
    value = _clean_value(value)
    value = re.split(r"\s*役員", value)[0].strip()
    value = re.sub(r"\s*CEO\s*", " ", value).strip()
    return value


def _extract_from_pairs(pairs: list[tuple[str, str]]) -> dict[str, Optional[str]]:
    result = {
        "head_office_address": None,
        "representative_name": None,
        "capital_stock": None,
        "establishment_date": None,
    }
    for label, value in pairs:
        cleaned = _clean_value(value)
        if not cleaned:
            continue
        for field, aliases in FIELD_LABELS.items():
            if result[field] is None and _label_matches(label, aliases):
                cleaned_field = cleaned
                if field == "head_office_address":
                    cleaned_field = _clean_address(cleaned)
                elif field == "representative_name":
                    cleaned_field = _clean_representative(cleaned)
                result[field] = cleaned_field
    return result


def _pairs_from_table(table: Tag) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for row in table.find_all("tr"):
        cells = row.find_all(["th", "td"])
        if len(cells) < 2:
            continue
        label = cells[0].get_text(" ", strip=True)
        value = " ".join(cell.get_text(" ", strip=True) for cell in cells[1:])
        if label and value:
            pairs.append((label, value))
    return pairs


def _pairs_from_dl(dl: Tag) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    dts = dl.find_all("dt")
    for dt in dts:
        dd = dt.find_next_sibling("dd")
        if dd is None:
            continue
        label = dt.get_text(" ", strip=True)
        value = dd.get_text(" ", strip=True)
        if label and value:
            pairs.append((label, value))
    return pairs


def _pairs_from_definition_lists(soup: BeautifulSoup) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for dl in soup.find_all("dl"):
        pairs.extend(_pairs_from_dl(dl))
    return pairs


def _pairs_from_tables(soup: BeautifulSoup) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for table in soup.find_all("table"):
        pairs.extend(_pairs_from_table(table))
    return pairs


def _pairs_from_labeled_divs(soup: BeautifulSoup) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for elem in soup.find_all(["div", "li", "p", "span"]):
        classes = " ".join(elem.get("class", []))
        if not re.search(r"(label|title|name|item|row|field|th)", classes, re.I):
            continue
        text = elem.get_text(" ", strip=True)
        if "：" in text:
            label, value = text.split("：", 1)
        elif ":" in text:
            label, value = text.split(":", 1)
        else:
            continue
        label = label.strip()
        value = value.strip()
        if label and value and len(label) <= 30:
            pairs.append((label, value))
    return pairs


def _pairs_from_rows(soup: BeautifulSoup) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for row in soup.select("div[class*='row'], li[class*='item'], tr, .p-company-data__item"):
        children = row.find_all(["dt", "th", "span", "p", "div"], recursive=False)
        if len(children) >= 2:
            label = children[0].get_text(" ", strip=True)
            value = children[1].get_text(" ", strip=True)
            if label and value and len(label) <= 30:
                pairs.append((label, value))
    return pairs


def extract_from_html(html: str) -> dict[str, Optional[str]]:
    soup = BeautifulSoup(html, "lxml")
    pairs: list[tuple[str, str]] = []
    pairs.extend(_pairs_from_tables(soup))
    pairs.extend(_pairs_from_definition_lists(soup))
    pairs.extend(_pairs_from_labeled_divs(soup))
    pairs.extend(_pairs_from_rows(soup))
    result = _extract_from_pairs(pairs)
    text = soup.get_text("\n", strip=True)
    return _merge_results(result, extract_from_text(text))


def extract_from_text(text: str) -> dict[str, Optional[str]]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    pairs: list[tuple[str, str]] = []

    patterns = [
        (r"^(本社所在地|本社住所|所在地|本社)\s*[:：]\s*(.+)$", "head_office_address"),
        (r"^(代表取締役社長|代表取締役会長|代表取締役|代表者|代表)\s*[:：]\s*(.+)$", "representative_name"),
        (r"^資本金\s*[:：]\s*(.+)$", "capital_stock"),
        (r"^(設立年月日|設立年月|設立|創業)\s*[:：]\s*(.+)$", "establishment_date"),
        (r"(?:株式会社[^\n]{0,30})?代表取締役社長\s+([^\n]+)", "representative_name"),
        (r"代表取締役社長\s+([一-龥ぁ-んァ-ンー・\s]+)", "representative_name"),
    ]

    result: dict[str, Optional[str]] = {
        "head_office_address": None,
        "representative_name": None,
        "capital_stock": None,
        "establishment_date": None,
    }

    for line in lines:
        for regex, field in patterns:
            match = re.match(regex, line)
            if match and result[field] is None:
                raw = _clean_value(match.group(2) if match.lastindex == 2 else match.group(1))
                if field == "head_office_address":
                    raw = _clean_address(raw)
                elif field == "representative_name":
                    raw = _clean_representative(raw)
                result[field] = raw

        if "：" in line or ":" in line:
            sep = "：" if "：" in line else ":"
            label, value = line.split(sep, 1)
            pairs.append((label.strip(), value.strip()))

    pair_result = _extract_from_pairs(pairs)
    return _merge_results(result, pair_result)


def _merge_results(
    primary: dict[str, Optional[str]],
    secondary: dict[str, Optional[str]],
) -> dict[str, Optional[str]]:
    merged = dict(primary)
    for key, value in secondary.items():
        if merged.get(key) in (None, "") and value:
            merged[key] = value
    return merged


def to_japanese_record(company: dict[str, Any], extracted: dict[str, Optional[str]], source_url: str) -> dict[str, str]:
    return {
        "企業名": company["name"],
        "URL": company["url"],
        "取得元ページ": source_url,
        "本社住所": extracted.get("head_office_address") or "",
        "代表氏名": extracted.get("representative_name") or "",
        "資本金": extracted.get("capital_stock") or "",
        "設立年月": extracted.get("establishment_date") or "",
    }
