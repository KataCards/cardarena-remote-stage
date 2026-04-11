# Resource Pages Template

This folder contains the shared layout, styling, and behavior for static pages under
`src/resources/pages/` (boot page and error pages).

## Purpose

- Centralize semantic tokens, hero/CTA patterns, and ambient effects.
- Keep page HTML focused on content only.
- Preserve local-file compatibility by using relative links.

## Files

- `style.css`: shared tokens, hero/CTA patterns, layout, and effects.
- `script.js`: shared lightweight behavior for static pages.

## Font Setup (Local)

Place these files in `src/resources/pages/template/fonts/`:

- `Geist-Variable.woff2`
- `GeistMono-Variable.woff2`

The stylesheet already contains `@font-face` entries for those filenames.
If they are not present, fallback fonts are used automatically.

## How To Use

1. In any page HTML file, link the shared assets:

   <link rel="stylesheet" href="../template/style.css">
   <script defer src="../template/script.js"></script>

2. For deeper folders, adjust relative paths accordingly (for example error pages use `../../template/...`).

3. Keep page-specific changes in markup classes and text, not in duplicated inline CSS.
