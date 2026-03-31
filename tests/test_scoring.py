from src.transform.scoring import score_company


def test_score_company_bounds_and_band() -> None:
    row = {
        "careers_page_found": 1,
        "total_open_roles": 18,
        "engineering_roles": 8,
        "go_to_market_roles": 6,
        "news_articles_30d": 4,
        "news_articles_90d": 10,
        "total_pages_scraped": 6,
        "keyword_coverage_score": 72.0,
        "data_completeness_score": 88.0,
    }
    score = score_company(row)
    assert 0 <= score["total_score"] <= 100
    assert score["score_band"] in {"High Priority", "Medium Priority", "Watchlist", "Low Priority"}
    assert score["hiring_signal_score"] <= 30
    assert score["news_signal_score"] <= 20
    assert score["website_signal_score"] <= 30
