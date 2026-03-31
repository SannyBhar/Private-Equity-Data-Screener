from __future__ import annotations

import streamlit as st

from src.app.data_access import list_companies, read_sql
from src.config import DB_PATH
from src.db.connection import get_connection
from src.llm.summarize_company import generate_screening_brief

st.set_page_config(page_title="Company Detail", layout="wide")
st.title("Company Detail")

companies_df = list_companies()
if companies_df.empty:
    st.warning("No companies loaded. Run `python run_pipeline.py` first.")
    st.stop()

company_name = st.selectbox("Select company", companies_df["company_name"].tolist())
company_row = companies_df[companies_df["company_name"] == company_name].iloc[0]
company_id = int(company_row["company_id"])

profile_df = read_sql(
    """
    SELECT c.company_name, c.domain, c.sector, c.sub_sector, c.headquarters,
           s.total_score, s.score_band, s.hiring_signal_score, s.news_signal_score,
           s.website_signal_score, s.completeness_score, s.risk_penalty_score
    FROM companies c
    LEFT JOIN screening_scores s ON c.company_id = s.company_id
    WHERE c.company_id = ?
    """,
    (company_id,),
)

feature_df = read_sql("SELECT * FROM company_features WHERE company_id = ?", (company_id,))
jobs_df = read_sql(
    "SELECT title, department, location, source_url, scraped_at FROM job_postings WHERE company_id = ? LIMIT 25",
    (company_id,),
)
news_df = read_sql(
    "SELECT published_at, source_name, title, url, sentiment_label, snippet FROM news_articles WHERE company_id = ? ORDER BY published_at DESC LIMIT 20",
    (company_id,),
)
pages_df = read_sql(
    "SELECT page_type, page_title, clean_text, word_count FROM website_pages_clean WHERE company_id = ? ORDER BY word_count DESC LIMIT 10",
    (company_id,),
)

st.subheader("Profile")
st.dataframe(profile_df, use_container_width=True, hide_index=True)

col1, col2, col3, col4 = st.columns(4)
if not feature_df.empty:
    feat = feature_df.iloc[0]
    col1.metric("Total Pages Scraped", int(feat["total_pages_scraped"]))
    col2.metric("Open Roles", int(feat["total_open_roles"]))
    col3.metric("News (30d)", int(feat["news_articles_30d"]))
    col4.metric("Keyword Coverage", f"{feat['keyword_coverage_score']:.1f}")

st.subheader("Latest Jobs")
st.dataframe(jobs_df, use_container_width=True, hide_index=True)

st.subheader("Recent News")
st.dataframe(news_df, use_container_width=True, hide_index=True)

st.subheader("Website Evidence Snippets")
for _, row in pages_df.iterrows():
    with st.expander(f"{row['page_type']} | {row['page_title'] or '(no title)'}"):
        st.write((row["clean_text"] or "")[:2000])

st.subheader("LLM Screening Brief")
latest_summary = read_sql(
    """
    SELECT summary_text, generated_at, model_name
    FROM llm_summaries
    WHERE company_id = ? AND summary_type = 'screening_brief'
    ORDER BY generated_at DESC
    LIMIT 1
    """,
    (company_id,),
)

if st.button("Generate / Refresh Brief"):
    with get_connection(DB_PATH) as conn:
        ok, message = generate_screening_brief(conn, company_id, company_name)
    if ok:
        st.success("Generated screening brief.")
    else:
        st.warning(message)
    st.rerun()

if not latest_summary.empty:
    row = latest_summary.iloc[0]
    st.caption(f"Model: {row['model_name']} | Generated: {row['generated_at']}")
    st.markdown(row["summary_text"])
else:
    st.info("No saved summary yet. Click 'Generate / Refresh Brief'.")

with st.expander("Evidence Panel"):
    st.markdown("Structured features")
    st.dataframe(feature_df, use_container_width=True, hide_index=True)
    st.markdown("Score row")
    st.dataframe(profile_df[[
        "total_score", "score_band", "hiring_signal_score", "news_signal_score", "website_signal_score", "completeness_score", "risk_penalty_score"
    ]], use_container_width=True, hide_index=True)
