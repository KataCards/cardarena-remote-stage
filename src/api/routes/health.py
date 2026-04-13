from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter

from .openapi import error_responses

if TYPE_CHECKING:
    from ..registry import KioskRegistry


def build_router(registry: "KioskRegistry") -> APIRouter:
    """Build the health-check router."""
    router = APIRouter(
        tags=["Health"],
        responses=error_responses(500),
    )

    @router.get(
        "/health",
        response_model=dict[str, int | str],
        summary="API health check",
        responses={
            200: {
                "description": "API is reachable and returns current kiosk count.",
                "content": {
                    "application/json": {
                        "example": {"status": "ok", "kiosk_count": 1}
                    }
                },
            }
        },
    )
    async def health() -> dict[str, int | str]:
        """Return a basic API health snapshot."""
        return {"status": "ok", "kiosk_count": len(registry.list_all())}

    return router
