# vainzof.co.il - Daily SEO Rank Tracking (Google Search Console)

This repository includes an automated daily SEO rank-tracking job based on the **Google Search Console API** (no SERP scraping).

## Folder structure

- `scripts/check_rankings.py` - main Python script that fetches yesterday's query performance and writes reports.
- `config/queries.json` - configurable site, country, device, and list of tracked queries.
- `.github/workflows/daily-rank-check.yml` - scheduled + manual GitHub Actions workflow.
- `requirements.txt` - Python dependencies.
- `output/` - generated CSV + Markdown reports (artifact output).

## What the script produces

On each successful run:

- `output/rankings_YYYY-MM-DD.csv` - daily snapshot.
- `output/rank_history.csv` - cumulative history (idempotent replacement by date+query key).
- `output/daily_summary.md` - quick Markdown table for that run.

Columns written per query:

- `date`
- `checked_at_utc`
- `checked_at_israel`
- `site`
- `query`
- `country`
- `device`
- `clicks`
- `impressions`
- `ctr`
- `avg_position`
- `estimated_google_page`
- `previous_avg_position`
- `position_change_vs_previous` (calculated as `previous_avg_position - current_avg_position`, so positive = improvement)

## Configuration

Edit `config/queries.json`:

```json
{
  "site_url": "sc-domain:vainzof.co.il",
  "country": "ISR",
  "device": "all",
  "queries": [
    "יובל ויינזוף",
    "סוכן ביטוח בהרצליה"
  ]
}
```

Notes:

- `site_url` supports Search Console property formats such as `sc-domain:vainzof.co.il`.
- `device` supports `all` (default) or specific Search Console device values.

## Required GitHub Secret

Add this repository secret:

- **`GSC_SERVICE_ACCOUNT_JSON`**: full JSON credentials of a Google Cloud service account.

### Important permissions setup

1. In Google Search Console, open the target property (for example `sc-domain:vainzof.co.il`).
2. Add the service account email as a property user (read access is enough).
3. If this permission is missing, the API call will fail and the workflow will exit with a clear error.

## GitHub Actions scheduling and timezone behavior

Workflow file: `.github/workflows/daily-rank-check.yml`

- Runs on a UTC cron window (`17 1-4 * * *`) to cover Israel 05:00 under DST and standard time.
- GitHub Actions schedules are UTC and run against the latest commit on the default branch.
- The Python script uses `Asia/Jerusalem` local time and proceeds only at local hour `05`.
- If run outside that hour, it exits successfully without error.
- Manual `workflow_dispatch` runs set `FORCE_RUN=true` so you can test instantly.

## Manual validation test plan (workflow_dispatch)

1. Push the branch to GitHub.
2. Confirm the `GSC_SERVICE_ACCOUNT_JSON` secret is configured.
3. Open **Actions** -> **Daily SEO Rank Check** -> **Run workflow**.
4. Verify logs show per-query summary lines and output file paths.
5. Download the uploaded artifact (`seo-rank-output-<run_id>`).
6. Confirm the artifact includes:
   - `output/rankings_YYYY-MM-DD.csv`
   - `output/rank_history.csv`
   - `output/daily_summary.md`
7. Re-run `workflow_dispatch` on the same day and verify `rank_history.csv` remains idempotent for the same date+query keys.



### Bootstrap/demo run (no API call)

If you want to verify output generation immediately in an environment without Google credentials/dependencies, run:

```bash
python scripts/check_rankings.py --config config/queries.json --output-dir output --force-run --demo-run
```

This writes the same CSV/Markdown structure with zeroed metrics and empty position fields.

## Local run (optional)

```bash
export GSC_SERVICE_ACCOUNT_JSON='{"type":"service_account",...}'
python -m pip install -r requirements.txt
python scripts/check_rankings.py --config config/queries.json --output-dir output --force-run
```

