"""Health check route — no authentication required."""
from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter

if TYPE_CHECKING:
    from src.api.registry import KioskRegistry


def build_router(registry: "KioskRegistry") -> APIRouter:
    router = APIRouter()

    @router.get("/health")
    async def health() -> dict[str, object]:
        return {"status": "ok", "kiosk_count": len(registry.list())}

    return router
