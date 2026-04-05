from __future__ import annotations

import json
from datetime import datetime, timezone

from app.analyzer import analyze_page_gap
from app.config import load_settings
from app.db import bulk_insert, get_connection, init_db
from app.fetch_gsc_data import GSCFetchParams, fetch_gsc_data
from app.gsc_client import GSCClient
from app.opportunity_scoring import filter_opportunities, score_opportunities
from app.page_extractor import extract_page_snapshot
from app.report_builder import build_reports


def _empty_opportunities_df():
    import pandas as pd

    return pd.DataFrame(
        columns=[
            "query",
            "page",
            "clicks",
            "impressions",
            "ctr",
            "position",
            "expected_ctr",
            "opportunity_score",
        ]
    )


def run_pipeline() -> None:
    settings = load_settings()
    conn = get_connection(settings.db_path)
    init_db(conn)

    gsc_client = GSCClient(
        client_id=settings.gsc_client_id,
        client_secret=settings.gsc_client_secret,
        refresh_token=settings.gsc_refresh_token,
        site_url=settings.gsc_site_url,
        timeout=settings.request_timeout_seconds,
    )

    fetch_params = GSCFetchParams(
        start_date=settings.start_date,
        end_date=settings.end_date,
        max_rows=settings.max_rows,
    )
    raw_df = fetch_gsc_data(gsc_client, fetch_params)
    print(f"Fetched {len(raw_df)} query-page rows from GSC ({settings.start_date} to {settings.end_date}).")

    if raw_df.empty:
        build_reports(settings.reports_dir, _empty_opportunities_df(), [])
        print("No GSC rows returned. Generated empty reports.")
        return

    impressions_mask = raw_df["impressions"] >= settings.min_impressions
    position_mask = (raw_df["position"] >= settings.min_position) & (raw_df["position"] <= settings.max_position)
    brand_mask = raw_df["query"].astype(str).str.lower()
    brand_pattern = "|".join(settings.exclude_brand_queries) if settings.exclude_brand_queries else ""
    brand_pass_mask = ~brand_mask.str.contains(brand_pattern, regex=True, na=False) if brand_pattern else None

    print(
        "Filter diagnostics:",
        f"impressions>={settings.min_impressions}: {int(impressions_mask.sum())}/{len(raw_df)};",
        f"position_between_{settings.min_position}_{settings.max_position}: {int(position_mask.sum())}/{len(raw_df)};",
        (
            f"brand_excluded_pass: {int(brand_pass_mask.sum())}/{len(raw_df)};"
            if brand_pass_mask is not None
            else "brand_excluded_pass: skipped;"
        ),
    )

    bulk_insert(
        conn,
        """
        INSERT INTO query_page_metrics (
            query, page, clicks, impressions, ctr, position, start_date, end_date, fetched_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                row.query,
                row.page,
                float(row.clicks),
                float(row.impressions),
                float(row.ctr),
                float(row.position),
                row.start_date,
                row.end_date,
                row.fetched_at,
            )
            for row in raw_df.itertuples(index=False)
        ],
    )

    filtered_df = filter_opportunities(
        df=raw_df,
        min_impressions=settings.min_impressions,
        min_position=settings.min_position,
        max_position=settings.max_position,
        exclude_brand_queries=settings.exclude_brand_queries,
    )

    scored_df = score_opportunities(filtered_df)
    top_df = scored_df.head(settings.top_n).copy()

    if top_df.empty:
        # Fallback: if strict filters return nothing, continue with the best rows
        # from raw data so the run still returns actionable output files.
        fallback_df = score_opportunities(raw_df).head(settings.top_n).copy()
        if fallback_df.empty:
            build_reports(settings.reports_dir, _empty_opportunities_df(), [])
            print("No opportunities found after fallback. Generated empty reports.")
            return
        top_df = fallback_df
        print("No opportunities matched strict filters; using fallback ranking from raw GSC data.")

    selected_at = datetime.now(timezone.utc).isoformat()
    bulk_insert(
        conn,
        """
        INSERT INTO opportunities (
            query, page, clicks, impressions, ctr, position, expected_ctr, opportunity_score, selected_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                row.query,
                row.page,
                float(row.clicks),
                float(row.impressions),
                float(row.ctr),
                float(row.position),
                float(row.expected_ctr),
                float(row.opportunity_score),
                selected_at,
            )
            for row in top_df.itertuples(index=False)
        ],
    )

    analysis_items: list[dict] = []

    for row in top_df.itertuples(index=False):
        snapshot = extract_page_snapshot(row.page, timeout=settings.request_timeout_seconds)

        bulk_insert(
            conn,
            """
            INSERT INTO page_snapshots (
                page, title, meta_description, h1, h2s_json, main_content, html_fetched_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    snapshot.page,
                    snapshot.title,
                    snapshot.meta_description,
                    snapshot.h1,
                    json.dumps(snapshot.h2s, ensure_ascii=False),
                    snapshot.main_content,
                    datetime.now(timezone.utc).isoformat(),
                )
            ],
        )

        analysis = analyze_page_gap(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
            payload={
                "query": row.query,
                "page": row.page,
                "position": float(row.position),
                "ctr": float(row.ctr),
                "title": snapshot.title,
                "meta_description": snapshot.meta_description,
                "h1": snapshot.h1,
                "h2s": snapshot.h2s,
                "main_content": snapshot.main_content,
            },
            timeout=max(40, settings.request_timeout_seconds),
        )

        analysis_items.append(
            {
                "query": row.query,
                "page": row.page,
                "position": float(row.position),
                "impressions": float(row.impressions),
                "opportunity_score": float(row.opportunity_score),
                "analysis": analysis,
            }
        )

    build_reports(settings.reports_dir, top_df, analysis_items)
    print("Pipeline completed successfully.")


if __name__ == "__main__":
    run_pipeline()
