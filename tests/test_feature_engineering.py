import sqlite3

from src.transform.feature_engineering import build_company_features


def _setup_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.executescript(
        """
        CREATE TABLE companies (company_id INTEGER PRIMARY KEY, company_name TEXT);
        CREATE TABLE website_pages_clean (
            clean_page_id INTEGER PRIMARY KEY,
            company_id INTEGER,
            word_count INTEGER,
            keyword_ai INTEGER,
            keyword_enterprise INTEGER,
            keyword_automation INTEGER,
            keyword_security INTEGER,
            keyword_healthcare INTEGER
        );
        CREATE TABLE job_postings (job_id INTEGER PRIMARY KEY, company_id INTEGER, department TEXT);
        CREATE TABLE news_articles (article_id INTEGER PRIMARY KEY, company_id INTEGER, published_at TEXT);
        CREATE TABLE company_features (
            company_id INTEGER PRIMARY KEY,
            total_pages_scraped INTEGER,
            total_words_scraped INTEGER,
            careers_page_found INTEGER,
            total_open_roles INTEGER,
            engineering_roles INTEGER,
            go_to_market_roles INTEGER,
            executive_roles INTEGER,
            news_articles_30d INTEGER,
            news_articles_90d INTEGER,
            keyword_coverage_score REAL,
            data_completeness_score REAL,
            updated_at TEXT
        );
        """
    )
    return conn


def test_build_company_features_basic_counts() -> None:
    conn = _setup_conn()
    conn.execute("INSERT INTO companies(company_id, company_name) VALUES (1, 'Acme')")
    conn.execute(
        "INSERT INTO website_pages_clean(company_id, word_count, keyword_ai, keyword_enterprise, keyword_automation, keyword_security, keyword_healthcare) VALUES (1, 1000, 1, 1, 0, 1, 0)"
    )
    conn.execute("INSERT INTO job_postings(company_id, department) VALUES (1, 'Engineering')")
    conn.execute("INSERT INTO news_articles(company_id, published_at) VALUES (1, '2026-03-01T00:00:00+00:00')")
    conn.commit()

    count = build_company_features(conn)
    assert count == 1

    row = conn.execute("SELECT * FROM company_features WHERE company_id = 1").fetchone()
    assert row["total_pages_scraped"] == 1
    assert row["total_words_scraped"] == 1000
    assert row["total_open_roles"] == 1
    assert row["engineering_roles"] == 1
    assert row["news_articles_90d"] >= 1
