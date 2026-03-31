from __future__ import annotations

from src.utils.date_utils import parse_date_to_iso
from src.utils.text_cleaning import normalize_whitespace


def clean_jobs(conn) -> int:
    rows = conn.execute("SELECT job_id, title, posting_text, posted_date, department FROM job_postings").fetchall()
    updated = 0

    for row in rows:
        title = normalize_whitespace(row["title"] or "")
        posting_text = normalize_whitespace(row["posting_text"] or title)
        posted_date = parse_date_to_iso(row["posted_date"]) if row["posted_date"] else None
        department = row["department"] or _infer_department(title)

        conn.execute(
            """
            UPDATE job_postings
            SET title = ?, posting_text = ?, posted_date = ?, department = ?
            WHERE job_id = ?
            """,
            (title, posting_text, posted_date, department, row["job_id"]),
        )
        updated += 1

    conn.commit()
    return updated


def _infer_department(title: str) -> str:
    low = title.lower()
    if any(k in low for k in ["engineer", "developer", "data", "architect"]):
        return "Engineering"
    if any(k in low for k in ["sales", "marketing", "account", "customer success"]):
        return "GTM"
    if any(k in low for k in ["chief", "vp", "director", "head"]):
        return "Executive"
    return "Other"
