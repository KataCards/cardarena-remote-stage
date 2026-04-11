from __future__ import annotations

from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI

from src.api.registry import KioskRegistry
from src.config import get_settings
from src.kiosk.kiosk.factory.base import KioskFactory


class KioskStartupService:
    """Owns the kiosk lifecycle: build → register → start → (yield) → stop."""

    def __init__(self, registry: KioskRegistry, factory: KioskFactory) -> None:
        self._registry = registry
        self._factory = factory

    def build_lifespan(self):
        """Return the asynccontextmanager lifespan for FastAPI(lifespan=...)."""

        @asynccontextmanager
        async def lifespan(app: FastAPI):  # noqa: ARG001
            settings = get_settings()
            kiosk = self._factory.build(settings)
            self._registry.register(str(uuid4()), kiosk)
            for current_kiosk in self._registry.list_all().values():
                await current_kiosk.start()
            yield
            for current_kiosk in self._registry.list_all().values():
                await current_kiosk.stop()

        return lifespan
