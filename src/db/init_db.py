from __future__ import annotations

from pathlib import Path

from src.db.connection import get_connection


def run_sql_file(db_path: Path, sql_path: Path) -> None:
    sql_text = sql_path.read_text(encoding="utf-8")
    with get_connection(db_path) as conn:
        conn.executescript(sql_text)


def initialize_database(db_path: Path, ddl_path: Path, views_path: Path) -> None:
    run_sql_file(db_path, ddl_path)
    run_sql_file(db_path, views_path)
