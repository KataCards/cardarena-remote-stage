from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, HTTPException

from ..models import KioskStatus, KioskSummary
from ...security import Scope, require_scope

if TYPE_CHECKING:
    from ..registry import KioskRegistry


def build_router(registry: "KioskRegistry") -> APIRouter:
    """Build read-only kiosk routes."""
    router = APIRouter()

    @router.get("/kiosks", response_model=list[KioskSummary])
    async def list_kiosks(_=Depends(require_scope(Scope.READ))) -> list[KioskSummary]:
        summaries = []
        for uuid, kiosk in registry.list_all().items():
            summaries.append(
                KioskSummary(
                    uuid=uuid,
                    engine_type=kiosk.engine.engine_type,
                    is_running=kiosk.is_running,
                    current_url=kiosk.current_url,
                )
            )
        return summaries

    @router.get("/kiosks/{uuid}", response_model=KioskStatus)
    async def get_kiosk(uuid: str, _=Depends(require_scope(Scope.READ))) -> KioskStatus:
        kiosk = registry.get(uuid)
        if kiosk is None:
            raise HTTPException(status_code=404, detail=f"Kiosk not found: {uuid}")
        return KioskStatus(
            uuid=uuid,
            engine_type=kiosk.engine.engine_type,
            current_url=kiosk.current_url,
            is_running=kiosk.is_running,
        )

    return router
