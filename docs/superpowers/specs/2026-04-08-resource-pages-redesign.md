# Resource Pages Redesign

**Date:** 2026-04-08
**Scope:** `src/resources/pages/` — 4 error pages (403, 404, 500, 502) + boot-ready page

---

## Goal

Rework the static resource pages to more closely resemble the cardarena-frontend-core landing page aesthetic, while fitting entirely within a no-scroll viewport at both 16:9 (landscape kiosk) and 9:16 (portrait kiosk) aspect ratios.

---

## Constraints

- No scrolling in either orientation — content must fit within `100dvh`
- Two layouts: one shared by all error pages, one for boot-ready (and future non-error pages)
- All existing content is preserved — this is a layout/CSS rework, not a content change
- Shared template (`style.css`, `script.js`) stays shared; HTML files are updated to use new structure

---

## Approach: Orientation Media Queries

Use `@media (orientation: landscape)` and `@media (orientation: portrait)` in `style.css` to flip between layouts. No JS required.

---

## Shared Foundation Changes (`style.css`)

- `html, body` and `.shell` change from `min-height: 100vh` to `height: 100dvh; overflow: hidden`
- `body` removes `min-height: 100%` in favour of `height: 100dvh`
- `main` gets `max-height: calc(100dvh - 2 * var(--shell-pad)); overflow: hidden` to prevent card overflow
- `clamp()` font size upper bounds tightened so content never overflows at typical kiosk resolutions (1280×720 landscape, 720×1280 portrait)
- Orbs, animations, glassmorphism card, design tokens — unchanged

---

## Layout A: Error Pages (403, 404, 500, 502)

### Landscape (16:9)
```
┌─────────────────────────────────────────────────────────┐
│  eyebrow · · · · · · · · · · · · · · · ● STATUS CHIP    │
│                                                         │
│  [CODE]   Title                                         │
│           Subtitle copy line                            │
│                                                         │
│  ┌──────────────────┐  ┌──────────────────┐            │
│  │ What to check    │  │ Current state    │            │
│  │ · item           │  │ paragraph        │            │
│  │ · item           │  │                  │            │
│  └──────────────────┘  └──────────────────┘            │
│                                                         │
│  [Retry request]  [Go back]                             │
│  footer · · · · · · · · · · · · · · · · · · · · · · ·  │
└─────────────────────────────────────────────────────────┘
```

### Portrait (9:16)
Same element order. Error code + title stack full-width. Panel blocks stack vertically. Buttons go full-width. Card takes ~90vw.

### Key structural change
Eyebrow and status chip move into a single flex row (`justify-content: space-between`) to save vertical space.

---

## Layout B: Boot-Ready Page

### Landscape (16:9)
```
┌─────────────────────────────────────────────────────────┐
│  CardArena Remote Stage · · · · · · · ● BOOT COMPLETE   │
│                                                         │
│  READY                    ┌─────────────────────────┐  │
│  Bootup worked. The       │ Signal                  │  │
│  kiosk is ready to        │ ─────────────────────── │  │
│  take inputs.             │ Online      System      │  │
│                           │ Armed       Inputs      │  │
│  Runtime is healthy,      │ Ready       Mode        │  │
│  API is responding.       └─────────────────────────┘  │
│                                                         │
│  [Open control surface]  [Read boot docs]               │
│  ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─  │
│  ● Static boot-ready page · CardArena startup online    │
└─────────────────────────────────────────────────────────┘
```

### Portrait (9:16)
READY code + headline + copy + buttons stacked full-width. Status card below as a single row of three metrics (Online · Armed · Ready). Footer at bottom.

### Key structural change
Eyebrow + status chip become a top header row. `READY` code gets prominent display sizing. Status card fills the right column in landscape. Footer pinned to bottom of card.

---

## Files Touched

| File | Change |
|------|--------|
| `src/resources/pages/template/style.css` | Foundation changes + orientation media queries |
| `src/resources/pages/error-pages/403/index.html` | Eyebrow+status header row |
| `src/resources/pages/error-pages/404/index.html` | Eyebrow+status header row |
| `src/resources/pages/error-pages/500/index.html` | Eyebrow+status header row |
| `src/resources/pages/error-pages/502/index.html` | Eyebrow+status header row |
| `src/resources/pages/boot-ready/index.html` | Eyebrow+status header row; footer pinned |

---

## What Is Not Changing

- Visual design tokens (colors, fonts, shadows, animations)
- Content text in any page
- The shared `script.js`
- The orb/halo/pulse decorative elements
