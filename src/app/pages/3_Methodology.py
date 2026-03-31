from __future__ import annotations

import streamlit as st

st.set_page_config(page_title="Methodology", layout="wide")
st.title("Methodology")

st.header("Data Sources")
st.markdown(
    """
- Seed universe: curated `companies_seed.csv` (15-20 B2B SaaS companies)
- Website pages: company public pages (`/`, `/about`, `/company`, `/product`, `/platform`, `/solutions`)
- Careers signals: public `careers/jobs` pages and linked ATS pages where visible
- News signals: Google News RSS search by company name
"""
)

st.header("Scoring Logic (Heuristic, Explainable)")
st.markdown(
    """
Total score out of 100:
- Hiring signal (30): careers presence, role count, engineering + GTM mix
- News signal (20): 30-day and 90-day activity
- Website/commercial signal (30): page coverage + keyword coverage
- Data completeness (10): pages, words, jobs, news coverage sufficiency
- Risk penalty (-10 max): sparse/noisy evidence

This is not an investment recommendation. It is a screening prioritization heuristic for exploratory diligence.
"""
)

st.header("Why This Is Relevant to PE Screening")
st.markdown(
    """
- Demonstrates structured + unstructured alternative data ingestion
- Uses SQL + Python transformations for evidence standardization
- Produces transparent, interview-defensible scoring
- Adds practical LLM summarization constrained to stored evidence
"""
)

st.header("Limitations")
st.markdown(
    """
- Public web content can be incomplete or inconsistent
- News source is intentionally simple and may include irrelevant matches
- Careers parsing is heuristic and not ATS-API grade
- Intended for local MVP and educational use
"""
)
