# seo-gap-agent

Automated SEO optimization agent that pulls Google Search Console query/page data, identifies ranking gaps, analyzes pages with OpenAI, and generates implementation-ready reports.

## What it does

On each run the agent:

1. Pulls last 28 days of GSC performance data (`query + page`) with pagination up to 50,000 rows.
2. Filters opportunities:
   - `impressions >= 1` (configurable)
   - `position between 1 and 12` (configurable)
   - excludes brand queries from a configurable list.
   - if strict filters return no rows, falls back to ranking raw GSC rows so reports are still generated.
   - logs filter diagnostics (how many rows pass each condition) for easier debugging in Actions logs.
3. Scores opportunities with:

   `opportunity_score = impressions * (expected_ctr - ctr) / position`

4. Extracts page signals (`title`, `meta description`, `H1`, `H2s`, `main content`).
5. Calls OpenAI to return strict JSON recommendations.
6. Writes reports:
   - `reports/top_opportunities.csv`
   - `reports/fixes_report.md`
   - `reports/dev_tasks.json`
   - if no rows are available at all, writes empty report files instead of exiting without outputs.
7. Stores run data in SQLite (`data/seo_gap_agent.db`).

## Project structure

```text
repo-root/
├─ .github/workflows/run-agent.yml
└─ seo-gap-agent/
   ├─ app/
   │  ├─ main.py
   │  ├─ gsc_client.py
   │  ├─ fetch_gsc_data.py
   │  ├─ opportunity_scoring.py
   │  ├─ page_extractor.py
   │  ├─ analyzer.py
   │  ├─ prompts.py
   │  ├─ report_builder.py
   │  ├─ db.py
   │  └─ config.py
   ├─ reports/
   ├─ data/
   ├─ requirements.txt
   └─ README.md
```

## Requirements

- Python 3.11
- Google Search Console property access
- OpenAI API key

Install dependencies:

```bash
pip install -r requirements.txt
```

## Environment variables

Set these before running:

- `OPENAI_API_KEY`
- `GSC_CLIENT_ID`
- `GSC_CLIENT_SECRET`
- `GSC_REFRESH_TOKEN`
- `GSC_SITE_URL`

Optional:

- `EXCLUDE_BRAND_QUERIES` (comma-separated, example: `brand,brand.com,brand name`)
- `OPENAI_MODEL` (default: `gpt-4.1-mini`; empty value also falls back to this default)
- `MIN_IMPRESSIONS` (default: `1`)
- `MIN_POSITION` (default: `1`)
- `MAX_POSITION` (default: `12`)
- `TOP_N` (default: `20`)

## Getting Google Search Console credentials

This project uses an OAuth refresh token flow (suitable for GitHub Actions):

1. Open Google Cloud Console and create/select a project.
2. Enable **Google Search Console API**.
3. Configure OAuth consent screen.
4. Create OAuth Client ID credentials (Web or Desktop app).
5. Generate a refresh token with the scope:

   `https://www.googleapis.com/auth/webmasters.readonly`

6. Save values into GitHub Secrets:
   - `GSC_CLIENT_ID`
   - `GSC_CLIENT_SECRET`
   - `GSC_REFRESH_TOKEN`
   - `GSC_SITE_URL` (example: `sc-domain:example.com` or `https://www.example.com/`)

## Run locally

From inside `seo-gap-agent/`:

```bash
python app/main.py
```

Outputs:

- `reports/top_opportunities.csv`
- `reports/fixes_report.md`
- `reports/dev_tasks.json`
- `data/seo_gap_agent.db`

## GitHub Actions automation

Workflow file: `../.github/workflows/run-agent.yml` (at repository root)

- Triggered weekly (Monday at 08:00 UTC).
- Supports manual trigger (`workflow_dispatch`).
- Installs Python 3.11 + dependencies.
- Runs `python app/main.py`.
- Uploads generated reports as an artifact (`seo-gap-agent-reports`).

## Notes

- Keep `EXCLUDE_BRAND_QUERIES` updated so branded terms are excluded from gap analysis.
- The AI response is validated to ensure strict JSON keys before report generation.
- OpenAI analysis retries on `429` rate limits (exponential backoff). If retries are exhausted, fallback placeholder recommendations are written and reused for the remaining rows in that run.
- When a run is rate-limited by OpenAI, reports explicitly mark AI analysis as unavailable and avoid emitting fake per-row fix text.
- SQLite tables created:
  - `query_page_metrics`
  - `opportunities`
  - `page_snapshots`
