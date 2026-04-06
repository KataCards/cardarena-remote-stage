"""Kiosk read routes — GET /kiosks and GET /kiosks/{uuid}."""
from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, HTTPException

from src.api.models.kiosk import KioskStatus, KioskSummary
from src.security.base.principal import Scope
from src.security.dependencies import require_scope

if TYPE_CHECKING:
    from src.api.registry import KioskRegistry


def build_router(registry: "KioskRegistry") -> APIRouter:
    router = APIRouter()

    @router.get("/kiosks", response_model=list[KioskSummary])
    async def list_kiosks(_=Depends(require_scope(Scope.READ))) -> list[KioskSummary]:
        summaries = []
        for uuid, kiosk in registry.list().items():
            try:
                url = await kiosk.engine.get_current_url()
            except RuntimeError:
                url = ""
            summaries.append(
                KioskSummary(uuid=uuid, is_running=kiosk.is_running, current_url=url)
            )
        return summaries

    @router.get("/kiosks/{uuid}", response_model=KioskStatus)
    async def get_kiosk(uuid: str, _=Depends(require_scope(Scope.READ))) -> KioskStatus:
        kiosk = registry.get(uuid)
        if kiosk is None:
            raise HTTPException(status_code=404, detail=f"Kiosk not found: {uuid}")
        try:
            url = await kiosk.engine.get_current_url()
        except RuntimeError:
            url = ""
        return KioskStatus(uuid=uuid, current_url=url, is_running=kiosk.is_running, error=None)

    return router
