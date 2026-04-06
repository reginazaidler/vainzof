# vainzof.co.il

Static website source for `vainzof.co.il`.

## Repository contents

- HTML pages at the repository root.
- Shared assets under `assets/`.
- Shared JavaScript under `js/`.
- Technical SEO audit utility: `scripts/seo_audit.py`.
- Optional SEO audit docs: `SEO-AUTOMATION.md`.
- Insurance trends automation docs: `TRENDS-AUTOMATION.md`.

## Removed automation

The previous daily rank report automation (Search Console collection, report email sender, and scheduled workflow) was removed from this repository.

## Deploy

The site is deployed via GitHub Pages using `.github/workflows/deploy-pages.yml`.

## Local checks

Run the local SEO audit script (optional):

```bash
python scripts/seo_audit.py
```


## Insurance Trends agent (free)

Run:

```bash
python3 scripts/insurance_trends_agent.py --geo IL --lookback-hours 6
```

Outputs are written to `reports/insurance-trends-report.md`, `reports/insurance-trends-report.json`, and `data/trends-agent/snapshot_*.json`.


GitHub-only run: use **Actions → Run Insurance Trends Agent** (workflow file: `.github/workflows/insurance-trends-agent.yml`).
In manual GitHub runs you can override `geo` and `lookback_hours`; if no direct insurance trends are found, the report includes fallback insurance-angle ideas based on general hot trends.
