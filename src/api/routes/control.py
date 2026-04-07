from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response

from ..models import NavigateRequest
from ...security import Scope, require_scope

if TYPE_CHECKING:
    from ..registry import KioskRegistry


def build_router(registry: "KioskRegistry") -> APIRouter:
    """Build kiosk control routes."""
    router = APIRouter()

    @router.post("/kiosks/{uuid}/navigate", status_code=204)
    async def navigate(
        uuid: str,
        body: NavigateRequest,
        _=Depends(require_scope(Scope.CONTROL)),
    ) -> Response:
        kiosk = registry.get(uuid)
        if kiosk is None:
            raise HTTPException(status_code=404, detail=f"Kiosk not found: {uuid}")
        success = await kiosk.navigate(body.url)
        if not success:
            raise HTTPException(status_code=500, detail="Kiosk operation failed")
        return Response(status_code=204)

    @router.post("/kiosks/{uuid}/reload", status_code=204)
    async def reload(
        uuid: str,
        _=Depends(require_scope(Scope.CONTROL)),
    ) -> Response:
        kiosk = registry.get(uuid)
        if kiosk is None:
            raise HTTPException(status_code=404, detail=f"Kiosk not found: {uuid}")
        success = await kiosk.reload()
        if not success:
            raise HTTPException(status_code=500, detail="Kiosk operation failed")
        return Response(status_code=204)

    return router
