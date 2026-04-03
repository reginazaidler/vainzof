from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Iterable


def get_connection(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS query_page_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT NOT NULL,
            page TEXT NOT NULL,
            clicks REAL NOT NULL,
            impressions REAL NOT NULL,
            ctr REAL NOT NULL,
            position REAL NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            fetched_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS opportunities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT NOT NULL,
            page TEXT NOT NULL,
            clicks REAL NOT NULL,
            impressions REAL NOT NULL,
            ctr REAL NOT NULL,
            position REAL NOT NULL,
            expected_ctr REAL NOT NULL,
            opportunity_score REAL NOT NULL,
            selected_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS page_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            page TEXT NOT NULL,
            title TEXT,
            meta_description TEXT,
            h1 TEXT,
            h2s_json TEXT,
            main_content TEXT,
            html_fetched_at TEXT NOT NULL
        );
        """
    )
    conn.commit()


def bulk_insert(
    conn: sqlite3.Connection,
    sql: str,
    rows: Iterable[tuple[Any, ...]],
) -> None:
    conn.executemany(sql, rows)
    conn.commit()
