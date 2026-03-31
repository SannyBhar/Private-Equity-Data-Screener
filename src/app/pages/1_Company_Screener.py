from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src.app.data_access import read_sql

st.set_page_config(page_title="Company Screener", layout="wide")
st.title("Company Screener")

screen_df = read_sql("SELECT * FROM vw_company_screen ORDER BY total_score DESC")

if screen_df.empty:
    st.warning("No screening data available. Run `python run_pipeline.py` first.")
    st.stop()

sector_options = sorted(screen_df["sector"].dropna().unique().tolist())
band_options = sorted(screen_df["score_band"].dropna().unique().tolist())

c1, c2, c3, c4 = st.columns(4)
with c1:
    selected_sector = st.multiselect("Sector", sector_options, default=sector_options)
with c2:
    selected_band = st.multiselect("Score Band", band_options, default=band_options)
with c3:
    min_jobs = st.number_input("Min Open Roles", min_value=0, max_value=300, value=0, step=1)
with c4:
    min_news = st.number_input("Min News (30d)", min_value=0, max_value=100, value=0, step=1)

filtered = screen_df[
    (screen_df["sector"].isin(selected_sector))
    & (screen_df["score_band"].isin(selected_band))
    & (screen_df["total_open_roles"] >= min_jobs)
    & (screen_df["news_articles_30d"] >= min_news)
].copy()

filtered = filtered.sort_values("total_score", ascending=False)

st.subheader("Screening Table")
st.dataframe(filtered, use_container_width=True, hide_index=True)

csv_bytes = filtered.to_csv(index=False).encode("utf-8")
st.download_button("Export Filtered CSV", data=csv_bytes, file_name="company_screener_export.csv", mime="text/csv")

left, right = st.columns(2)
with left:
    st.subheader("Top Total Scores")
    top_df = filtered.head(10)
    fig = px.bar(top_df, x="company_name", y="total_score", color="score_band")
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Open Roles Distribution")
    fig2 = px.histogram(filtered, x="total_open_roles", nbins=20)
    st.plotly_chart(fig2, use_container_width=True)

st.subheader("News vs Hiring")
scatter = px.scatter(
    filtered,
    x="news_articles_30d",
    y="total_open_roles",
    color="score_band",
    size="total_score",
    hover_data=["company_name", "total_score"],
)
st.plotly_chart(scatter, use_container_width=True)
