from __future__ import annotations

import re
from typing import Iterable

from bs4 import BeautifulSoup


BOILERPLATE_SELECTORS = [
    "script",
    "style",
    "noscript",
    "svg",
    "header",
    "footer",
    "nav",
    "form",
]


def html_to_clean_text(html: str) -> tuple[str, str]:
    """Return (title, cleaned_text) from HTML content."""
    soup = BeautifulSoup(html or "", "html.parser")
    title = (soup.title.string.strip() if soup.title and soup.title.string else "")

    for selector in BOILERPLATE_SELECTORS:
        for node in soup.select(selector):
            node.decompose()

    text = soup.get_text(" ", strip=True)
    text = normalize_whitespace(text)
    return title, text


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def normalize_company_name(name: str) -> str:
    cleaned = normalize_whitespace(name)
    return cleaned.replace(".com", "").strip()


def keyword_flag(text: str, keywords: Iterable[str]) -> int:
    haystack = f" {text.lower()} "
    for kw in keywords:
        if f" {kw.lower()} " in haystack:
            return 1
    return 0


def clipped(text: str, max_len: int = 600) -> str:
    cleaned = normalize_whitespace(text)
    if len(cleaned) <= max_len:
        return cleaned
    return cleaned[: max_len - 3].rstrip() + "..."
