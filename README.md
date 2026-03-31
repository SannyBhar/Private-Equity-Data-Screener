# Private Equity Alternative Data Screener

A recruiter-ready analytics MVP that simulates how a private equity investment insights team can use **public alternative data**, **SQL analytics**, and **LLM-assisted synthesis** to prioritize B2B SaaS companies for exploratory diligence.

## Project Overview
This project ingests and standardizes three evidence streams for 15-20 seed companies:
- company website content (structured scraping of key pages)
- hiring signal proxies from careers/job pages
- recent news activity from public RSS

It materializes cleaned data in SQLite, computes company-level features and explainable heuristic scores, and exposes an interactive Streamlit interface for screening and drill-down.

## PE Workflow Framing
This MVP is intentionally scoped as a **screening support tool**, not an investment decision engine.

Typical analyst workflow:
1. Start with a predefined universe of B2B SaaS companies.
2. Pull lightweight public signals (web, hiring, news).
3. Standardize messy text and timestamps.
4. Aggregate features in SQL tables/views.
5. Rank names by transparent screening heuristics.
6. Generate an evidence-grounded short brief for discussion.

## Architecture (Text Diagram)
```text
seed CSV (companies)
   -> ingestion: websites + careers + news (requests/bs4/rss)
   -> raw SQLite tables + local cache files
   -> cleaning/normalization transforms
   -> feature engineering (company_features)
   -> heuristic scoring (screening_scores)
   -> SQL views (vw_company_screen, vw_jobs_latest, vw_news_latest)
   -> Streamlit dashboard (screener, detail, methodology)
   -> optional LLM screening brief saved in llm_summaries
```

## Folder Structure
```text
.
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── run_pipeline.py
├── data/
│   ├── raw/
│   │   ├── companies_seed.csv
│   │   ├── html_cache/
│   │   └── news_raw/
│   ├── processed/
│   └── sqlite/
│       └── pe_screener.db
├── sql/
│   ├── ddl.sql
│   ├── views.sql
│   └── analytics_queries.sql
├── src/
│   ├── config.py
│   ├── utils/
│   ├── db/
│   ├── ingestion/
│   ├── transform/
│   ├── llm/
│   └── app/
│       ├── Home.py
│       └── pages/
└── tests/
```

## Data Sources
- **Seed universe**: `data/raw/companies_seed.csv`
- **Web pages**: company-owned public pages (`/`, `/about`, `/company`, `/product`, `/platform`, `/solutions`)
- **Careers/jobs**: common careers routes + linked ATS URLs when detectable
- **News**: Google News RSS (public feed)

## Database Schema
Core tables:
- `companies`
- `website_pages_raw`
- `website_pages_clean`
- `job_postings`
- `news_articles`
- `company_features`
- `screening_scores`
- `llm_summaries`

See full definitions in `sql/ddl.sql`, with analyst-facing views in `sql/views.sql`.

## Pipeline Flow
`run_pipeline.py` executes:
1. Initialize DB schema and views.
2. Load and upsert seed companies.
3. Scrape website pages.
4. Scrape careers/jobs signals.
5. Fetch news RSS items.
6. Clean text and normalize dates.
7. Engineer company-level features.
8. Compute and persist screening scores.

Useful mode:
- `--skip-network`: recompute transforms/scores from existing raw data only.

## Scoring Methodology
Total score out of 100:
- Hiring signal (30): careers presence, open-role volume, eng/GTM mix
- News signal (20): recency/activity in 30d and 90d
- Website signal (30): page coverage + keyword coverage
- Data completeness (10): sufficient evidence across sources
- Risk penalties (-10 max): sparse website data, no jobs, no news

The score is a **screening prioritization heuristic** for exploratory underwriting support.

## Streamlit Walkthrough
Pages:
1. **Company Screener**
- sortable/filterable table
- filters (sector, score band, min jobs, min news)
- CSV export
- top-score chart, jobs histogram, news-vs-hiring scatter

2. **Company Detail**
- profile and score breakdown
- latest jobs, recent news, website snippets
- optional LLM screening brief generator
- expandable evidence panel

3. **Methodology**
- sources, scoring logic, limitations, PE relevance

## LLM Feature (Optional)
The screening brief generator is evidence-grounded:
- uses only stored snippets and structured metrics
- explicitly handles missing evidence
- saves outputs to `llm_summaries`

If no API key is set, the app shows a graceful fallback message.

## Setup and Run
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Run pipeline:
```bash
python run_pipeline.py
```

If you want to recompute without fetching fresh network data:
```bash
python run_pipeline.py --skip-network
```

Launch app:
```bash
streamlit run src/app/Home.py
```

Run tests:
```bash
pytest -q
```

## Limitations
- Public web extraction can be noisy and inconsistent.
- Careers parsing is heuristic and not ATS API-grade.
- RSS query matching may include partial/irrelevant headlines.
- This is local MVP scope; not production data infrastructure.

## Future Improvements
- Better ATS-specific adapters (Lever/Greenhouse/Ashby parsing)
- More robust boilerplate removal and snippet ranking
- Configurable scoring weights in UI
- Historical snapshots for trend deltas
- Optional richer sentiment classifier over news snippets

## Resume-Ready Bullets
- Built an end-to-end private equity alternative-data screener using Python, SQL, and Streamlit over 15-20 B2B SaaS companies.
- Designed SQLite schema and SQL views to standardize raw web/careers/news data into analyst-ready screening features.
- Implemented explainable heuristic scoring (0-100) for hiring, news, website maturity, completeness, and risk penalties.
- Added an LLM-assisted, evidence-grounded screening brief generator with persisted outputs and graceful fallback when API keys are missing.

## Interview Talking Points
- Why deterministic heuristics are useful before predictive modeling.
- How to balance scraping ambition with reliability and legal/public constraints.
- Tradeoffs between signal coverage and data quality in early-stage diligence tooling.
- How SQL views and modular ETL design support iteration and auditability.
