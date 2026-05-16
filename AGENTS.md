# eMulebb Pages Agent Policy

This repository publishes the public GitHub Pages site for eMule broadband
edition.

Read `docs/SITE-HANDBOOK.md` before making content, layout, SEO, locale, or
publishing-policy changes.

## Hard Rules

- Do not publish logo, mascot, favicon, screenshot, or other brand image assets
  from this repository.
- Keep the site text-first. If a page needs a product signal, use typography,
  layout, color, and structured content instead of image branding.
- Treat `eMule-tooling` active/reference docs as the source of truth. Pages
  summarizes and links; it does not invent feature or release facts.
- Only shipped, landed, passed, or release-proven features belong in the public
  homepage feature/catalog copy.
- Keep English canonical. Completed locale pages live under `es/`, `pt-br/`,
  `pt-pt/`, `it/`, `ru/`, `de/`, `fr/`, `pl/`, `nl/`, and `tr/`; they should
  match the English section structure, use reciprocal `hreflang` links, and
  stay `index,follow`.
- Keep `pt/` as the Portuguese regional chooser only; it must stay
  `noindex,follow` and must not be listed in `sitemap.xml`.
- Use granular commits: separate policy, content, layout, SEO, and locale work.
- Run the static validation checks in `docs/SITE-HANDBOOK.md` before committing
  and pushing.

## Supporting Tooling

- Page production and validation helpers are tracked in
  `..\eMulebb-workspace\repos\eMule-tooling\helpers\pages-site-tools.py`.
- Use `python ..\eMulebb-workspace\repos\eMule-tooling\helpers\pages-site-tools.py --pages-root . validate`
  before publishing locale, metadata, sitemap, asset-policy, or navigation
  changes.
- Use `python ..\eMulebb-workspace\repos\eMule-tooling\helpers\pages-site-tools.py --pages-root . write-sitemap --lastmod YYYY-MM-DD`
  to regenerate `sitemap.xml` from the canonical locale table.
