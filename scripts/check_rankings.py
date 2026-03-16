#!/usr/bin/env python3
"""Daily Search Console rank tracker for configured queries."""

from __future__ import annotations

import argparse
import csv
import json
import logging
import os
import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from math import floor
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


LOGGER = logging.getLogger("gsc_rank_tracker")
ISRAEL_TZ = ZoneInfo("Asia/Jerusalem")
SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]
HISTORY_COLUMNS = [
    "date",
    "checked_at_utc",
    "checked_at_israel",
    "site",
    "query",
    "country",
    "device",
    "clicks",
    "impressions",
    "ctr",
    "avg_position",
    "estimated_google_page",
    "previous_avg_position",
    "position_change_vs_previous",
]


@dataclass
class Config:
    site_url: str
    country: str
    device: str
    queries: list[str]


@dataclass
class QueryResult:
    date: str
    checked_at_utc: str
    checked_at_israel: str
    site: str
    query: str
    country: str
    device: str
    clicks: int
    impressions: int
    ctr: str
    avg_position: str
    estimated_google_page: str
    previous_avg_position: str
    position_change_vs_previous: str

    def as_dict(self) -> dict[str, str | int]:
        return {
            "date": self.date,
            "checked_at_utc": self.checked_at_utc,
            "checked_at_israel": self.checked_at_israel,
            "site": self.site,
            "query": self.query,
            "country": self.country,
            "device": self.device,
            "clicks": self.clicks,
            "impressions": self.impressions,
            "ctr": self.ctr,
            "avg_position": self.avg_position,
            "estimated_google_page": self.estimated_google_page,
            "previous_avg_position": self.previous_avg_position,
            "position_change_vs_previous": self.position_change_vs_previous,
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check daily Search Console ranks")
    parser.add_argument("--config", default="config/queries.json", help="Path to query config JSON")
    parser.add_argument("--output-dir", default="output", help="Directory for generated reports")
    parser.add_argument(
        "--target-hour",
        type=int,
        default=5,
        help="Required local hour in Asia/Jerusalem for scheduled execution",
    )
    parser.add_argument(
        "--force-run",
        action="store_true",
        default=os.getenv("FORCE_RUN", "false").lower() in {"1", "true", "yes"},
        help="Ignore local-hour guard and run immediately",
    )
    return parser.parse_args()


def setup_logging() -> None:
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO").upper(),
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )


def load_config(path: Path) -> Config:
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with path.open("r", encoding="utf-8") as config_file:
        raw = json.load(config_file)

    required_keys = {"site_url", "country", "device", "queries"}
    missing_keys = sorted(required_keys - raw.keys())
    if missing_keys:
        raise ValueError(f"Missing required config key(s): {', '.join(missing_keys)}")

    queries = raw["queries"]
    if not isinstance(queries, list) or not queries:
        raise ValueError("config.queries must be a non-empty list")

    return Config(
        site_url=str(raw["site_url"]),
        country=str(raw["country"]).upper(),
        device=str(raw["device"]).lower(),
        queries=[str(q) for q in queries],
    )


def should_run_now(target_hour: int, force_run: bool) -> bool:
    now_il = datetime.now(ISRAEL_TZ)
    if force_run:
        LOGGER.info("FORCE_RUN enabled, bypassing local-hour guard (current Israel time: %s)", now_il.isoformat())
        return True

    if now_il.hour != target_hour:
        LOGGER.info(
            "Skipping run: local Israel hour is %s, target is %s. Exiting successfully.",
            now_il.hour,
            target_hour,
        )
        return False

    return True


def load_credentials() -> service_account.Credentials:
    credential_json = os.getenv("GSC_SERVICE_ACCOUNT_JSON")
    if not credential_json:
        raise RuntimeError(
            "Missing credentials: set GSC_SERVICE_ACCOUNT_JSON with full service account JSON."
        )

    try:
        info = json.loads(credential_json)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Invalid GSC_SERVICE_ACCOUNT_JSON: must be valid JSON") from exc

    try:
        creds = service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError("Could not create credentials from GSC_SERVICE_ACCOUNT_JSON") from exc

    return creds


def build_service(creds: service_account.Credentials) -> Any:
    return build("searchconsole", "v1", credentials=creds, cache_discovery=False)


def build_request_body(target_date: date, query: str, country: str, device: str) -> dict[str, Any]:
    filters = [
        {"dimension": "query", "operator": "equals", "expression": query},
        {"dimension": "country", "operator": "equals", "expression": country},
    ]
    if device != "all":
        filters.append({"dimension": "device", "operator": "equals", "expression": device.upper()})

    return {
        "startDate": target_date.isoformat(),
        "endDate": target_date.isoformat(),
        "dimensionFilterGroups": [{"groupType": "and", "filters": filters}],
        "rowLimit": 1,
    }


def fetch_query_metrics(
    service: Any,
    site_url: str,
    target_date: date,
    query: str,
    country: str,
    device: str,
) -> dict[str, float | int | None]:
    request = build_request_body(target_date, query, country, device)
    response = service.searchanalytics().query(siteUrl=site_url, body=request).execute()

    rows = response.get("rows", [])
    if not rows:
        return {"clicks": 0, "impressions": 0, "ctr": 0.0, "position": None}

    row = rows[0]
    return {
        "clicks": int(row.get("clicks", 0)),
        "impressions": int(row.get("impressions", 0)),
        "ctr": float(row.get("ctr", 0.0)),
        "position": float(row.get("position")) if row.get("position") is not None else None,
    }


def parse_float(value: str) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def read_history(history_path: Path) -> list[dict[str, str]]:
    if not history_path.exists():
        return []

    with history_path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        return [dict(row) for row in reader]


def previous_position_for_query(history: list[dict[str, str]], query: str) -> float | None:
    candidates = [
        row
        for row in history
        if row.get("query") == query and parse_float(row.get("avg_position")) is not None
    ]
    if not candidates:
        return None

    candidates.sort(key=lambda row: (row.get("date", ""), row.get("checked_at_utc", "")))
    return parse_float(candidates[-1].get("avg_position", ""))


def format_optional_float(value: float | None, digits: int = 2) -> str:
    if value is None:
        return ""
    return f"{value:.{digits}f}"


def calculate_estimated_page(avg_position: float | None) -> str:
    if avg_position is None:
        return ""
    return str(floor((avg_position - 1) / 10) + 1)


def build_results(
    config: Config,
    service: Any,
    target_date: date,
    history: list[dict[str, str]],
) -> list[QueryResult]:
    now_utc = datetime.now(timezone.utc)
    now_il = now_utc.astimezone(ISRAEL_TZ)

    results: list[QueryResult] = []
    for query in config.queries:
        metrics = fetch_query_metrics(
            service=service,
            site_url=config.site_url,
            target_date=target_date,
            query=query,
            country=config.country,
            device=config.device,
        )

        avg_position = metrics["position"]
        prev_position = previous_position_for_query(history, query)
        change = None
        if prev_position is not None and avg_position is not None:
            change = prev_position - avg_position

        result = QueryResult(
            date=target_date.isoformat(),
            checked_at_utc=now_utc.replace(microsecond=0).isoformat(),
            checked_at_israel=now_il.replace(microsecond=0).isoformat(),
            site=config.site_url,
            query=query,
            country=config.country,
            device=config.device,
            clicks=int(metrics["clicks"]),
            impressions=int(metrics["impressions"]),
            ctr=format_optional_float(float(metrics["ctr"]), 4),
            avg_position=format_optional_float(avg_position, 2),
            estimated_google_page=calculate_estimated_page(avg_position),
            previous_avg_position=format_optional_float(prev_position, 2),
            position_change_vs_previous=format_optional_float(change, 2),
        )
        results.append(result)

    return results


def write_csv(path: Path, rows: list[dict[str, str | int]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def merge_history(existing_rows: list[dict[str, str]], new_rows: list[QueryResult]) -> list[dict[str, str | int]]:
    keys_to_replace = {
        (row.date, row.site, row.query, row.country, row.device)
        for row in new_rows
    }

    filtered_existing = [
        row
        for row in existing_rows
        if (
            row.get("date", ""),
            row.get("site", ""),
            row.get("query", ""),
            row.get("country", ""),
            row.get("device", ""),
        )
        not in keys_to_replace
    ]

    merged: list[dict[str, str | int]] = filtered_existing + [row.as_dict() for row in new_rows]
    merged.sort(key=lambda row: (row["date"], row["query"]))
    return merged


def write_daily_summary(path: Path, results: list[QueryResult]) -> None:
    lines = [
        "# Daily SEO Rank Summary",
        "",
        "| Query | Clicks | Impressions | CTR | Avg Position | Est. Google Page | Change vs Previous |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]

    for row in results:
        lines.append(
            "| {query} | {clicks} | {impressions} | {ctr} | {avg_position} | {estimated_google_page} | {position_change_vs_previous} |".format(
                query=row.query,
                clicks=row.clicks,
                impressions=row.impressions,
                ctr=row.ctr or "",
                avg_position=row.avg_position or "",
                estimated_google_page=row.estimated_google_page or "",
                position_change_vs_previous=row.position_change_vs_previous or "",
            )
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def print_console_summary(results: list[QueryResult]) -> None:
    LOGGER.info("Daily results summary (%d queries):", len(results))
    for row in results:
        LOGGER.info(
            "query='%s' clicks=%s impressions=%s ctr=%s avg_position=%s page=%s delta=%s",
            row.query,
            row.clicks,
            row.impressions,
            row.ctr,
            row.avg_position or "-",
            row.estimated_google_page or "-",
            row.position_change_vs_previous or "-",
        )


def main() -> int:
    setup_logging()
    args = parse_args()

    if not should_run_now(target_hour=args.target_hour, force_run=args.force_run):
        return 0

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        config = load_config(Path(args.config))
        credentials = load_credentials()
        service = build_service(credentials)
    except Exception as exc:  # noqa: BLE001
        LOGGER.error("Startup failure: %s", exc)
        return 1

    target_date = datetime.now(timezone.utc).date() - timedelta(days=1)
    history_path = output_dir / "rank_history.csv"
    daily_path = output_dir / f"rankings_{target_date.isoformat()}.csv"
    summary_path = output_dir / "daily_summary.md"

    existing_history = read_history(history_path)

    try:
        results = build_results(
            config=config,
            service=service,
            target_date=target_date,
            history=existing_history,
        )
    except HttpError as exc:
        LOGGER.error(
            "Search Console API call failed. Ensure the service account has access to '%s'. Error: %s",
            config.site_url,
            exc,
        )
        return 1
    except Exception as exc:  # noqa: BLE001
        LOGGER.error("Unexpected error while fetching rankings: %s", exc)
        return 1

    daily_rows = [row.as_dict() for row in results]
    merged_history = merge_history(existing_history, results)

    write_csv(daily_path, daily_rows, HISTORY_COLUMNS)
    write_csv(history_path, merged_history, HISTORY_COLUMNS)
    write_daily_summary(summary_path, results)
    print_console_summary(results)

    LOGGER.info("Saved daily snapshot: %s", daily_path)
    LOGGER.info("Saved cumulative history: %s", history_path)
    LOGGER.info("Saved markdown summary: %s", summary_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
