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
    parser.add_argument("--target-hour", type=int, default=5, help="Required local hour in Asia/Jerusalem")
    parser.add_argument(
        "--force-run",
        action="store_true",
        default=os.getenv("FORCE_RUN", "false").lower() in {"1", "true", "yes"},
        help="Ignore local-hour guard and run immediately",
    )
    parser.add_argument(
        "--demo-run",
        action="store_true",
        default=os.getenv("DEMO_RUN", "false").lower() in {"1", "true", "yes"},
        help="Generate local bootstrap output without calling Google API (for environment-limited tests)",
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
    with path.open("r", encoding="utf-8") as f:
        raw = json.load(f)

    required_keys = {"site_url", "country", "device", "queries"}
    missing = sorted(required_keys - raw.keys())
    if missing:
        raise ValueError(f"Missing required config key(s): {', '.join(missing)}")
    if not isinstance(raw["queries"], list) or not raw["queries"]:
        raise ValueError("config.queries must be a non-empty list")

    return Config(
        site_url=str(raw["site_url"]),
        country=str(raw["country"]).upper(),
        device=str(raw["device"]).lower(),
        queries=[str(q) for q in raw["queries"]],
    )


def should_run_now(target_hour: int, force_run: bool) -> bool:
    now_il = datetime.now(ISRAEL_TZ)
    if force_run:
        LOGGER.info("FORCE_RUN enabled (current Israel time: %s)", now_il.isoformat())
        return True
    if now_il.hour != target_hour:
        LOGGER.info("Skipping run: local Israel hour is %s, target is %s", now_il.hour, target_hour)
        return False
    return True


def load_credentials() -> Any:
    credential_json = os.getenv("GSC_SERVICE_ACCOUNT_JSON")
    if not credential_json:
        raise RuntimeError("Missing credentials: set GSC_SERVICE_ACCOUNT_JSON with full service account JSON.")

    try:
        info = json.loads(credential_json)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Invalid GSC_SERVICE_ACCOUNT_JSON: must be valid JSON") from exc

    try:
        from google.oauth2 import service_account

        return service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError("Could not create credentials from GSC_SERVICE_ACCOUNT_JSON") from exc


def build_service(creds: Any) -> Any:
    try:
        from googleapiclient.discovery import build
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError("google-api-python-client is missing. Install requirements.txt first.") from exc
    return build("searchconsole", "v1", credentials=creds, cache_discovery=False)


def build_request_body(target_date: date, query: str, country: str, device: str) -> dict[str, Any]:
    filters: list[dict[str, str]] = [
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


def fetch_query_metrics(service: Any, site_url: str, target_date: date, query: str, country: str, device: str) -> dict[str, float | int | None]:
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
        "position": float(row["position"]) if row.get("position") is not None else None,
    }


def parse_float(value: str | None) -> float | None:
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def read_history(history_path: Path) -> list[dict[str, str]]:
    if not history_path.exists():
        return []
    with history_path.open("r", encoding="utf-8", newline="") as f:
        return [dict(row) for row in csv.DictReader(f)]


def previous_position_for_query(history: list[dict[str, str]], query: str) -> float | None:
    candidates = [r for r in history if r.get("query") == query and parse_float(r.get("avg_position")) is not None]
    if not candidates:
        return None
    candidates.sort(key=lambda r: (r.get("date", ""), r.get("checked_at_utc", "")))
    return parse_float(candidates[-1].get("avg_position"))


def fmt_float(value: float | None, digits: int = 2) -> str:
    return "" if value is None else f"{value:.{digits}f}"


def estimated_page(avg_position: float | None) -> str:
    return "" if avg_position is None else str(floor((avg_position - 1) / 10) + 1)


def build_results(config: Config, target_date: date, history: list[dict[str, str]], service: Any | None, demo_run: bool) -> list[QueryResult]:
    now_utc = datetime.now(timezone.utc).replace(microsecond=0)
    now_il = now_utc.astimezone(ISRAEL_TZ)

    results: list[QueryResult] = []
    for query in config.queries:
        if demo_run:
            metrics = {"clicks": 0, "impressions": 0, "ctr": 0.0, "position": None}
        else:
            metrics = fetch_query_metrics(service, config.site_url, target_date, query, config.country, config.device)

        current_pos = metrics["position"]
        prev_pos = previous_position_for_query(history, query)
        delta = (prev_pos - current_pos) if (prev_pos is not None and current_pos is not None) else None

        results.append(
            QueryResult(
                date=target_date.isoformat(),
                checked_at_utc=now_utc.isoformat(),
                checked_at_israel=now_il.isoformat(),
                site=config.site_url,
                query=query,
                country=config.country,
                device=config.device,
                clicks=int(metrics["clicks"]),
                impressions=int(metrics["impressions"]),
                ctr=fmt_float(float(metrics["ctr"]), 4),
                avg_position=fmt_float(current_pos, 2),
                estimated_google_page=estimated_page(current_pos),
                previous_avg_position=fmt_float(prev_pos, 2),
                position_change_vs_previous=fmt_float(delta, 2),
            )
        )
    return results


def write_csv(path: Path, rows: list[dict[str, str | int]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def merge_history(existing: list[dict[str, str]], new_rows: list[QueryResult]) -> list[dict[str, str | int]]:
    keys = {(r.date, r.site, r.query, r.country, r.device) for r in new_rows}
    kept = [
        row
        for row in existing
        if (row.get("date", ""), row.get("site", ""), row.get("query", ""), row.get("country", ""), row.get("device", "")) not in keys
    ]
    merged = kept + [r.as_dict() for r in new_rows]
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
            f"| {row.query} | {row.clicks} | {row.impressions} | {row.ctr} | {row.avg_position} | {row.estimated_google_page} | {row.position_change_vs_previous} |"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def print_summary(results: list[QueryResult], demo_run: bool) -> None:
    if demo_run:
        LOGGER.warning("DEMO_RUN enabled: output was generated without Google Search Console API calls.")
    LOGGER.info("Daily results summary (%d queries)", len(results))
    for r in results:
        LOGGER.info(
            "query='%s' clicks=%s impressions=%s ctr=%s avg_position=%s page=%s delta=%s",
            r.query,
            r.clicks,
            r.impressions,
            r.ctr,
            r.avg_position or "-",
            r.estimated_google_page or "-",
            r.position_change_vs_previous or "-",
        )


def main() -> int:
    setup_logging()
    args = parse_args()

    if not should_run_now(args.target_hour, args.force_run):
        return 0

    output_dir = Path(args.output_dir)
    target_date = datetime.now(timezone.utc).date() - timedelta(days=1)
    history_path = output_dir / "rank_history.csv"
    daily_path = output_dir / f"rankings_{target_date.isoformat()}.csv"
    summary_path = output_dir / "daily_summary.md"

    try:
        config = load_config(Path(args.config))
    except Exception as exc:  # noqa: BLE001
        LOGGER.error("Config load failure: %s", exc)
        return 1

    service = None
    if not args.demo_run:
        try:
            creds = load_credentials()
            service = build_service(creds)
        except Exception as exc:  # noqa: BLE001
            LOGGER.error("Startup failure: %s", exc)
            return 1

    history = read_history(history_path)
    try:
        results = build_results(config, target_date, history, service, args.demo_run)
    except Exception as exc:  # noqa: BLE001
        LOGGER.error("Search Console query failed: %s", exc)
        return 1

    daily_rows = [r.as_dict() for r in results]
    merged_history = merge_history(history, results)
    write_csv(daily_path, daily_rows, HISTORY_COLUMNS)
    write_csv(history_path, merged_history, HISTORY_COLUMNS)
    write_daily_summary(summary_path, results)
    print_summary(results, args.demo_run)

    LOGGER.info("Saved daily snapshot: %s", daily_path)
    LOGGER.info("Saved cumulative history: %s", history_path)
    LOGGER.info("Saved markdown summary: %s", summary_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
