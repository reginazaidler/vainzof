from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


def build_reports(
    reports_dir: Path,
    opportunities_df: pd.DataFrame,
    analysis_items: list[dict[str, Any]],
) -> None:
    reports_dir.mkdir(parents=True, exist_ok=True)

    csv_path = reports_dir / "top_opportunities.csv"
    md_path = reports_dir / "fixes_report.md"
    json_path = reports_dir / "dev_tasks.json"

    opportunities_df.to_csv(csv_path, index=False)

    markdown_lines: list[str] = [
        "# SEO Gap Agent Report",
        "",
        "## Top Opportunities",
        "",
    ]

    dev_tasks: list[dict[str, Any]] = []

    for idx, item in enumerate(analysis_items, start=1):
        analysis = item["analysis"]
        markdown_lines.extend(
            [
                f"### {idx}. Query: `{item['query']}`",
                f"- **Page:** {item['page']}",
                f"- **Position:** {item['position']:.2f}",
                f"- **Impressions:** {item['impressions']:.0f}",
                f"- **Opportunity Score:** {item['opportunity_score']:.4f}",
                f"- **Issues:** {', '.join(analysis['why_not_rank_1'])}",
                "- **Exact Fixes:**",
                f"  - Title: {analysis['title_fix']}",
                f"  - Opening paragraph: {analysis['opening_paragraph_fix']}",
                f"  - Sections to add: {', '.join(analysis['sections_to_add'])}",
                f"  - FAQ to add: {', '.join(analysis['faq_to_add'])}",
                f"  - Trust elements: {', '.join(analysis['trust_elements_to_add'])}",
                f"  - CTA fix: {analysis['cta_fix']}",
                f"  - Priority: {analysis['priority']}",
                "",
            ]
        )

        dev_tasks.append(
            {
                "query": item["query"],
                "page": item["page"],
                "position": item["position"],
                "opportunity_score": item["opportunity_score"],
                "priority": analysis["priority"],
                "tasks": {
                    "title_fix": analysis["title_fix"],
                    "opening_paragraph_fix": analysis["opening_paragraph_fix"],
                    "sections_to_add": analysis["sections_to_add"],
                    "faq_to_add": analysis["faq_to_add"],
                    "trust_elements_to_add": analysis["trust_elements_to_add"],
                    "cta_fix": analysis["cta_fix"],
                },
            }
        )

    md_path.write_text("\n".join(markdown_lines), encoding="utf-8")
    json_path.write_text(json.dumps(dev_tasks, indent=2, ensure_ascii=False), encoding="utf-8")
