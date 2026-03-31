from __future__ import annotations

from src.utils.date_utils import utc_now_iso


def _clip(value: float, floor: float, ceiling: float) -> float:
    return max(floor, min(ceiling, value))


def score_company(feature_row) -> dict:
    roles = int(feature_row["total_open_roles"] or 0)
    eng = int(feature_row["engineering_roles"] or 0)
    gtm = int(feature_row["go_to_market_roles"] or 0)
    news30 = int(feature_row["news_articles_30d"] or 0)
    news90 = int(feature_row["news_articles_90d"] or 0)
    pages = int(feature_row["total_pages_scraped"] or 0)
    keywords = float(feature_row["keyword_coverage_score"] or 0)
    completeness_pct = float(feature_row["data_completeness_score"] or 0)

    hiring = _clip((8 if feature_row["careers_page_found"] else 0) + min(roles * 1.5, 14) + min(eng * 0.8 + gtm * 0.6, 8), 0, 30)
    news = _clip(min(news30 * 3, 12) + min(news90 * 1.2, 8), 0, 20)
    website = _clip(min(pages * 4, 12) + (keywords * 0.18), 0, 30)
    completeness = _clip(completeness_pct * 0.1, 0, 10)

    risk_penalty = 0.0
    if pages < 2:
        risk_penalty += 4
    if roles == 0:
        risk_penalty += 3
    if news90 == 0:
        risk_penalty += 3
    risk_penalty = _clip(risk_penalty, 0, 10)

    total = _clip(hiring + news + website + completeness - risk_penalty, 0, 100)

    if total >= 75:
        band = "High Priority"
    elif total >= 55:
        band = "Medium Priority"
    elif total >= 35:
        band = "Watchlist"
    else:
        band = "Low Priority"

    return {
        "hiring_signal_score": round(hiring, 2),
        "news_signal_score": round(news, 2),
        "website_signal_score": round(website, 2),
        "completeness_score": round(completeness, 2),
        "risk_penalty_score": round(risk_penalty, 2),
        "total_score": round(total, 2),
        "score_band": band,
    }


def score_all_companies(conn) -> int:
    rows = conn.execute("SELECT * FROM company_features").fetchall()
    now = utc_now_iso()

    for row in rows:
        score = score_company(row)
        conn.execute(
            """
            INSERT INTO screening_scores (
                company_id, hiring_signal_score, news_signal_score, website_signal_score,
                completeness_score, risk_penalty_score, total_score, score_band, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(company_id) DO UPDATE SET
                hiring_signal_score = excluded.hiring_signal_score,
                news_signal_score = excluded.news_signal_score,
                website_signal_score = excluded.website_signal_score,
                completeness_score = excluded.completeness_score,
                risk_penalty_score = excluded.risk_penalty_score,
                total_score = excluded.total_score,
                score_band = excluded.score_band,
                updated_at = excluded.updated_at
            """,
            (
                row["company_id"],
                score["hiring_signal_score"],
                score["news_signal_score"],
                score["website_signal_score"],
                score["completeness_score"],
                score["risk_penalty_score"],
                score["total_score"],
                score["score_band"],
                now,
            ),
        )
    conn.commit()
    return len(rows)
