from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response

from ..models import AdBreak, ScheduleRequest
from .utils import get_kiosk_or_404
from ...security import Scope, require_scope

if TYPE_CHECKING:
    from ..registry import KioskRegistry
    from ..scheduler import KioskScheduler


def build_router(registry: "KioskRegistry", scheduler: "KioskScheduler") -> APIRouter:
    """Build schedule-management routes."""
    router = APIRouter()

    @router.post("/kiosks/{uuid}/schedule", status_code=204)
    async def start_schedule(
        uuid: str,
        body: ScheduleRequest,
        _=Depends(require_scope(Scope.CONTROL)),
    ) -> Response:
        get_kiosk_or_404(registry, uuid)
        # run_schedule is intentionally sync; it only creates the background task.
        scheduler.run_schedule(uuid, body)
        return Response(status_code=204)

    @router.post("/kiosks/{uuid}/schedule/cancel", status_code=204)
    async def cancel_schedule(
        uuid: str,
        _=Depends(require_scope(Scope.CONTROL)),
    ) -> Response:
        get_kiosk_or_404(registry, uuid)
        scheduler.cancel(uuid)
        return Response(status_code=204)

    @router.post("/kiosks/{uuid}/ad-break", status_code=204)
    async def ad_break(
        uuid: str,
        body: AdBreak,
        _=Depends(require_scope(Scope.CONTROL)),
    ) -> Response:
        get_kiosk_or_404(registry, uuid)
        await scheduler.run_ad_break(uuid, body)
        return Response(status_code=204)

    return router
