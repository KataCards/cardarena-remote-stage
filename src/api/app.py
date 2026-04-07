from __future__ import annotations

from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI

from src.config import get_settings as get_api_settings
from src.kiosk.engine.playwright import PlaywrightEngine
from src.kiosk.kiosk.playwright import PlaywrightKiosk
from src.security.api_keys.db import ApiKeyDatabase
from src.security.api_keys.repository import ApiKeyRepository
from src.security.api_keys.router import build_router as build_security_router
from src.security.config import get_settings as get_security_settings
from src.api.registry import KioskRegistry
from src.api.routes.control import build_router as build_control_router
from src.api.routes.health import build_router as build_health_router
from src.api.routes.kiosks import build_router as build_kiosks_router
from src.api.routes.schedule import build_router as build_schedule_router
from src.api.scheduler import KioskScheduler

# ---------------------------------------------------------------------------
# Kiosk registry (module-level — no kiosk construction here)
# ---------------------------------------------------------------------------
registry = KioskRegistry()
scheduler = KioskScheduler(registry)

# NOTE: A second ApiKeyDatabase connection is expected here (separate from
# the one used by src/security/dependencies.py). Both connections target
# the same SQLite file intentionally: the CRUD router needs its own repo,
# while the auth provider in dependencies.py manages its own.
_sec = get_security_settings()
_db = ApiKeyDatabase(_sec.apikey_db_path)
_db.initialise()
_repo = ApiKeyRepository(_db)


# ---------------------------------------------------------------------------
# Lifespan — kiosk construction happens here to avoid import-time failures:
# 1. PlaywrightKiosk validates default_page URL regex at construction time
# 2. PlaywrightEngine validates that resource file paths exist at construction time
# Both would fail at import time if env vars are missing or misconfigured.
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001
    _api = get_api_settings()

    _engine = PlaywrightEngine(
        engine_type="playwright",
        resources={"error": _api.kiosk_error_page} if _api.kiosk_error_page else {},
        error_map={404: "error", 500: "error"} if _api.kiosk_error_page else {},
        headless=_api.kiosk_headless,
    )
    _kiosk = PlaywrightKiosk(
        engine=_engine,
        default_page=_api.kiosk_default_url,
        kiosk_name=_api.kiosk_name,
        allowed_urls=_api.kiosk_allowed_urls,
    )
    registry.register(str(uuid4()), _kiosk)
    for kiosk in registry.list_all().values():
        await kiosk.start()
    yield
    for kiosk in registry.list_all().values():
        await kiosk.stop()


# ---------------------------------------------------------------------------
# App assembly
# ---------------------------------------------------------------------------
app = FastAPI(lifespan=lifespan)
app.include_router(build_security_router(_repo))
app.include_router(build_health_router(registry))
app.include_router(build_kiosks_router(registry))
app.include_router(build_control_router(registry))
app.include_router(build_schedule_router(registry, scheduler))
