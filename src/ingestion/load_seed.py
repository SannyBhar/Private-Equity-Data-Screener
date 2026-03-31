from __future__ import annotations

import pandas as pd

from src.utils.text_cleaning import normalize_company_name
from src.utils.url_utils import normalize_domain


def load_seed_companies(seed_csv_path) -> pd.DataFrame:
    df = pd.read_csv(seed_csv_path)
    df["company_name"] = df["company_name"].astype(str).map(normalize_company_name)
    df["domain"] = df["domain"].astype(str).map(normalize_domain)
    return df


def upsert_companies(conn, companies_df: pd.DataFrame) -> int:
    rows = companies_df.to_dict(orient="records")
    for row in rows:
        conn.execute(
            """
            INSERT INTO companies (company_name, domain, sector, sub_sector, headquarters, source_type)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(domain) DO UPDATE SET
                company_name = excluded.company_name,
                sector = excluded.sector,
                sub_sector = excluded.sub_sector,
                headquarters = excluded.headquarters,
                source_type = excluded.source_type
            """,
            (
                row["company_name"],
                row["domain"],
                row.get("sector"),
                row.get("sub_sector"),
                row.get("headquarters"),
                row.get("source_type", "seed"),
            ),
        )
    conn.commit()
    return len(rows)
