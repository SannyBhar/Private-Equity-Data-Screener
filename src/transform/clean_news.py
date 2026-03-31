from __future__ import annotations

from src.utils.date_utils import parse_date_to_iso
from src.utils.text_cleaning import normalize_whitespace


def clean_news(conn) -> int:
    rows = conn.execute("SELECT article_id, title, snippet, source_name, published_at FROM news_articles").fetchall()
    updated = 0
    for row in rows:
        title = normalize_whitespace(row["title"] or "")
        snippet = normalize_whitespace(row["snippet"] or "")
        source_name = normalize_whitespace(row["source_name"] or "Google News")
        published_at = parse_date_to_iso(row["published_at"]) if row["published_at"] else None

        conn.execute(
            """
            UPDATE news_articles
            SET title = ?, snippet = ?, source_name = ?, published_at = ?
            WHERE article_id = ?
            """,
            (title, snippet, source_name, published_at, row["article_id"]),
        )
        updated += 1
    conn.commit()
    return updated
