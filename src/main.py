from __future__ import annotations

from fastapi import APIRouter, FastAPI
import uvicorn

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
