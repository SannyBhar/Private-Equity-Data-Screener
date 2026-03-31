from __future__ import annotations

from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from src.config import ATS_HOST_HINTS, CAREER_PATHS, REQUEST_TIMEOUT_SECONDS, USER_AGENT
from src.utils.date_utils import utc_now_iso
from src.utils.url_utils import build_url


def _fetch(url: str) -> tuple[int | None, str]:
    try:
        r = requests.get(url, timeout=REQUEST_TIMEOUT_SECONDS, headers={"User-Agent": USER_AGENT})
        return r.status_code, r.text
    except requests.RequestException:
        return None, ""


def _extract_jobs_from_html(soup: BeautifulSoup, source_url: str) -> list[dict]:
    jobs: list[dict] = []
    selectors = ["a", "h2", "h3", '[class*="job"]', '[class*="role"]']
    seen: set[str] = set()
    for selector in selectors:
        for node in soup.select(selector):
            text = " ".join(node.get_text(" ", strip=True).split())
            if len(text) < 8 or len(text) > 120:
                continue
            low = text.lower()
            if any(skip in low for skip in ["cookie", "privacy", "benefits", "culture"]):
                continue
            if text.lower() in seen:
                continue
            seen.add(text.lower())
            jobs.append(
                {
                    "source_url": source_url,
                    "title": text,
                    "location": None,
                    "department": _infer_department(text),
                    "employment_type": None,
                    "posting_text": text,
                    "posted_date": None,
                }
            )
            if len(jobs) >= 30:
                return jobs
    return jobs


def _infer_department(title: str) -> str:
    low = title.lower()
    if any(k in low for k in ["engineer", "developer", "platform", "data scientist", "ml"]):
        return "Engineering"
    if any(k in low for k in ["sales", "account", "marketing", "customer success", "partnership"]):
        return "GTM"
    if any(k in low for k in ["chief", "vp", "head of", "director"]):
        return "Executive"
    return "Other"


def _discover_ats_link(base_url: str, html: str) -> str | None:
    soup = BeautifulSoup(html or "", "html.parser")
    for link in soup.select("a[href]"):
        href = (link.get("href") or "").strip()
        if not href:
            continue
        full = urljoin(base_url, href)
        if any(host in full for host in ATS_HOST_HINTS):
            return full
    return None


def scrape_company_careers(conn, company_id: int, domain: str) -> int:
    now = utc_now_iso()
    roles_inserted = 0
    careers_found = 0

    candidate_urls = [build_url(domain, path) for path in CAREER_PATHS]

    homepage_status, homepage_html = _fetch(build_url(domain, "/"))
    if homepage_status and homepage_status < 400:
        ats = _discover_ats_link(build_url(domain, "/"), homepage_html)
        if ats:
            candidate_urls.append(ats)

    conn.execute("DELETE FROM job_postings WHERE company_id = ?", (company_id,))

    for url in candidate_urls:
        status, html = _fetch(url)
        if status is None or status >= 400 or not html:
            continue

        careers_found = 1
        soup = BeautifulSoup(html, "html.parser")
        jobs = _extract_jobs_from_html(soup, url)
        for job in jobs:
            conn.execute(
                """
                INSERT INTO job_postings (
                    company_id, source_url, title, location, department,
                    employment_type, posting_text, posted_date, scraped_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    company_id,
                    job["source_url"],
                    job["title"],
                    job["location"],
                    job["department"],
                    job["employment_type"],
                    job["posting_text"],
                    job["posted_date"],
                    now,
                ),
            )
            roles_inserted += 1

        if roles_inserted > 0:
            break

    conn.execute(
        """
        UPDATE company_features
        SET careers_page_found = ?, updated_at = ?
        WHERE company_id = ?
        """,
        (careers_found, now, company_id),
    )
    conn.commit()
    return roles_inserted


def scrape_all_careers(conn, companies_df) -> int:
    total = 0
    for row in companies_df.itertuples(index=False):
        total += scrape_company_careers(conn, row.company_id, row.domain)
    return total
