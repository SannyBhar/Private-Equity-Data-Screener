from __future__ import annotations

import pandas as pd

from src.config import DB_PATH
from src.db.connection import get_connection


def read_sql(query: str, params: tuple | None = None) -> pd.DataFrame:
    with get_connection(DB_PATH) as conn:
        return pd.read_sql_query(query, conn, params=params or ())


def list_companies() -> pd.DataFrame:
    return read_sql("SELECT company_id, company_name FROM companies ORDER BY company_name")
