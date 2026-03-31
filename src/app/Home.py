from __future__ import annotations

import streamlit as st

st.set_page_config(page_title="Private Equity Alternative Data Screener", layout="wide")

st.title("Private Equity Alternative Data Screener")
st.markdown(
    """
This app simulates a private equity investment insights workflow that combines:
- public alternative data scraping (website, careers, news)
- SQL-backed feature engineering in SQLite
- transparent heuristic screening scores
- optional LLM-grounded screening brief generation

Use the sidebar to open:
- `1_Company_Screener`
- `2_Company_Detail`
- `3_Methodology`
"""
)

st.info(
    "Run `python run_pipeline.py` before using the dashboard so the SQLite tables are populated."
)
