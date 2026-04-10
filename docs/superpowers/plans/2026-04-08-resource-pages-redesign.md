# Resource Pages Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rework all static resource pages to fit no-scroll in 16:9 and 9:16 viewports using a landing-page-inspired layout, with a shared error layout and a separate boot-ready hero layout.

**Architecture:** Shared `style.css` gets three additions: a no-scroll foundation (fixed heights), a `.page-header` flex row component, and orientation media queries. All five HTML files get a single structural change (eyebrow + status wrapped in `.page-header`). No new files are created.

**Tech Stack:** Vanilla HTML, CSS (no build step). Verification via browser DevTools device toolbar.

---

## File Map

| File | Change |
|------|--------|
| `src/resources/pages/template/style.css` | No-scroll foundation, `.page-header`, font tightening, orientation queries |
| `src/resources/pages/error-pages/403/index.html` | Wrap eyebrow + status in `.page-header` |
| `src/resources/pages/error-pages/404/index.html` | Wrap eyebrow + status in `.page-header` |
| `src/resources/pages/error-pages/500/index.html` | Wrap eyebrow + status in `.page-header` |
| `src/resources/pages/error-pages/502/index.html` | Wrap eyebrow + status in `.page-header` |
| `src/resources/pages/boot-ready/index.html` | Wrap eyebrow + status in `.page-header` |

---

## Task 1: No-scroll foundation in style.css

**Files:**
- Modify: `src/resources/pages/template/style.css`

- [ ] **Step 1: Change `html, body` shared block from `min-height` to fixed height**

Find this block (lines 60–63):
```css
html,
body {
  margin: 0;
  min-height: 100%;
}
```
Replace with:
```css
html,
body {
  margin: 0;
  height: 100dvh;
}
```

- [ ] **Step 2: Change `body` block from `min-height` to fixed height and add `overflow: hidden`**

Find this in the `body` rule (line 68):
```css
body {
  min-height: 100vh;
```
Replace `min-height: 100vh` with `height: 100dvh` and add `overflow: hidden` as the second property:
```css
body {
  height: 100dvh;
  overflow: hidden;
```

- [ ] **Step 3: Change `.shell` from `min-height` to fixed height**

Find in `.shell` (line 111):
```css
.shell {
  position: relative;
  min-height: 100vh;
```
Replace `min-height: 100vh` with `height: 100dvh`:
```css
.shell {
  position: relative;
  height: 100dvh;
```

- [ ] **Step 4: Add `max-height` and `overflow: hidden` to `main`**

Find in `main` (line 213), after `border-radius: var(--radius);`:
```css
main {
  position: relative;
  width: min(var(--page-width), 100%);
  padding: var(--card-pad);
  border-radius: var(--radius);
  border: 1px solid hsl(var(--border));
```
Add `max-height` and `overflow: hidden` after `width`:
```css
main {
  position: relative;
  width: min(var(--page-width), 100%);
  max-height: calc(100dvh - 2 * var(--shell-pad));
  overflow: hidden;
  padding: var(--card-pad);
  border-radius: var(--radius);
  border: 1px solid hsl(var(--border));
```

- [ ] **Step 5: Verify in browser — open any error page at 1280×720**

Open `src/resources/pages/error-pages/404/index.html` in Chrome.
Open DevTools → device toolbar → set custom size 1280×720.
Expected: no scrollbar, all content visible, card centered.

- [ ] **Step 6: Commit**

```bash
git add src/resources/pages/template/style.css
git commit -m "feat: add no-scroll foundation to resource page template"
```

---

## Task 2: Tighten font sizes in style.css

**Files:**
- Modify: `src/resources/pages/template/style.css`

These reductions ensure the error code, heading, and copy fit inside the card at 1280×720 (the tightest expected landscape kiosk resolution).

- [ ] **Step 1: Tighten `.code` font size**

Find (line 325):
```css
.code {
  margin: 0;
  font-size: clamp(64px, 7.2vw, 116px);
```
Replace with:
```css
.code {
  margin: 0;
  font-size: clamp(48px, 5.8vw, 88px);
```

- [ ] **Step 2: Tighten `h1` font size**

Find (line 333):
```css
h1 {
  margin: 0;
  font-size: clamp(34px, 3.85vw, 58px);
```
Replace with:
```css
h1 {
  margin: 0;
  font-size: clamp(26px, 3.1vw, 46px);
```

- [ ] **Step 3: Verify in browser at 1280×720**

Open `src/resources/pages/error-pages/404/index.html` at 1280×720.
Expected: error code visible and large, heading readable, no overflow.

- [ ] **Step 4: Commit**

```bash
git add src/resources/pages/template/style.css
git commit -m "feat: tighten font sizes for no-scroll kiosk viewports"
```

---

## Task 3: Add `.page-header` component to style.css

**Files:**
- Modify: `src/resources/pages/template/style.css`

- [ ] **Step 1: Add `.page-header` rule after the `.eyebrow` rule**

Find the `.eyebrow` block (line 246). After its closing `}`, insert:
```css

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}

.page-header .eyebrow {
  margin: 0;
}

.page-header .status {
  margin: 0;
}
```

- [ ] **Step 2: Verify in browser — temporarily add the class to an error page**

Open `src/resources/pages/error-pages/404/index.html`. In DevTools, wrap the eyebrow `<p>` and status `<div>` in a `<div class="page-header">` (in the Elements panel, not the file). Expected: eyebrow appears left, status chip appears right on the same line.

- [ ] **Step 3: Commit**

```bash
git add src/resources/pages/template/style.css
git commit -m "feat: add page-header flex row component to template"
```

---

## Task 4: Add orientation media queries to style.css

**Files:**
- Modify: `src/resources/pages/template/style.css`

- [ ] **Step 1: Add landscape and portrait orientation rules at the end of style.css, before the `prefers-reduced-motion` block**

Find the `@media (prefers-reduced-motion: reduce)` block (line 766). Insert above it:
```css
@media (orientation: landscape) {
  :root {
    --shell-pad: clamp(10px, 1.4vw, 22px);
    --card-pad: clamp(14px, 1.8vw, 28px);
  }
}

@media (orientation: portrait) {
  :root {
    --shell-pad: 12px;
    --card-pad: clamp(14px, 4vw, 26px);
  }

  /* Boot-ready: status card becomes a horizontal row of metrics */
  .hero-side .status-card {
    display: flex;
    flex-wrap: wrap;
    align-items: flex-start;
    gap: 8px;
  }

  .hero-side .status-card .block-title {
    width: 100%;
    margin-bottom: 0;
  }

  .hero-side .status-card .status-line {
    flex: 1 1 80px;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 8px 10px;
    border-top: none;
    border: 1px solid hsl(var(--border));
    border-radius: 12px;
    background: hsl(var(--background));
    gap: 4px;
  }

  .hero-side .status-card .status-line strong {
    font-size: 14px;
  }
}

```

- [ ] **Step 2: Verify landscape at 1280×720**

Open `src/resources/pages/boot-ready/index.html` at 1280×720.
Expected: tighter padding, two-column hero, no scroll.

- [ ] **Step 3: Verify portrait at 720×1280**

Set DevTools to 720×1280.
Expected: single-column layout, status card shows three metric tiles side-by-side, no scroll.

- [ ] **Step 4: Commit**

```bash
git add src/resources/pages/template/style.css
git commit -m "feat: add landscape/portrait orientation media queries to template"
```

---

## Task 5: Update all error page HTML files

**Files:**
- Modify: `src/resources/pages/error-pages/403/index.html`
- Modify: `src/resources/pages/error-pages/404/index.html`
- Modify: `src/resources/pages/error-pages/500/index.html`
- Modify: `src/resources/pages/error-pages/502/index.html`

The only structural change for each file: wrap the loose `<p class="eyebrow">` and `<div class="status">` in a `<div class="page-header">`.

- [ ] **Step 1: Update 403/index.html**

Find:
```html
      <p class="eyebrow">CardArena Remote Stage</p>
      <div class="status">Authorization Required</div>
```
Replace with:
```html
      <div class="page-header">
        <p class="eyebrow">CardArena Remote Stage</p>
        <div class="status">Authorization Required</div>
      </div>
```

- [ ] **Step 2: Update 404/index.html**

Find:
```html
      <p class="eyebrow">CardArena Remote Stage</p>
      <div class="status">Route Missing</div>
```
Replace with:
```html
      <div class="page-header">
        <p class="eyebrow">CardArena Remote Stage</p>
        <div class="status">Route Missing</div>
      </div>
```

- [ ] **Step 3: Update 500/index.html**

Find:
```html
      <p class="eyebrow">CardArena Remote Stage</p>
      <div class="status">Service Failure</div>
```
Replace with:
```html
      <div class="page-header">
        <p class="eyebrow">CardArena Remote Stage</p>
        <div class="status">Service Failure</div>
      </div>
```

- [ ] **Step 4: Update 502/index.html**

Find:
```html
      <p class="eyebrow">CardArena Remote Stage</p>
      <div class="status">Upstream Unavailable</div>
```
Replace with:
```html
      <div class="page-header">
        <p class="eyebrow">CardArena Remote Stage</p>
        <div class="status">Upstream Unavailable</div>
      </div>
```

- [ ] **Step 5: Verify all four error pages**

Open each file in Chrome at 1280×720 and 720×1280.
Expected at both sizes:
- Eyebrow text on the left, coloured status chip on the right, same line
- Error code large and prominent
- Two info blocks side-by-side (landscape) / stacked (portrait)
- Action buttons visible
- No scrollbar

- [ ] **Step 6: Commit**

```bash
git add src/resources/pages/error-pages/403/index.html \
        src/resources/pages/error-pages/404/index.html \
        src/resources/pages/error-pages/500/index.html \
        src/resources/pages/error-pages/502/index.html
git commit -m "feat: add page-header to all error pages"
```

---

## Task 6: Update boot-ready HTML

**Files:**
- Modify: `src/resources/pages/boot-ready/index.html`

- [ ] **Step 1: Wrap eyebrow + status in `.page-header`**

Find:
```html
      <p class="eyebrow">CardArena Remote Stage</p>
      <div class="status">Boot complete · API online</div>
```
Replace with:
```html
      <div class="page-header">
        <p class="eyebrow">CardArena Remote Stage</p>
        <div class="status">Boot complete · API online</div>
      </div>
```

- [ ] **Step 2: Verify boot-ready at 1280×720 (landscape)**

Open `src/resources/pages/boot-ready/index.html` in Chrome at 1280×720.
Expected:
- Eyebrow left, green status chip right, same line
- `READY` code large and prominent
- Two-column hero: copy + buttons left, Signal card right
- Footer bar at bottom of card
- No scrollbar

- [ ] **Step 3: Verify boot-ready at 720×1280 (portrait)**

Set DevTools to 720×1280.
Expected:
- Single-column layout
- `READY` code, headline, copy, buttons stacked
- Status card below as three horizontal metric tiles (Online / Armed / Ready)
- No scrollbar

- [ ] **Step 4: Commit**

```bash
git add src/resources/pages/boot-ready/index.html
git commit -m "feat: add page-header to boot-ready page"
```

---

## Task 7: Cross-page smoke check

- [ ] **Step 1: Check all pages at 1920×1080**

Open each of the 5 pages at 1920×1080. Expected: card centered, all content visible, no scroll, no clipped content.

- [ ] **Step 2: Check all pages at 1280×720**

Repeat at 1280×720. This is the tightest expected landscape resolution.
Expected: same as above — content fits, no scrollbar.

- [ ] **Step 3: Check all pages at 720×1280**

Repeat at 720×1280.
Expected: portrait single-column layout, no scrollbar.

- [ ] **Step 4: Check `prefers-reduced-motion`**

In DevTools → Rendering → Emulate CSS media feature `prefers-reduced-motion: reduce`.
Expected: all animations frozen, no visual glitches, layout unchanged.
