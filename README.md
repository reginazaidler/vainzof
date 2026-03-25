# vainzof.co.il - Daily SEO Rank Tracking (Google Search Console)

This repository includes an automated daily SEO rank-tracking job based on the **Google Search Console API** (no SERP scraping).

## Folder structure

- `scripts/check_rankings.py` - main Python script that fetches Search Console query performance and writes reports.
- `scripts/send_report_email.py` - sends the generated report files by email via SMTP.
- `config/queries.json` - configurable site, country, device, and list of tracked queries.
- `.github/workflows/daily-rank-check.yml` - scheduled + manual GitHub Actions workflow.
- `requirements.txt` - Python dependencies.
- `output/` - generated CSV + Markdown reports (artifact output).

## What the script produces

On each successful run:

- `output/rankings_YYYY-MM-DD.csv` - daily snapshot.
- `output/rank_history.csv` - cumulative history (idempotent replacement by date+query key).
- `output/daily_summary.md` - quick Markdown table for that run.
- `output/last_target_date.txt` - the exact date used for the current run (used by email step).

> Search Console data can be delayed. The script starts with yesterday (UTC) and can automatically fall back to older dates until data exists.

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

Add these repository secrets:

- **`GSC_SERVICE_ACCOUNT_JSON`**: full JSON credentials of a Google Cloud service account.
- **`SMTP_HOST`**: SMTP server host (for example `smtp.gmail.com`).
- **`SMTP_PORT`**: SMTP port (`587` for STARTTLS or `465` for SSL).
- **`SMTP_USERNAME`**: SMTP username/login.
- **`SMTP_PASSWORD`**: SMTP password or app password.
- **`SMTP_FROM`**: sender email address.
- **`SMTP_TO`**: comma-separated recipient emails.
- **`REPORT_SUBJECT_PREFIX`** (optional): custom email subject prefix.

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
- After a successful run, the workflow sends the summary + CSV files to the emails in `SMTP_TO`.

## Manual validation test plan (workflow_dispatch)

1. Push the branch to GitHub.
2. Confirm the `GSC_SERVICE_ACCOUNT_JSON` secret is configured.
3. Open **Actions** -> **Daily SEO Rank Check** -> **Run workflow**.
4. Verify logs show per-query summary lines and output file paths.
5. Verify the workflow step **Send report by email** completed successfully and the recipients received the email.
6. Download the uploaded artifact (`seo-rank-output-<run_id>`).
7. Confirm the artifact includes:
   - `output/rankings_YYYY-MM-DD.csv`
   - `output/rank_history.csv`
   - `output/daily_summary.md`
8. Re-run `workflow_dispatch` on the same day and verify `rank_history.csv` remains idempotent for the same date+query keys.



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

Optional fallback tuning:

```bash
python scripts/check_rankings.py --config config/queries.json --output-dir output --max-date-lag-days 3
```
