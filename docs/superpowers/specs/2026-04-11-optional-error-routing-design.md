# Optional Error Page Routing

**Date:** 2026-04-11

## Summary

Make automatic navigation to premade error pages opt-out via an environment variable, defaulting to enabled.

## Background

When the Playwright browser receives an HTTP error response on the main frame (e.g. 404, 502), `PlaywrightKiosk._on_error` navigates the browser to a local `file://` error page configured via `kiosk_error_pages_dir`. This behaviour is always active if an error map is loaded. Some deployments want to suppress this routing — letting the browser display its own error state or leaving the page as-is.

There is also a latent bug: if `kiosk_error_pages_dir` is not set, the `on_error` callback is still wired but the `error_map` is empty, causing `handle_error()` to raise `KeyError` on any error response.

## Design

### New setting — `src/config.py`

```python
kiosk_error_routing: bool = True
```

- Environment variable: `KIOSK_ERROR_ROUTING`
- Default: `true` (no change in behaviour for existing deployments)
- When `false`: error responses are not intercepted; the browser shows whatever it shows

### Factory change — `src/kiosk/kiosk/factory/playwright.py`

Guard error map construction behind the new setting:

```python
if settings.kiosk_error_routing and settings.kiosk_error_pages_dir:
    resources, error_map = build_error_map(settings.kiosk_error_pages_dir)
else:
    resources, error_map = {}, {}
```

### Kiosk init change — `src/kiosk/kiosk/playwright.py`

Wire `on_error` only when `error_map` is non-empty (also fixes the latent KeyError bug):

```python
def model_post_init(self, _: Any) -> None:
    if self.engine.error_map:
        self.engine.on_error = self._on_error
```

## Behaviour Matrix

| `KIOSK_ERROR_ROUTING` | `kiosk_error_pages_dir` set | Result |
|---|---|---|
| `true` (default) | yes | Error pages loaded, callback wired — current behaviour |
| `true` (default) | no | Empty maps, no callback wired — previously had latent bug, now clean |
| `false` | yes or no | Empty maps, no callback wired — errors not intercepted |

## Files Changed

| File | Change |
|---|---|
| `src/config.py` | Add `kiosk_error_routing: bool = True` |
| `src/kiosk/kiosk/factory/playwright.py` | Guard `build_error_map` behind setting |
| `src/kiosk/kiosk/playwright.py` | Only wire `on_error` when `error_map` is non-empty |

## Testing

- Unit test: factory builds empty error_map when `kiosk_error_routing=False`
- Unit test: `model_post_init` does not wire `on_error` when `error_map` is empty
- Unit test: existing behaviour unchanged when `kiosk_error_routing=True` and dir is set
