from __future__ import annotations

from typing import Iterable

import pandas as pd


def replace_table(conn, table_name: str, df: pd.DataFrame) -> None:
    df.to_sql(table_name, conn, if_exists="replace", index=False)


def append_rows(conn, table_name: str, rows: Iterable[dict]) -> None:
    rows = list(rows)
    if not rows:
        return
    pd.DataFrame(rows).to_sql(table_name, conn, if_exists="append", index=False)
