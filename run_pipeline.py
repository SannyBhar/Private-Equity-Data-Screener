from __future__ import annotations

import argparse

import pandas as pd

from src.config import DB_PATH, HTML_CACHE_DIR, NEWS_RAW_DIR, SEED_CSV, SQL_DIR, ensure_directories
from src.db.connection import get_connection
from src.db.init_db import initialize_database
from src.ingestion.fetch_news import fetch_all_news
from src.ingestion.load_seed import load_seed_companies, upsert_companies
from src.ingestion.scrape_careers import scrape_all_careers
from src.ingestion.scrape_websites import scrape_all_websites
from src.transform.clean_company_pages import clean_website_pages
from src.transform.clean_jobs import clean_jobs
from src.transform.clean_news import clean_news
from src.transform.feature_engineering import build_company_features
from src.transform.scoring import score_all_companies
from src.utils.logging_utils import get_logger

logger = get_logger("pipeline")


def run_pipeline(skip_network: bool = False) -> None:
    ensure_directories()
    initialize_database(DB_PATH, SQL_DIR / "ddl.sql", SQL_DIR / "views.sql")

    with get_connection(DB_PATH) as conn:
        seed_df = load_seed_companies(SEED_CSV)
        upserted = upsert_companies(conn, seed_df)
        logger.info("Upserted %s companies from seed", upserted)

        companies_df = pd.read_sql_query(
            "SELECT company_id, company_name, domain FROM companies ORDER BY company_id",
            conn,
        )

        if not skip_network:
            pages = scrape_all_websites(conn, companies_df, HTML_CACHE_DIR)
            logger.info("Scraped %s website pages", pages)

            roles = scrape_all_careers(conn, companies_df)
            logger.info("Scraped %s job posting rows", roles)

            news = fetch_all_news(conn, companies_df, NEWS_RAW_DIR)
            logger.info("Fetched %s news items", news)
        else:
            logger.info("Skipped network ingestion; using existing raw data")

        cleaned_pages = clean_website_pages(conn)
        cleaned_jobs = clean_jobs(conn)
        cleaned_news = clean_news(conn)
        logger.info(
            "Cleaned rows | pages=%s jobs=%s news=%s",
            cleaned_pages,
            cleaned_jobs,
            cleaned_news,
        )

        features = build_company_features(conn)
        scores = score_all_companies(conn)
        logger.info("Built features for %s companies and scores for %s companies", features, scores)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run PE alternative data screener pipeline")
    parser.add_argument(
        "--skip-network",
        action="store_true",
        help="Skip website/news/jobs fetch and only run transforms/scoring on existing data",
    )
    args = parser.parse_args()
    run_pipeline(skip_network=args.skip_network)


if __name__ == "__main__":
    main()
