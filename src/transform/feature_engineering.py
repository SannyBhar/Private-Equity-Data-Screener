from __future__ import annotations

from datetime import datetime, timedelta, timezone

from src.utils.date_utils import utc_now_iso


def _count_roles(rows, department: str) -> int:
    return sum(1 for r in rows if (r["department"] or "").lower() == department.lower())


def _keyword_coverage(pages) -> float:
    if not pages:
        return 0.0
    score = 0
    for row in pages:
        score += int(row["keyword_ai"] or 0)
        score += int(row["keyword_enterprise"] or 0)
        score += int(row["keyword_automation"] or 0)
        score += int(row["keyword_security"] or 0)
        score += int(row["keyword_healthcare"] or 0)
    max_score = len(pages) * 5
    return round((score / max_score) * 100, 2) if max_score else 0.0


def _completeness(total_pages: int, total_words: int, total_jobs: int, total_news_90d: int) -> float:
    pages_score = min(total_pages / 4, 1.0)
    words_score = min(total_words / 2500, 1.0)
    jobs_score = min(total_jobs / 8, 1.0)
    news_score = min(total_news_90d / 6, 1.0)
    return round(((pages_score + words_score + jobs_score + news_score) / 4) * 100, 2)


def build_company_features(conn) -> int:
    company_ids = [r["company_id"] for r in conn.execute("SELECT company_id FROM companies").fetchall()]
    now = utc_now_iso()
    now_dt = datetime.now(timezone.utc)
    cut_30 = now_dt - timedelta(days=30)
    cut_90 = now_dt - timedelta(days=90)

    for company_id in company_ids:
        pages = conn.execute(
            "SELECT word_count, keyword_ai, keyword_enterprise, keyword_automation, keyword_security, keyword_healthcare FROM website_pages_clean WHERE company_id = ? AND word_count >= 30",
            (company_id,),
        ).fetchall()
        jobs = conn.execute(
            "SELECT department FROM job_postings WHERE company_id = ?",
            (company_id,),
        ).fetchall()
        news = conn.execute(
            "SELECT published_at FROM news_articles WHERE company_id = ?",
            (company_id,),
        ).fetchall()

        total_pages = len(pages)
        total_words = sum(int(p["word_count"] or 0) for p in pages)
        total_jobs = len(jobs)
        engineering_roles = _count_roles(jobs, "Engineering")
        gtm_roles = _count_roles(jobs, "GTM")
        exec_roles = _count_roles(jobs, "Executive")

        careers_page_found = 1 if total_jobs > 0 else 0

        news_30 = 0
        news_90 = 0
        for n in news:
            if not n["published_at"]:
                continue
            try:
                dt = datetime.fromisoformat(n["published_at"].replace("Z", "+00:00"))
            except ValueError:
                continue
            if dt >= cut_30:
                news_30 += 1
            if dt >= cut_90:
                news_90 += 1

        keyword_coverage = _keyword_coverage(pages)
        completeness = _completeness(total_pages, total_words, total_jobs, news_90)

        conn.execute(
            """
            INSERT INTO company_features (
                company_id, total_pages_scraped, total_words_scraped, careers_page_found,
                total_open_roles, engineering_roles, go_to_market_roles, executive_roles,
                news_articles_30d, news_articles_90d, keyword_coverage_score, data_completeness_score, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(company_id) DO UPDATE SET
                total_pages_scraped = excluded.total_pages_scraped,
                total_words_scraped = excluded.total_words_scraped,
                careers_page_found = excluded.careers_page_found,
                total_open_roles = excluded.total_open_roles,
                engineering_roles = excluded.engineering_roles,
                go_to_market_roles = excluded.go_to_market_roles,
                executive_roles = excluded.executive_roles,
                news_articles_30d = excluded.news_articles_30d,
                news_articles_90d = excluded.news_articles_90d,
                keyword_coverage_score = excluded.keyword_coverage_score,
                data_completeness_score = excluded.data_completeness_score,
                updated_at = excluded.updated_at
            """,
            (
                company_id,
                total_pages,
                total_words,
                careers_page_found,
                total_jobs,
                engineering_roles,
                gtm_roles,
                exec_roles,
                news_30,
                news_90,
                keyword_coverage,
                completeness,
                now,
            ),
        )

    conn.commit()
    return len(company_ids)
