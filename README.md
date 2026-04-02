# vainzof.co.il

Static website source for `vainzof.co.il`.

## Repository contents

- HTML pages at the repository root.
- Shared assets under `assets/`.
- Shared JavaScript under `js/`.
- Technical SEO audit utility: `scripts/seo_audit.py`.
- Optional SEO audit docs: `SEO-AUTOMATION.md`.

## Removed automation

The previous daily rank report automation (Search Console collection, report email sender, and scheduled workflow) was removed from this repository.

## Deploy

The site is deployed via GitHub Pages using `.github/workflows/deploy-pages.yml`.

## Local checks

Run the local SEO audit script (optional):

```bash
python scripts/seo_audit.py
```
