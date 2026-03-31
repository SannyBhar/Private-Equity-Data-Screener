from __future__ import annotations

from src.config import KEYWORDS
from src.utils.date_utils import utc_now_iso
from src.utils.text_cleaning import html_to_clean_text, keyword_flag


def clean_website_pages(conn) -> int:
    conn.execute("DELETE FROM website_pages_clean")
    rows = conn.execute(
        """
        SELECT company_id, url, page_type, html_content
        FROM website_pages_raw
        """
    ).fetchall()

    now = utc_now_iso()
    cleaned_count = 0
    for row in rows:
        if not row["html_content"]:
            continue
        title, clean_text = html_to_clean_text(row["html_content"] or "")
        if not clean_text:
            continue
        word_count = len(clean_text.split())

        conn.execute(
            """
            INSERT INTO website_pages_clean (
                company_id, url, page_type, page_title, clean_text, word_count,
                keyword_ai, keyword_enterprise, keyword_automation, keyword_security, keyword_healthcare,
                updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(company_id, url) DO UPDATE SET
                page_type = excluded.page_type,
                page_title = excluded.page_title,
                clean_text = excluded.clean_text,
                word_count = excluded.word_count,
                keyword_ai = excluded.keyword_ai,
                keyword_enterprise = excluded.keyword_enterprise,
                keyword_automation = excluded.keyword_automation,
                keyword_security = excluded.keyword_security,
                keyword_healthcare = excluded.keyword_healthcare,
                updated_at = excluded.updated_at
            """,
            (
                row["company_id"],
                row["url"],
                row["page_type"],
                title,
                clean_text,
                word_count,
                keyword_flag(clean_text, KEYWORDS["ai"]),
                keyword_flag(clean_text, KEYWORDS["enterprise"]),
                keyword_flag(clean_text, KEYWORDS["automation"]),
                keyword_flag(clean_text, KEYWORDS["security"]),
                keyword_flag(clean_text, KEYWORDS["healthcare"]),
                now,
            ),
        )
        cleaned_count += 1

    conn.commit()
    return cleaned_count
