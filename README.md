# cardarena-remote-stage

Part of the [CardArena](https://github.com/KataCards) tournament ecosystem.

cardarena-remote-stage is a self-hosted, remotely controllable browser kiosk system built in Python. It exposes a secured REST API that lets a frontend, automation system, or operator control a browser over the network in real time — purpose-built for driving tournament stage displays in the CardArena ecosystem.

The design is built around three independently pluggable layers. Each layer is defined by an abstract base class; concrete implementations are selected at startup via environment variable. Swapping an implementation — browser engine, auth backend, or any future layer — requires no changes outside that layer.

- **Browser engine** (`src/kiosk/`) — abstract browser control surface owning lifecycle, navigation, interaction (click, scroll, type, key press), screenshot capture, and error page handling. Coordinate-based, no DOM or selector access by design. Active implementation: Playwright. Additional engines are selectable via `KIOSK_ENGINE` as they are added.
- **Security** (`src/security/`) — abstract auth layer upstream of the API. Active provider selected at startup via `SECURITY_PROVIDER`. Implemented: API key (SQLite-backed, HMAC-hashed, scope-based) and IP whitelist. Adding a provider means implementing two methods.
- **API** (`src/api/`) — FastAPI application exposing the full control surface over HTTP. Every endpoint is scope-protected. Owns scheduling, ad breaks, and the kiosk registry. Never touches the browser engine directly.

---

## Requirements

- Python 3.13+
- [`uv`](https://docs.astral.sh/uv/) — used for all dependency and script management

---

## Installation

```bash
uv sync
uv run playwright install chromium
cp .env.example .env
# Edit .env and fill in required values (see Configuration)
```

---

## Configuration

All configuration is read from environment variables or a `.env` file in the project root.

### Application (`src/config.py`)

| Variable | Description | Default | Required |
|---|---|---|---|
| `HOST` | Network interface to bind | `0.0.0.0` | No |
| `PORT` | Port to listen on | `8000` | No |
| `KIOSK_DEFAULT_URL` | URL the browser opens on startup. Accepts `https://`, `http://`, `file:///`, or a relative path resolved from the project root. | `https://example.com` | No |
| `KIOSK_NAME` | Human-readable label for this kiosk instance | `default` | No |
| `KIOSK_HEADLESS` | Run the browser in headless mode | `false` | No |
| `KIOSK_FULLSCREEN` | Launch the browser in fullscreen / kiosk mode | `false` | No |
| `KIOSK_ALLOWED_URLS` | Comma-separated URL whitelist. Navigation to any URL not in this list is silently rejected. Leave empty to allow all URLs. | _(empty — all allowed)_ | No |
| `KIOSK_ERROR_PAGES_DIR` | Path to a directory of HTTP error page overrides. See [Error pages](#error-pages). | _(none)_ | No |
| `KIOSK_ERROR_ROUTING` | Enable routing HTTP error responses to local error pages. Requires `KIOSK_ERROR_PAGES_DIR`. | `true` | No |

### Playwright Factory (`src/kiosk/kiosk/factory/config.py`)

| Variable | Description | Default | Required |
|---|---|---|---|
| `KIOSK_PLAYWRIGHT_BROWSER_TYPE` | Playwright browser engine. Supported: `chromium`, `firefox`, `webkit`. | `chromium` | No |
| `KIOSK_PLAYWRIGHT_LAUNCH_ARGS` | Space-separated Playwright launch args (for example: `--window-size=1920,1080 --incognito`). Only explicit args are passed. | _(empty)_ | No |

### Security (`src/security/config.py`)

| Variable | Description | Default | Required |
|---|---|---|---|
| `SECURITY_PROVIDER` | Authentication backend. Supported: `api_key`, `ip_whitelist` | `api_key` | No |
| `APIKEY_SECRET` | HMAC secret used to hash API keys. Generate with `openssl rand -hex 32`. | _(none)_ | Yes (when `SECURITY_PROVIDER=api_key`) |
| `APIKEY_DB_PATH` | Path to the SQLite database storing API keys | `./security.db` | No |
| `APIKEY_DB_TYPE` | Database type (currently only `sqlite` is supported) | `sqlite` | No |
| `ALLOWED_IPS` | Comma-separated list of allowed client IP addresses | _(empty)_ | Yes (when `SECURITY_PROVIDER=ip_whitelist`) |

---

## Running

```bash
uv run kiosk
```

The API is available at `http://HOST:PORT`. Interactive API docs (Swagger UI) are at `/docs`.

---

## API key management

The `apikey` CLI manages keys when `SECURITY_PROVIDER=api_key`. Keys are scoped — a key must hold the appropriate scope to access a given endpoint. Scopes: `read`, `control`, `admin`.

**Create a key**

```bash
uv run apikey create --name dashboard --scopes read,control
```

With an expiry date:

```bash
uv run apikey create --name ci-runner --scopes control --expires 2025-12-31T23:59:59
```

**List all keys**

```bash
uv run apikey list
```

**Revoke a key** (marks as revoked; key remains in the database)

```bash
uv run apikey revoke --name dashboard
```

**Permanently delete a key**

```bash
uv run apikey delete --name dashboard
```

The raw key is shown only once at creation time. Store it immediately — it cannot be retrieved again.

---

## API reference

All endpoints require the `X-API-Key` header (or pass the client IP check for `ip_whitelist`). The scope column indicates the minimum scope required.

### Health

| Method | Path | Scope | Description |
|---|---|---|---|
| `GET` | `/health` | None | Returns API status and registered kiosk count |

### Kiosk status

| Method | Path | Scope | Description |
|---|---|---|---|
| `GET` | `/kiosks` | `read` | List all registered kiosks (summary) |
| `GET` | `/kiosks/{uuid}` | `read` | Get full status for a specific kiosk |

### Kiosk control

All control endpoints return `204 No Content` on success.

| Method | Path | Scope | Description |
|---|---|---|---|
| `POST` | `/kiosks/{uuid}/navigate` | `control` | Navigate to a URL (`{ "url": "..." }`) |
| `POST` | `/kiosks/{uuid}/reload` | `control` | Reload the current page |
| `POST` | `/kiosks/{uuid}/start` | `control` | Start the kiosk browser |
| `POST` | `/kiosks/{uuid}/stop` | `control` | Stop the kiosk browser |
| `POST` | `/kiosks/{uuid}/restart` | `control` | Stop then start the kiosk browser |
| `POST` | `/kiosks/{uuid}/go-back` | `control` | Navigate back in browser history |
| `POST` | `/kiosks/{uuid}/go-forward` | `control` | Navigate forward in browser history |
| `POST` | `/kiosks/{uuid}/go-home` | `control` | Navigate to `KIOSK_DEFAULT_URL` |
| `POST` | `/kiosks/{uuid}/click` | `control` | Click at coordinates (`{ "x": 0, "y": 0 }`) |
| `POST` | `/kiosks/{uuid}/type-text` | `control` | Type text into the focused element (`{ "text": "..." }`) |
| `POST` | `/kiosks/{uuid}/scroll` | `control` | Scroll the page (`{ "direction": "down", "amount": 300 }`) — directions: `up`, `down`, `left`, `right` |
| `POST` | `/kiosks/{uuid}/press-key` | `control` | Press a key (`{ "key": "Enter" }`) — Playwright key names |
| `POST` | `/kiosks/{uuid}/screenshot` | `control` | Returns a PNG screenshot as a file download |

### Schedule

| Method | Path | Scope | Description |
|---|---|---|---|
| `POST` | `/kiosks/{uuid}/schedule` | `control` | Start a continuous content rotation loop |
| `POST` | `/kiosks/{uuid}/schedule/cancel` | `control` | Stop the running schedule loop |
| `POST` | `/kiosks/{uuid}/ad-break` | `control` | Navigate to an ad URL for a fixed duration, then return |

**Schedule request body:**

```json
{
  "entries": [
    { "url": "https://example.com", "duration_seconds": 30, "order": 0 },
    { "url": "https://status.example.com", "duration_seconds": 10, "order": 1 }
  ]
}
```

**Ad break request body:**

```json
{ "url": "https://ads.example.com", "duration_seconds": 15 }
```

Entries are played in `order` sequence, looping indefinitely until cancelled. A running schedule is replaced (not stacked) if a new one is posted.

### Security key management

| Method | Path | Scope | Description |
|---|---|---|---|
| `POST` | `/security/keys` | `admin` | Create a new API key |
| `GET` | `/security/keys` | `admin` | List all API keys |
| `DELETE` | `/security/keys/{name}` | `admin` | Revoke a key |
| `DELETE` | `/security/keys/{name}/hard` | `admin` | Permanently delete a key |

---

## Error pages

When `KIOSK_ERROR_ROUTING=true` and `KIOSK_ERROR_PAGES_DIR` is set, the kiosk intercepts main-frame HTTP error responses and navigates to a local HTML page instead.

The directory must follow this structure — one subdirectory per HTTP status code, each containing an `index.html`:

```
error-pages/
  404/
    index.html
  500/
    index.html
  503/
    index.html
```

Any subdirectory whose name is not a valid HTTP status code (100–599) is ignored. Any status code directory without an `index.html` is also ignored.

---

## Architecture

```
┌─────────────────────────────────────────┐
│           API layer  (FastAPI)          │
│  routes · registry · scheduler · scopes │
└────────────────────┬────────────────────┘
                     │  Kiosk ABC
┌────────────────────▼────────────────────┐
│         Kiosk abstraction layer         │
│  whitelist · retry · URL tracking       │
│  error routing · lifecycle              │
└──────────┬─────────────────┬────────────┘
           │ Engine ABC       │ Controls ABC
┌──────────▼──────┐  ┌───────▼────────────┐
│  Browser engine │  │  Browser controls  │
│  launch · close │  │  navigate · click  │
│  screenshot     │  │  scroll · type     │
│  cookies        │  │  press · reload    │
└─────────────────┘  └────────────────────┘
```

The architecture is defined by abstract base classes. Concrete implementations are chosen at startup. Every pluggable seam is enforced by Python's `ABC` — not convention, not documentation, not trust.

---

### Browser engine layer

The browser engine is defined by four abstract classes. All four must be implemented together; they are the complete contract for a browser backend.

| Abstract class | File | Responsibility |
|---|---|---|
| `Engine` | `src/kiosk/engine/base.py` | Browser lifecycle (`launch`, `close`), page state (`get_current_url`, `screenshot`), cookie storage, and the error-callback hook |
| `Controls` | `src/kiosk/controls/base.py` | User interaction: `navigate`, `reload`, `go_back`, `go_forward`, `click`, `type_text`, `scroll`, `press_key`, `wait_for_navigation` |
| `Kiosk` | `src/kiosk/kiosk/base.py` | Orchestration layer that owns all invariants the API relies on (see below) |
| `KioskFactory` | `src/kiosk/kiosk/factory/base.py` | Constructs a `Kiosk` from application `Settings` — one factory per engine implementation |

Current concrete implementation: `PlaywrightEngine`, `PlaywrightControls`, `PlaywrightKiosk`, `PlaywrightKioskFactory` — all under `src/kiosk/`.

**Adding a new engine** means implementing all four classes and registering the factory. The API, security, scheduler, and registry require no changes. Once multiple engines exist, the active one will be selected via `KIOSK_ENGINE`.

#### Invariants enforced by the `Kiosk` base class

The `Kiosk` base class holds logic that all engine implementations inherit and cannot bypass. These are the guarantees the API depends on regardless of which engine is running:

- **URL whitelist** — `Kiosk.navigate()` checks `allowed_urls` before delegating to `Controls`. No engine implementation can route around it.
- **URL state consistency** — `_sync_current_url()` is called after every navigation method in the base class. `current_url` is always accurate regardless of which method caused the navigation.
- **Error page routing** — the `Engine.on_error` callback is wired only when `error_map` is non-empty. Error routing is opt-in and never fires for unconfigured status codes.
- **Retry on startup** — `_navigate_with_retry()` applies exponential backoff for the initial navigation. All `Kiosk` subclasses inherit this without reimplementing it.

---

### Security layer

The security layer is defined by one abstract class.

| Abstract class | File | Methods to implement |
|---|---|---|
| `SecurityProvider` | `src/security/base/provider.py` | `openapi_scheme` — the FastAPI security scheme (used for `/docs`); `verify(credentials, request) -> Principal` — authenticate the request and return a scoped principal, or raise `HTTPException` |

The `Principal` returned by `verify` carries a list of `Scope` values (`read`, `control`, `admin`). These are what route-level `require_scope()` guards check. The provider decides which scopes to grant — the API does not care how.

Current concrete implementations: `ApiKeyProvider` (HMAC-SHA256-hashed keys in SQLite), `IpWhitelistProvider` (client IP check, grants all scopes).

**Adding a new provider:**

1. Subclass `SecurityProvider` and implement `openapi_scheme` and `verify`.
2. Add a branch to `get_active_provider()` in `src/security/config.py`.

Nothing else changes. The new provider is automatically applied to every existing and future route.

**Why security sits upstream of the API.** The provider is resolved once at startup and injected as a FastAPI dependency. Adding a route automatically inherits auth — there is no way to accidentally ship an unauthenticated endpoint. The API layer has no knowledge of which provider is active.

---

### API layer

Routes follow a consistent factory pattern: each concern is a `build_router()` function that takes the registry (and optionally the scheduler) and returns an `APIRouter`. The composition root (`src/main.py`) wires them together.

**Adding a new route group:**

1. Create `src/api/routes/my_feature.py` with a `build_router(registry) -> APIRouter` function.
2. Guard each endpoint with `Depends(require_scope(Scope.CONTROL))` (or `READ` / `ADMIN`).
3. Register in `src/main.py`: `app.include_router(build_my_feature_router(registry))`.

**Why the API never touches the engine directly.** Routes call methods on `Kiosk`, never on `Engine` or `Controls`. The `Kiosk` abstraction is the API's only contract with the browser. All invariants — whitelist, URL sync, retry, error routing — live there. If the API bypassed it, those guarantees would silently stop applying.

**Why coordinate-based control.** The API controls a physical screen shown to end users, not a headless scraping session. Selector or DOM access would couple control logic to specific page layouts, expose the internal structure of displayed pages, and create a security surface. Coordinates are the correct abstraction for a screen-control system.
