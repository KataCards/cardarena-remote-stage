from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter

if TYPE_CHECKING:
    from ..registry import KioskRegistry


def build_router(registry: "KioskRegistry") -> APIRouter:
    """Build the health-check router."""
    router = APIRouter()

    @router.get("/health")
    async def health() -> dict[str, int | str]:
        """Return a basic API health snapshot."""
        return {"status": "ok", "kiosk_count": len(registry.list_all())}

    return router
