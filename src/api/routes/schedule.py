"""Schedule routes — start/cancel schedule loops and run ad breaks."""
from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response

from src.api.models.schedule import AdBreak, ScheduleRequest
from src.security.base.principal import Scope
from src.security.dependencies import require_scope

if TYPE_CHECKING:
    from src.api.registry import KioskRegistry
    from src.api.scheduler import KioskScheduler


def build_router(registry: "KioskRegistry", scheduler: "KioskScheduler") -> APIRouter:
    router = APIRouter()

    @router.post("/kiosks/{uuid}/schedule", status_code=204)
    async def start_schedule(
        uuid: str,
        body: ScheduleRequest,
        _=Depends(require_scope(Scope.CONTROL)),
    ) -> Response:
        if registry.get(uuid) is None:
            raise HTTPException(status_code=404, detail=f"Kiosk not found: {uuid}")
        scheduler.run_schedule(uuid, body)
        return Response(status_code=204)

    @router.post("/kiosks/{uuid}/schedule/cancel", status_code=204)
    async def cancel_schedule(
        uuid: str,
        _=Depends(require_scope(Scope.CONTROL)),
    ) -> Response:
        if registry.get(uuid) is None:
            raise HTTPException(status_code=404, detail=f"Kiosk not found: {uuid}")
        scheduler.cancel(uuid)
        return Response(status_code=204)

    @router.post("/kiosks/{uuid}/ad-break", status_code=204)
    async def ad_break(
        uuid: str,
        body: AdBreak,
        _=Depends(require_scope(Scope.CONTROL)),
    ) -> Response:
        if registry.get(uuid) is None:
            raise HTTPException(status_code=404, detail=f"Kiosk not found: {uuid}")
        await scheduler.run_ad_break(uuid, body)
        return Response(status_code=204)

    return router
