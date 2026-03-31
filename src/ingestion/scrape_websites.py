from __future__ import annotations

from pathlib import Path

import requests

from src.config import PAGE_PATHS, REQUEST_TIMEOUT_SECONDS, USER_AGENT
from src.utils.date_utils import utc_now_iso
from src.utils.url_utils import build_url


def fetch_url(url: str) -> tuple[int | None, str]:
    try:
        resp = requests.get(
            url,
            timeout=REQUEST_TIMEOUT_SECONDS,
            headers={"User-Agent": USER_AGENT},
        )
        return resp.status_code, resp.text
    except requests.RequestException:
        return None, ""


def scrape_company_pages(conn, company_id: int, domain: str, html_cache_dir: Path) -> int:
    successful_pages = 0
    now = utc_now_iso()

    for page_type, path in PAGE_PATHS.items():
        url = build_url(domain, path)
        status_code, html = fetch_url(url)

        conn.execute(
            """
            INSERT INTO website_pages_raw (company_id, url, page_type, status_code, html_content, fetched_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(company_id, url) DO UPDATE SET
                page_type = excluded.page_type,
                status_code = excluded.status_code,
                html_content = excluded.html_content,
                fetched_at = excluded.fetched_at
            """,
            (company_id, url, page_type, status_code, html, now),
        )
        if status_code is not None and status_code < 400 and html.strip():
            successful_pages += 1

        if html:
            safe_file = html_cache_dir / f"{company_id}_{page_type}.html"
            safe_file.write_text(html, encoding="utf-8", errors="ignore")

    conn.commit()
    return successful_pages


def scrape_all_websites(conn, companies_df, html_cache_dir: Path) -> int:
    total = 0
    for row in companies_df.itertuples(index=False):
        total += scrape_company_pages(conn, row.company_id, row.domain, html_cache_dir)
    return total
