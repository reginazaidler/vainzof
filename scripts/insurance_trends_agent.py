#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib import parse, request
from xml.etree import ElementTree

DEFAULT_KEYWORDS = [
    "ביטוח",
    "ביטוח רכב",
    "ביטוח דירה",
    "ביטוח בריאות",
    "ביטוח חיים",
    "ביטוח נסיעות",
    "סוכן ביטוח",
    "פוליסה",
    "פרמיה",
    "תביעה",
    "השתתפות עצמית",
    "car insurance",
    "health insurance",
    "life insurance",
    "travel insurance",
    "insurance",
]


@dataclass
class TrendItem:
    title: str
    traffic: str
    pub_date: str
    link: str
    description: str
    source_geo: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Fetch Google Trends RSS, filter insurance-related trends, compare with previous runs, "
            "and generate content opportunities report."
        )
    )
    parser.add_argument("--geo", default="IL", help="Google Trends RSS geo code (default: IL)")
    parser.add_argument("--lookback-hours", type=int, default=6, help="Hours window for comparison (default: 6)")
    parser.add_argument(
        "--state-dir",
        default="data/trends-agent",
        help="Directory for snapshots/state files (default: data/trends-agent)",
    )
    parser.add_argument(
        "--report-path",
        default="reports/insurance-trends-report.md",
        help="Markdown report output path (default: reports/insurance-trends-report.md)",
    )
    parser.add_argument(
        "--json-path",
        default="reports/insurance-trends-report.json",
        help="JSON report output path (default: reports/insurance-trends-report.json)",
    )
    parser.add_argument(
        "--keywords-file",
        default="",
        help="Optional text file with one keyword per line (default: built-in list)",
    )
    parser.add_argument(
        "--rss-file",
        default="",
        help="Optional local RSS XML file for offline/dev runs (default: disabled)",
    )
    parser.add_argument("--max-ideas", type=int, default=10, help="Max article ideas in report (default: 10)")
    return parser.parse_args()


def load_keywords(keywords_file: str) -> list[str]:
    if not keywords_file:
        return DEFAULT_KEYWORDS

    path = Path(keywords_file)
    if not path.exists():
        raise FileNotFoundError(f"keywords file not found: {keywords_file}")

    keywords = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return keywords or DEFAULT_KEYWORDS


def fetch_trends_rss(geo: str) -> str:
    params = parse.urlencode({"geo": geo})
    url = f"https://trends.google.com/trending/rss?{params}"
    req = request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with request.urlopen(req, timeout=30) as response:
        return response.read().decode("utf-8", errors="ignore")


def load_rss(args: argparse.Namespace) -> str:
    if args.rss_file:
        path = Path(args.rss_file)
        if not path.exists():
            raise FileNotFoundError(f"rss file not found: {args.rss_file}")
        return path.read_text(encoding="utf-8")

    try:
        return fetch_trends_rss(args.geo)
    except Exception as exc:
        raise RuntimeError(
            "Failed to fetch Google Trends RSS. "
            "If your environment blocks direct access, rerun with --rss-file <path> for offline testing."
        ) from exc


def parse_rss(xml_text: str, geo: str) -> list[TrendItem]:
    root = ElementTree.fromstring(xml_text)
    items = []
    for item in root.findall("./channel/item"):
        title = (item.findtext("title") or "").strip()
        traffic = (item.findtext("{https://trends.google.com/trending/rss}approx_traffic") or "").strip()
        pub_date = (item.findtext("pubDate") or "").strip()
        link = (item.findtext("link") or "").strip()
        description = (item.findtext("description") or "").strip()
        items.append(
            TrendItem(
                title=title,
                traffic=traffic,
                pub_date=pub_date,
                link=link,
                description=description,
                source_geo=geo,
            )
        )
    return items


def tokenize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def is_insurance_related(item: TrendItem, keywords: list[str]) -> bool:
    haystack = tokenize(f"{item.title} {item.description}")
    return any(tokenize(kw) in haystack for kw in keywords)


def load_snapshot(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def choose_previous_snapshot(state_dir: Path, now: datetime, lookback_hours: int) -> Path | None:
    candidates = sorted(state_dir.glob("snapshot_*.json"), reverse=True)
    if not candidates:
        return None

    threshold = now - timedelta(hours=lookback_hours)
    for candidate in candidates:
        data = load_snapshot(candidate)
        timestamp = datetime.fromisoformat(data["run_timestamp_utc"])
        if timestamp >= threshold:
            return candidate
    return candidates[0]


def map_by_title(trends: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {tokenize(item["title"]): item for item in trends}


def generate_article_idea(title: str) -> dict[str, str]:
    clean = title.strip(" -")
    return {
        "topic": clean,
        "headline": f"{clean}: מה חשוב לדעת עכשיו לפני שקונים או מעדכנים ביטוח",
        "angle": "הסבר פרקטי + השוואת חלופות + טעויות נפוצות + למי זה מתאים",
        "cta": "רוצים לבדוק אם הפוליסה שלכם עדיין משתלמת? קבלו בדיקה אישית קצרה.",
    }


def build_report_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# דוח טרנדים לביטוח (Google Trends)",
        "",
        f"זמן ריצה (UTC): {payload['run_timestamp_utc']}",
        f"אזור: {payload['geo']}",
        f"מספר טרנדים כלליים שנמצאו: {payload['total_trends']}",
        f"מספר טרנדים רלוונטיים לביטוח: {payload['insurance_trends_count']}",
        "",
        "## שינויים לעומת הריצה הקודמת",
        f"- חדשים: {len(payload['changes']['new'])}",
        f"- ירדו מהרשימה: {len(payload['changes']['removed'])}",
        f"- נשארו: {len(payload['changes']['unchanged'])}",
        "",
        "## טרנדים חדשים רלוונטיים לביטוח",
    ]

    if payload["changes"]["new"]:
        for item in payload["changes"]["new"]:
            lines.append(f"- **{item['title']}** | traffic: {item.get('traffic', 'n/a')} | {item.get('link', '')}")
    else:
        lines.append("- לא נמצאו טרנדים חדשים בתחום הביטוח בריצה זו.")

    lines.extend(["", "## רעיונות לכתבות לפרסום מהיר"])
    if payload["article_ideas"]:
        for idx, idea in enumerate(payload["article_ideas"], start=1):
            lines.extend(
                [
                    f"### {idx}. {idea['headline']}",
                    f"- נושא: {idea['topic']}",
                    f"- זווית: {idea['angle']}",
                    f"- CTA: {idea['cta']}",
                    "",
                ]
            )
    else:
        lines.append("- אין כרגע רעיונות חדשים, מומלץ להרחיב רשימת מילות מפתח או להגדיל חלון זמן להשוואה.")

    lines.extend(
        [
            "## הערות",
            "- מקור הנתונים: Google Trends RSS (חינמי, ללא API בתשלום).",
            "- מומלץ להריץ כל 3–6 שעות דרך cron.",
        ]
    )
    return "\n".join(lines).strip() + "\n"


def main() -> int:
    args = parse_args()
    now = datetime.now(timezone.utc)
    state_dir = Path(args.state_dir)
    report_path = Path(args.report_path)
    json_path = Path(args.json_path)

    state_dir.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.parent.mkdir(parents=True, exist_ok=True)

    keywords = load_keywords(args.keywords_file)
    xml_text = load_rss(args)
    all_trends = parse_rss(xml_text, args.geo)
    insurance_items = [item for item in all_trends if is_insurance_related(item, keywords)]

    current_trends = [asdict(item) for item in insurance_items]
    previous_snapshot_path = choose_previous_snapshot(state_dir, now, args.lookback_hours)

    prev_trends: list[dict[str, Any]] = []
    if previous_snapshot_path:
        prev_data = load_snapshot(previous_snapshot_path)
        prev_trends = prev_data.get("insurance_trends", [])

    prev_map = map_by_title(prev_trends)
    curr_map = map_by_title(current_trends)

    new_titles = sorted(set(curr_map.keys()) - set(prev_map.keys()))
    removed_titles = sorted(set(prev_map.keys()) - set(curr_map.keys()))
    unchanged_titles = sorted(set(curr_map.keys()) & set(prev_map.keys()))

    article_ideas = [generate_article_idea(curr_map[title]["title"]) for title in new_titles[: args.max_ideas]]

    payload = {
        "run_timestamp_utc": now.isoformat(),
        "geo": args.geo,
        "keywords": keywords,
        "total_trends": len(all_trends),
        "insurance_trends_count": len(current_trends),
        "insurance_trends": current_trends,
        "changes": {
            "new": [curr_map[title] for title in new_titles],
            "removed": [prev_map[title] for title in removed_titles],
            "unchanged": [curr_map[title] for title in unchanged_titles],
        },
        "article_ideas": article_ideas,
        "previous_snapshot": str(previous_snapshot_path) if previous_snapshot_path else None,
    }

    snapshot_name = now.strftime("snapshot_%Y%m%dT%H%M%SZ.json")
    snapshot_path = state_dir / snapshot_name
    snapshot_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    report_path.write_text(build_report_markdown(payload), encoding="utf-8")

    print(f"[insurance-trends-agent] snapshot={snapshot_path}")
    print(f"[insurance-trends-agent] report_md={report_path}")
    print(f"[insurance-trends-agent] report_json={json_path}")
    print(
        "[insurance-trends-agent] "
        f"total={payload['total_trends']} insurance={payload['insurance_trends_count']} "
        f"new={len(payload['changes']['new'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
