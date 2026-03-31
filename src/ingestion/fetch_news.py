from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import quote_plus

import requests

from src.config import REQUEST_TIMEOUT_SECONDS, USER_AGENT
from src.utils.date_utils import parse_date_to_iso, utc_now_iso


def _google_news_rss_url(company_name: str) -> str:
    query = quote_plus(f'"{company_name}" B2B SaaS')
    return f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"


def _fetch_rss(url: str) -> str:
    try:
        r = requests.get(url, timeout=REQUEST_TIMEOUT_SECONDS, headers={"User-Agent": USER_AGENT})
        if r.status_code >= 400:
            return ""
        return r.text
    except requests.RequestException:
        return ""


def _sentiment_label(text: str) -> str:
    low = (text or "").lower()
    positive = ["growth", "launch", "partnership", "expands", "funding", "wins"]
    negative = ["layoff", "breach", "lawsuit", "decline", "cuts", "investigation"]
    if any(k in low for k in negative):
        return "negative"
    if any(k in low for k in positive):
        return "positive"
    return "neutral"


def _parse_items(xml_text: str, max_items: int = 12) -> list[dict]:
    if not xml_text.strip():
        return []
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return []

    items: list[dict] = []
    for item in root.findall("./channel/item")[:max_items]:
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        pub = parse_date_to_iso(item.findtext("pubDate"))
        desc = (item.findtext("description") or "").strip()
        source = item.find("source")
        source_name = (source.text.strip() if source is not None and source.text else "Google News")

        if not title or not link:
            continue
        items.append(
            {
                "source_name": source_name,
                "title": title,
                "url": link,
                "published_at": pub,
                "snippet": desc,
                "sentiment_label": _sentiment_label(f"{title} {desc}"),
            }
        )
    return items


def fetch_company_news(conn, company_id: int, company_name: str, news_raw_dir: Path) -> int:
    rss_url = _google_news_rss_url(company_name)
    xml_text = _fetch_rss(rss_url)
    now = utc_now_iso()

    if xml_text:
        news_raw_dir.mkdir(parents=True, exist_ok=True)
        out = news_raw_dir / f"{company_id}_news.xml"
        out.write_text(xml_text, encoding="utf-8", errors="ignore")

    rows = _parse_items(xml_text)
    for row in rows:
        conn.execute(
            """
            INSERT INTO news_articles (
                company_id, source_name, title, url, published_at, snippet, sentiment_label, scraped_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(company_id, title, url) DO UPDATE SET
                source_name = excluded.source_name,
                published_at = excluded.published_at,
                snippet = excluded.snippet,
                sentiment_label = excluded.sentiment_label,
                scraped_at = excluded.scraped_at
            """,
            (
                company_id,
                row["source_name"],
                row["title"],
                row["url"],
                row["published_at"],
                row["snippet"],
                row["sentiment_label"],
                now,
            ),
        )
    conn.commit()
    return len(rows)


def fetch_all_news(conn, companies_df, news_raw_dir: Path) -> int:
    total = 0
    for row in companies_df.itertuples(index=False):
        total += fetch_company_news(conn, row.company_id, row.company_name, news_raw_dir)
    return total
