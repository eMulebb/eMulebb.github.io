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
- Keep English canonical. Locale pages under `es/`, `it/`, and `pt/` are
  generated from the English structure and stay `noindex,follow` until complete.
- Use granular commits: separate policy, content, layout, SEO, and locale work.
- Run the static validation checks in `docs/SITE-HANDBOOK.md` before committing
  and pushing.
