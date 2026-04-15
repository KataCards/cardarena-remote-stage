from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends
from fastapi.responses import Response

from ..models import AdBreak, ScheduleRequest
from .openapi import error_responses
from .utils import get_kiosk_or_404
from ...security import Scope, require_scope
from src.utils import ErrorCode, raise_http

if TYPE_CHECKING:
    from ..registry import KioskRegistry
    from ..scheduler import KioskScheduler


def build_router(registry: "KioskRegistry", scheduler: "KioskScheduler") -> APIRouter:
    """Build schedule-management routes."""
    router = APIRouter(responses=error_responses(401, 403, 404, 422, 500))

    @router.post("/kiosks/{uuid}/schedule", status_code=204, summary="Start content schedule")
    async def start_schedule(
        uuid: str,
        body: ScheduleRequest,
        _=Depends(require_scope(Scope.CONTROL)),
    ) -> Response:
        get_kiosk_or_404(registry, uuid)
        log = registry.get_log(uuid)
        # run_schedule is intentionally sync; it only creates the background task.
        try:
            scheduler.run_schedule(uuid, body)
        except (RuntimeError, ValueError):
            if log:
                log.record("schedule_started", success=False, entry_count=len(body.entries))
            raise_http(
                500,
                ErrorCode.operation_failed,
                "Kiosk operation failed",
                context={"kiosk_uuid": uuid},
            )
        if log:
            log.record("schedule_started", entry_count=len(body.entries))
        return Response(status_code=204)

    @router.post("/kiosks/{uuid}/schedule/cancel", status_code=204, summary="Cancel content schedule")
    async def cancel_schedule(
        uuid: str,
        _=Depends(require_scope(Scope.CONTROL)),
    ) -> Response:
        get_kiosk_or_404(registry, uuid)
        log = registry.get_log(uuid)
        try:
            was_cancelled = scheduler.cancel(uuid)
        except (RuntimeError, ValueError):
            if log:
                log.record("schedule_cancelled", success=False)
            raise_http(
                500,
                ErrorCode.operation_failed,
                "Kiosk operation failed",
                context={"kiosk_uuid": uuid},
            )
        if log:
            # Record actual result: success=True only if a schedule was actually cancelled
            log.record("schedule_cancelled", success=was_cancelled, was_running=was_cancelled)
        return Response(status_code=204)

    @router.post("/kiosks/{uuid}/ad-break", status_code=204, summary="Run ad break")
    async def ad_break(
        uuid: str,
        body: AdBreak,
        _=Depends(require_scope(Scope.CONTROL)),
    ) -> Response:
        get_kiosk_or_404(registry, uuid)
        log = registry.get_log(uuid)
        
        # Record start event in activity log
        if log:
            log.record("ad_break_started", url=body.url, duration_seconds=body.duration_seconds)
        
        try:
            await scheduler.run_ad_break(uuid, body)
        except (RuntimeError, ValueError):
            if log:
                log.record(
                    "ad_break_failed",
                    success=False,
                    url=body.url,
                    duration_seconds=body.duration_seconds,
                )
            raise_http(
                500,
                ErrorCode.operation_failed,
                "Kiosk operation failed",
                context={"kiosk_uuid": uuid},
            )
        
        # Record end event in activity log
        if log:
            log.record("ad_break_ended", url=body.url, duration_seconds=body.duration_seconds)
        
        return Response(status_code=204)

    return router