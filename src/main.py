from __future__ import annotations

from time import perf_counter
from uuid import uuid4

from fastapi import APIRouter, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import uvicorn
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.types import ASGIApp, Receive, Scope, Send
from structlog.contextvars import bind_contextvars, unbind_contextvars

from src.api.registry import KioskRegistry
from src.api.routes.control import build_router as build_control_router
from src.api.routes.health import build_router as build_health_router
from src.api.routes.kiosks import build_router as build_kiosks_router
from src.api.routes.schedule import build_router as build_schedule_router
from src.api.scheduler import KioskScheduler
from src.config import get_settings
from src.kiosk.kiosk.factory.playwright import PlaywrightKioskFactory
from src.security.config import get_settings as get_security_settings
from src.startup import KioskStartupService
from src.utils import configure_logging, get_logger
from src.utils.exceptions.handlers import (
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)


logger = get_logger(__name__)

registry = KioskRegistry()
scheduler = KioskScheduler(registry)

_sec = get_security_settings()
_security_router: APIRouter | None = None

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

_startup = KioskStartupService(registry, PlaywrightKioskFactory())

app = FastAPI(lifespan=_startup.build_lifespan())


# --- Pure ASGI middleware for request context and logging
class RequestContextMiddleware:
    """Binds request_id to contextvars before exception handlers run, captures real status codes, and logs requests."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Bind request_id before calling app — includes exception handlers
        request_id = str(uuid4())
        bind_contextvars(request_id=request_id)
        started = perf_counter()
        status_code = 500
        method = scope.get("method", "")
        path = scope.get("path", "")

        async def send_with_status(message: dict) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, send_with_status)
        finally:
            duration_ms = round((perf_counter() - started) * 1000, 2)
            logger.info(
                "request",
                method=method,
                path=path,
                status_code=status_code,
                duration_ms=duration_ms,
            )
            unbind_contextvars("request_id")


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


# Register pure ASGI middleware to wrap entire stack including exception handlers
app.add_middleware(RequestContextMiddleware)


if _security_router is not None:
    app.include_router(_security_router)
app.include_router(build_health_router(registry))
app.include_router(build_kiosks_router(registry))
app.include_router(build_control_router(registry))
app.include_router(build_schedule_router(registry, scheduler))


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