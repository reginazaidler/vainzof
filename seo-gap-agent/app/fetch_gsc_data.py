from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

import pandas as pd

from app.gsc_client import GSCClient


@dataclass
class GSCFetchParams:
    start_date: str
    end_date: str
    max_rows: int = 50_000
    page_size: int = 25_000


def fetch_gsc_data(client: GSCClient, params: GSCFetchParams) -> pd.DataFrame:
    fetched_rows: list[dict[str, object]] = []
    start_row = 0

    while start_row < params.max_rows:
        rows = client.query_search_analytics(
            start_date=params.start_date,
            end_date=params.end_date,
            row_limit=min(params.page_size, params.max_rows - start_row),
            start_row=start_row,
        )

        if not rows:
            break

        for row in rows:
            keys = row.get("keys", ["", ""])
            fetched_rows.append(
                {
                    "query": keys[0],
                    "page": keys[1],
                    "clicks": float(row.get("clicks", 0.0)),
                    "impressions": float(row.get("impressions", 0.0)),
                    "ctr": float(row.get("ctr", 0.0)),
                    "position": float(row.get("position", 0.0)),
                }
            )

        start_row += len(rows)
        if len(rows) < min(params.page_size, params.max_rows - (start_row - len(rows))):
            break

    df = pd.DataFrame(fetched_rows)
    if df.empty:
        return df

    fetched_at = datetime.now(timezone.utc).isoformat()
    df["start_date"] = params.start_date
    df["end_date"] = params.end_date
    df["fetched_at"] = fetched_at
    return df
