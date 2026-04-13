from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends

from ..models import ActivityEvent, KioskStatus, KioskSummary
from .openapi import error_responses
from .utils import get_kiosk_or_404
from ...security import Scope, require_scope
from src.utils import ErrorCode, raise_http

if TYPE_CHECKING:
    from ..registry import KioskRegistry


def build_router(registry: "KioskRegistry") -> APIRouter:
    """Build read-only kiosk routes."""
    router = APIRouter(responses=error_responses(401, 403, 404, 422))

    @router.get("/kiosks", response_model=list[KioskSummary], summary="List all kiosks")
    async def list_kiosks(_=Depends(require_scope(Scope.READ))) -> list[KioskSummary]:
        return [
            KioskSummary(
                uuid=uuid,
                engine_type=kiosk.engine.engine_type,
                is_running=kiosk.is_running,
                current_url=kiosk.current_url,
            )
            for uuid, kiosk in registry.list_all().items()
        ]

    @router.get("/kiosks/{uuid}", response_model=KioskStatus, summary="Get kiosk status")
    async def get_kiosk(uuid: str, _=Depends(require_scope(Scope.READ))) -> KioskStatus:
        kiosk = get_kiosk_or_404(registry, uuid)
        return KioskStatus(
            uuid=uuid,
            engine_type=kiosk.engine.engine_type,
            current_url=kiosk.current_url,
            is_running=kiosk.is_running,
        )

    @router.get(
        "/kiosks/{uuid}/history",
        response_model=list[ActivityEvent],
        summary="Get kiosk activity history",
    )
    async def get_history(
        uuid: str,
        _=Depends(require_scope(Scope.ADMIN)),
    ) -> list[ActivityEvent]:
        log = registry.get_log(uuid)
        if log is None:
            raise_http(
                404,
                ErrorCode.not_found,
                f"Kiosk not found: {uuid}",
                context={"kiosk_uuid": uuid},
            )
        return log.list_all()

    return router
