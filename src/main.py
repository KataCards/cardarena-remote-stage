from __future__ import annotations

from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI
import uvicorn

from src.api.registry import KioskRegistry
from src.api.routes.control import build_router as build_control_router
from src.api.routes.health import build_router as build_health_router
from src.api.routes.kiosks import build_router as build_kiosks_router
from src.api.routes.schedule import build_router as build_schedule_router
from src.api.scheduler import KioskScheduler
from src.config import get_settings
from src.kiosk.engine.playwright import PlaywrightEngine
from src.kiosk.kiosk.playwright import PlaywrightKiosk
from src.security.config import get_settings as get_security_settings
from src.utils import build_error_map

# ---------------------------------------------------------------------------
# Kiosk registry (module-level — no kiosk construction here)
# ---------------------------------------------------------------------------
registry = KioskRegistry()
scheduler = KioskScheduler(registry)

_sec = get_security_settings()
_security_router = None

if _sec.security_provider == "api_key":
    from src.security.providers.api_keys.db import ApiKeyDatabase
    from src.security.providers.api_keys.repository import ApiKeyRepository
    from src.security.providers.api_keys.router import build_router as build_security_router

    # NOTE: A second ApiKeyDatabase connection is expected here (separate from
    # the one used by src/security/dependencies.py). Both connections target
    # the same SQLite file intentionally: the CRUD router needs its own repo,
    # while the auth provider in dependencies.py manages its own.
    _db = ApiKeyDatabase(_sec.apikey_db_path)
    _db.initialise()
    _repo = ApiKeyRepository(_db, _sec.apikey_secret.get_secret_value())
    _security_router = build_security_router(_repo)


# ---------------------------------------------------------------------------
# Lifespan — kiosk construction happens here to avoid import-time failures:
# 1. PlaywrightKiosk validates default_page URL regex at construction time
# 2. PlaywrightEngine validates that resource file paths exist at construction time
# Both would fail at import time if env vars are missing or misconfigured.
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001
    settings = get_settings()
    launch_args = ["--kiosk", "--disable-infobars", "--no-first-run"] if settings.kiosk_fullscreen else []

    if settings.kiosk_error_pages_dir:
        resources, error_map = build_error_map(settings.kiosk_error_pages_dir)
    else:
        resources = {"error": settings.kiosk_error_page} if settings.kiosk_error_page else {}
        error_map = {404: "error", 500: "error"} if settings.kiosk_error_page else {}

    primary_engine = PlaywrightEngine(
        engine_type="playwright",
        resources=resources,
        error_map=error_map,
        headless=settings.kiosk_headless,
        fullscreen=settings.kiosk_fullscreen,
        launch_args=launch_args,
    )
    primary_kiosk = PlaywrightKiosk(
        engine=primary_engine,
        default_page=settings.kiosk_default_url,
        kiosk_name=settings.kiosk_name,
        allowed_urls=settings.kiosk_allowed_urls,
    )
    firefox_engine = PlaywrightEngine(
        engine_type="playwright",
        browser_type="firefox",
        resources=resources,
        error_map=error_map,
        headless=settings.kiosk_headless,
        fullscreen=settings.kiosk_fullscreen,
        launch_args=launch_args,
    )
    firefox_kiosk = PlaywrightKiosk(
        engine=firefox_engine,
        default_page=settings.kiosk_default_url,
        kiosk_name=f"{settings.kiosk_name}-firefox",
        allowed_urls=settings.kiosk_allowed_urls,
    )

    registry.register(str(uuid4()), primary_kiosk)
    registry.register(str(uuid4()), firefox_kiosk)
    for current_kiosk in registry.list_all().values():
        await current_kiosk.start()
    yield
    for current_kiosk in registry.list_all().values():
        await current_kiosk.stop()


# ---------------------------------------------------------------------------
# App assembly
# ---------------------------------------------------------------------------
app = FastAPI(lifespan=lifespan)
if _security_router is not None:
    app.include_router(_security_router)
app.include_router(build_health_router(registry))
app.include_router(build_kiosks_router(registry))
app.include_router(build_control_router(registry))
app.include_router(build_schedule_router(registry, scheduler))


def main() -> None:
    """Run the FastAPI application with uvicorn."""
    settings = get_settings()
    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=False,
    )


if __name__ == "__main__":
    main()
