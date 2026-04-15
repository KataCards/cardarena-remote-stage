from __future__ import annotations

from fastapi import APIRouter, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import uvicorn
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.api.registry import KioskRegistry
from src.api.routes.control import build_router as build_control_router
from src.api.routes.health import build_router as build_health_router
from src.api.routes.kiosks import build_router as build_kiosks_router
from src.api.routes.schedule import build_router as build_schedule_router
from src.api.scheduler import KioskScheduler
from src.config import get_settings
from src.kiosk.kiosk.factory.playwright import PlaywrightKioskFactory
from src.middleware import RequestContextMiddleware
from src.security.config import get_settings as get_security_settings
from src.startup import KioskStartupService
from src.utils import configure_logging
from src.utils.exceptions.handlers import (
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)


# -------------------------------------------------------------------------
# Core Services
# -------------------------------------------------------------------------

registry = KioskRegistry()
scheduler = KioskScheduler(registry)
startup_service = KioskStartupService(registry, PlaywrightKioskFactory())


# -------------------------------------------------------------------------
# Security Router Setup
# -------------------------------------------------------------------------


def build_security_router_if_enabled() -> APIRouter | None:
    security_settings = get_security_settings()
    if security_settings.security_provider != "api_key":
        return None

    from src.security.providers.api_keys.db import ApiKeyDatabase
    from src.security.providers.api_keys.repository import ApiKeyRepository
    from src.security.providers.api_keys.router import build_router as build_security_router

    # NOTE: A second ApiKeyDatabase connection is expected here (separate from
    # the one used by src/security/dependencies.py). Both connections target
    # the same SQLite file intentionally: the CRUD router needs its own repo,
    # while the auth provider in dependencies.py manages its own.
    db = ApiKeyDatabase(security_settings.apikey_db_path)
    db.initialise()
    repo = ApiKeyRepository(db, security_settings.apikey_secret.get_secret_value())
    return build_security_router(repo)


security_router = build_security_router_if_enabled()


# -------------------------------------------------------------------------
# FastAPI App
# -------------------------------------------------------------------------

app = FastAPI(lifespan=startup_service.build_lifespan())


@app.exception_handler(StarletteHTTPException)
async def _http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    return await http_exception_handler(request, exc)


@app.exception_handler(RequestValidationError)
async def _validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    return await validation_exception_handler(request, exc)


@app.exception_handler(Exception)
async def _unhandled_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    return await unhandled_exception_handler(request, exc)


# -------------------------------------------------------------------------
# Middleware Registration
# -------------------------------------------------------------------------

app.add_middleware(RequestContextMiddleware)


# -------------------------------------------------------------------------
# Route Registration
# -------------------------------------------------------------------------

if security_router is not None:
    app.include_router(security_router)
app.include_router(build_health_router(registry))
app.include_router(build_kiosks_router(registry))
app.include_router(build_control_router(registry))
app.include_router(build_schedule_router(registry, scheduler))


# -------------------------------------------------------------------------
# Entrypoint
# -------------------------------------------------------------------------

def main() -> None:
    settings = get_settings()
    configure_logging(settings.log_level, settings.log_format)
    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=False,
        log_config=None,
    )


if __name__ == "__main__":
    main()