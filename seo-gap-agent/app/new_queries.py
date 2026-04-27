from __future__ import annotations

import sqlite3

import pandas as pd


def mark_new_queries(
    conn: sqlite3.Connection,
    current_df: pd.DataFrame,
    fetched_at: str,
) -> pd.DataFrame:
    """
    Mark queries that have not appeared in historical query_page_metrics rows
    before the current run timestamp.
    """
    if current_df.empty:
        with_flags = current_df.copy()
        with_flags["is_new_query"] = False
        return with_flags

    historical_rows = conn.execute(
        """
        SELECT DISTINCT query
        FROM query_page_metrics
        WHERE fetched_at < ?
        """,
        (fetched_at,),
    ).fetchall()
    historical_queries = {str(row["query"]).strip().lower() for row in historical_rows if row["query"]}

    with_flags = current_df.copy()
    with_flags["is_new_query"] = ~with_flags["query"].astype(str).str.strip().str.lower().isin(historical_queries)
    return with_flags
