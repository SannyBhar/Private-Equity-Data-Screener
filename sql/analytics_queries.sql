-- Top ranked companies for screening
SELECT company_name, total_score, score_band, total_open_roles, news_articles_30d
FROM vw_company_screen
ORDER BY total_score DESC
LIMIT 10;

-- Companies with highest hiring activity
SELECT company_name, total_open_roles, engineering_roles, go_to_market_roles, executive_roles
FROM companies c
JOIN company_features f USING (company_id)
ORDER BY total_open_roles DESC;

-- Compare signal dimensions
SELECT company_name, hiring_signal_score, news_signal_score, website_signal_score, total_score
FROM vw_company_screen
ORDER BY total_score DESC;

-- Data quality check
SELECT
  COUNT(*) AS company_count,
  AVG(total_pages_scraped) AS avg_pages,
  AVG(total_open_roles) AS avg_roles,
  AVG(news_articles_90d) AS avg_news_90d,
  AVG(data_completeness_score) AS avg_completeness
FROM company_features;
