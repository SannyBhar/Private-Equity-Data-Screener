PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS companies (
    company_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name TEXT NOT NULL,
    domain TEXT NOT NULL UNIQUE,
    sector TEXT,
    sub_sector TEXT,
    headquarters TEXT,
    source_type TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS website_pages_raw (
    page_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    url TEXT NOT NULL,
    page_type TEXT NOT NULL,
    status_code INTEGER,
    html_content TEXT,
    fetched_at TEXT,
    UNIQUE(company_id, url),
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

CREATE TABLE IF NOT EXISTS website_pages_clean (
    clean_page_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    url TEXT NOT NULL,
    page_type TEXT NOT NULL,
    page_title TEXT,
    clean_text TEXT,
    word_count INTEGER,
    keyword_ai INTEGER,
    keyword_enterprise INTEGER,
    keyword_automation INTEGER,
    keyword_security INTEGER,
    keyword_healthcare INTEGER,
    updated_at TEXT,
    UNIQUE(company_id, url),
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

CREATE TABLE IF NOT EXISTS job_postings (
    job_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    source_url TEXT,
    title TEXT,
    location TEXT,
    department TEXT,
    employment_type TEXT,
    posting_text TEXT,
    posted_date TEXT,
    scraped_at TEXT,
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

CREATE TABLE IF NOT EXISTS news_articles (
    article_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    source_name TEXT,
    title TEXT,
    url TEXT,
    published_at TEXT,
    snippet TEXT,
    sentiment_label TEXT,
    scraped_at TEXT,
    UNIQUE(company_id, title, url),
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

CREATE TABLE IF NOT EXISTS company_features (
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
    updated_at TEXT,
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

CREATE TABLE IF NOT EXISTS screening_scores (
    company_id INTEGER PRIMARY KEY,
    hiring_signal_score REAL,
    news_signal_score REAL,
    website_signal_score REAL,
    completeness_score REAL,
    risk_penalty_score REAL,
    total_score REAL,
    score_band TEXT,
    updated_at TEXT,
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

CREATE TABLE IF NOT EXISTS llm_summaries (
    summary_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    summary_type TEXT,
    model_name TEXT,
    prompt_version TEXT,
    summary_text TEXT,
    evidence_text TEXT,
    generated_at TEXT,
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);
