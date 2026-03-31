from __future__ import annotations

import json

import requests

from src.config import LLM_SUMMARIZATION_ENABLED, OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL
from src.llm.prompts import PROMPT_VERSION, screening_brief_prompt
from src.utils.date_utils import utc_now_iso
from src.utils.text_cleaning import clipped


def build_company_evidence(conn, company_id: int) -> str:
    feature = conn.execute("SELECT * FROM company_features WHERE company_id = ?", (company_id,)).fetchone()
    score = conn.execute("SELECT * FROM screening_scores WHERE company_id = ?", (company_id,)).fetchone()

    page_rows = conn.execute(
        "SELECT page_type, clean_text FROM website_pages_clean WHERE company_id = ? ORDER BY word_count DESC LIMIT 3",
        (company_id,),
    ).fetchall()
    job_rows = conn.execute(
        "SELECT title, department FROM job_postings WHERE company_id = ? LIMIT 8",
        (company_id,),
    ).fetchall()
    news_rows = conn.execute(
        "SELECT title, snippet, published_at FROM news_articles WHERE company_id = ? ORDER BY published_at DESC LIMIT 6",
        (company_id,),
    ).fetchall()

    parts: list[str] = ["Structured metrics:"]
    if feature:
        parts.append(
            json.dumps(
                {
                    "total_pages_scraped": feature["total_pages_scraped"],
                    "total_words_scraped": feature["total_words_scraped"],
                    "total_open_roles": feature["total_open_roles"],
                    "engineering_roles": feature["engineering_roles"],
                    "go_to_market_roles": feature["go_to_market_roles"],
                    "news_articles_30d": feature["news_articles_30d"],
                    "news_articles_90d": feature["news_articles_90d"],
                    "keyword_coverage_score": feature["keyword_coverage_score"],
                    "data_completeness_score": feature["data_completeness_score"],
                },
                ensure_ascii=True,
            )
        )
    if score:
        parts.append(
            json.dumps(
                {
                    "total_score": score["total_score"],
                    "score_band": score["score_band"],
                    "hiring_signal_score": score["hiring_signal_score"],
                    "news_signal_score": score["news_signal_score"],
                    "website_signal_score": score["website_signal_score"],
                },
                ensure_ascii=True,
            )
        )

    parts.append("Website snippets:")
    for r in page_rows:
        parts.append(f"- [{r['page_type']}] {clipped(r['clean_text'] or '', 700)}")

    parts.append("Recent jobs:")
    for r in job_rows:
        parts.append(f"- {r['title']} ({r['department']})")

    parts.append("Recent news:")
    for r in news_rows:
        parts.append(f"- {r['published_at']}: {r['title']} | {clipped(r['snippet'] or '', 240)}")

    return "\n".join(parts)


def _call_llm(prompt: str) -> str:
    url = f"{OPENAI_BASE_URL.rstrip('/')}/chat/completions"
    response = requests.post(
        url,
        timeout=30,
        headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"},
        json={
            "model": OPENAI_MODEL,
            "messages": [
                {"role": "system", "content": "You write concise, evidence-grounded investment screening notes."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
        },
    )
    response.raise_for_status()
    payload = response.json()
    return payload["choices"][0]["message"]["content"].strip()


def generate_screening_brief(conn, company_id: int, company_name: str) -> tuple[bool, str]:
    evidence = build_company_evidence(conn, company_id)

    if not LLM_SUMMARIZATION_ENABLED or not OPENAI_API_KEY:
        message = (
            "LLM summarization is disabled or API key is missing. "
            "Set OPENAI_API_KEY and LLM_SUMMARIZATION_ENABLED=true in your .env to enable."
        )
        return False, message

    prompt = screening_brief_prompt(company_name, evidence)
    try:
        summary_text = _call_llm(prompt)
    except Exception as exc:
        return False, f"Failed to generate summary: {exc}"

    conn.execute(
        """
        INSERT INTO llm_summaries (
            company_id, summary_type, model_name, prompt_version, summary_text, evidence_text, generated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (company_id, "screening_brief", OPENAI_MODEL, PROMPT_VERSION, summary_text, evidence, utc_now_iso()),
    )
    conn.commit()
    return True, summary_text
