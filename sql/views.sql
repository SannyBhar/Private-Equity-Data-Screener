CREATE VIEW IF NOT EXISTS vw_company_screen AS
SELECT
    c.company_id,
    c.company_name,
    c.domain,
    c.sector,
    c.sub_sector,
    c.headquarters,
    COALESCE(f.total_pages_scraped, 0) AS total_pages_scraped,
    COALESCE(f.total_open_roles, 0) AS total_open_roles,
    COALESCE(f.news_articles_30d, 0) AS news_articles_30d,
    COALESCE(f.news_articles_90d, 0) AS news_articles_90d,
    COALESCE(s.hiring_signal_score, 0) AS hiring_signal_score,
    COALESCE(s.news_signal_score, 0) AS news_signal_score,
    COALESCE(s.website_signal_score, 0) AS website_signal_score,
    COALESCE(s.completeness_score, 0) AS completeness_score,
    COALESCE(s.risk_penalty_score, 0) AS risk_penalty_score,
    COALESCE(s.total_score, 0) AS total_score,
    COALESCE(s.score_band, 'Insufficient Data') AS score_band
FROM companies c
LEFT JOIN company_features f ON c.company_id = f.company_id
LEFT JOIN screening_scores s ON c.company_id = s.company_id;

CREATE VIEW IF NOT EXISTS vw_jobs_latest AS
SELECT
    company_id,
    title,
    location,
    department,
    employment_type,
    posted_date,
    source_url,
    scraped_at
FROM job_postings
ORDER BY scraped_at DESC;

CREATE VIEW IF NOT EXISTS vw_news_latest AS
SELECT
    company_id,
    source_name,
    title,
    url,
    published_at,
    snippet,
    sentiment_label,
    scraped_at
FROM news_articles
ORDER BY published_at DESC;
