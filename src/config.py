from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
HTML_CACHE_DIR = RAW_DIR / "html_cache"
NEWS_RAW_DIR = RAW_DIR / "news_raw"
PROCESSED_DIR = DATA_DIR / "processed"
SQLITE_DIR = DATA_DIR / "sqlite"
DB_PATH = SQLITE_DIR / "pe_screener.db"
SQL_DIR = ROOT_DIR / "sql"

SEED_CSV = RAW_DIR / "companies_seed.csv"

REQUEST_TIMEOUT_SECONDS = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "12"))
USER_AGENT = os.getenv("USER_AGENT", "PE-Alt-Data-Screener/1.0 (+local-demo)")

LLM_SUMMARIZATION_ENABLED = os.getenv("LLM_SUMMARIZATION_ENABLED", "true").lower() == "true"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

KEYWORDS = {
    "ai": ["ai", "artificial intelligence", "machine learning", "llm"],
    "enterprise": ["enterprise", "b2b", "workflow", "platform", "scale"],
    "automation": ["automation", "automate", "orchestration", "rpa"],
    "security": ["security", "compliance", "identity", "risk", "zero trust"],
    "healthcare": ["healthcare", "clinical", "patient", "payer", "provider"],
}

PAGE_PATHS = {
    "home": "/",
    "about": "/about",
    "company": "/company",
    "product": "/product",
    "platform": "/platform",
    "solutions": "/solutions",
}

CAREER_PATHS = ["/careers", "/jobs"]
ATS_HOST_HINTS = ["lever.co", "greenhouse.io", "ashbyhq.com"]


def ensure_directories() -> None:
    for path in [HTML_CACHE_DIR, NEWS_RAW_DIR, PROCESSED_DIR, SQLITE_DIR]:
        path.mkdir(parents=True, exist_ok=True)
