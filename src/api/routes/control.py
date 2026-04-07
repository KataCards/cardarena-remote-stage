from __future__ import annotations

import io
from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response, StreamingResponse

from ..models import (
    ClickRequest,
    NavigateRequest,
    PressKeyRequest,
    ScrollRequest,
    TypeTextRequest,
)
from ...security import Scope, require_scope

if TYPE_CHECKING:
    from ..registry import KioskRegistry


def build_router(registry: "KioskRegistry") -> APIRouter:
    """Build kiosk control routes."""
    router = APIRouter()

    def _get_kiosk_or_404(uuid: str):
        kiosk = registry.get(uuid)
        if kiosk is None:
            raise HTTPException(status_code=404, detail=f"Kiosk not found: {uuid}")
        return kiosk

    @router.post("/kiosks/{uuid}/navigate", status_code=204)
    async def navigate(
        uuid: str,
        body: NavigateRequest,
        _=Depends(require_scope(Scope.CONTROL)),
    ) -> Response:
        kiosk = _get_kiosk_or_404(uuid)
        success = await kiosk.navigate(body.url)
        if not success:
            raise HTTPException(status_code=500, detail="Kiosk operation failed")
        return Response(status_code=204)

    @router.post("/kiosks/{uuid}/reload", status_code=204)
    async def reload(
        uuid: str,
        _=Depends(require_scope(Scope.CONTROL)),
    ) -> Response:
        kiosk = _get_kiosk_or_404(uuid)
        success = await kiosk.reload()
        if not success:
            raise HTTPException(status_code=500, detail="Kiosk operation failed")
        return Response(status_code=204)

    @router.post("/kiosks/{uuid}/start", status_code=204)
    async def start(
        uuid: str,
        _=Depends(require_scope(Scope.CONTROL)),
    ) -> Response:
        kiosk = _get_kiosk_or_404(uuid)
        try:
            await kiosk.start()
        except RuntimeError:
            raise HTTPException(status_code=500, detail="Kiosk operation failed")
        return Response(status_code=204)

    @router.post("/kiosks/{uuid}/stop", status_code=204)
    async def stop(
        uuid: str,
        _=Depends(require_scope(Scope.CONTROL)),
    ) -> Response:
        kiosk = _get_kiosk_or_404(uuid)
        try:
            await kiosk.stop()
        except RuntimeError:
            raise HTTPException(status_code=500, detail="Kiosk operation failed")
        return Response(status_code=204)

    @router.post("/kiosks/{uuid}/restart", status_code=204)
    async def restart(
        uuid: str,
        _=Depends(require_scope(Scope.CONTROL)),
    ) -> Response:
        kiosk = _get_kiosk_or_404(uuid)
        try:
            await kiosk.restart()
        except RuntimeError:
            raise HTTPException(status_code=500, detail="Kiosk operation failed")
        return Response(status_code=204)

    @router.post("/kiosks/{uuid}/go-back", status_code=204)
    async def go_back(
        uuid: str,
        _=Depends(require_scope(Scope.CONTROL)),
    ) -> Response:
        kiosk = _get_kiosk_or_404(uuid)
        success = await kiosk.go_back()
        if not success:
            raise HTTPException(status_code=500, detail="Kiosk operation failed")
        return Response(status_code=204)

    @router.post("/kiosks/{uuid}/go-forward", status_code=204)
    async def go_forward(
        uuid: str,
        _=Depends(require_scope(Scope.CONTROL)),
    ) -> Response:
        kiosk = _get_kiosk_or_404(uuid)
        success = await kiosk.go_forward()
        if not success:
            raise HTTPException(status_code=500, detail="Kiosk operation failed")
        return Response(status_code=204)

    @router.post("/kiosks/{uuid}/go-home", status_code=204)
    async def go_home(
        uuid: str,
        _=Depends(require_scope(Scope.CONTROL)),
    ) -> Response:
        kiosk = _get_kiosk_or_404(uuid)
        success = await kiosk.go_home()
        if not success:
            raise HTTPException(status_code=500, detail="Kiosk operation failed")
        return Response(status_code=204)

    @router.post("/kiosks/{uuid}/click", status_code=204)
    async def click(
        uuid: str,
        body: ClickRequest,
        _=Depends(require_scope(Scope.CONTROL)),
    ) -> Response:
        kiosk = _get_kiosk_or_404(uuid)
        success = await kiosk.click(body.x, body.y)
        if not success:
            raise HTTPException(status_code=500, detail="Kiosk operation failed")
        return Response(status_code=204)

    @router.post("/kiosks/{uuid}/type-text", status_code=204)
    async def type_text(
        uuid: str,
        body: TypeTextRequest,
        _=Depends(require_scope(Scope.CONTROL)),
    ) -> Response:
        kiosk = _get_kiosk_or_404(uuid)
        success = await kiosk.type_text(body.text)
        if not success:
            raise HTTPException(status_code=500, detail="Kiosk operation failed")
        return Response(status_code=204)

    @router.post("/kiosks/{uuid}/scroll", status_code=204)
    async def scroll(
        uuid: str,
        body: ScrollRequest,
        _=Depends(require_scope(Scope.CONTROL)),
    ) -> Response:
        kiosk = _get_kiosk_or_404(uuid)
        success = await kiosk.scroll(body.direction, body.amount)
        if not success:
            raise HTTPException(status_code=500, detail="Kiosk operation failed")
        return Response(status_code=204)

    @router.post("/kiosks/{uuid}/press-key", status_code=204)
    async def press_key(
        uuid: str,
        body: PressKeyRequest,
        _=Depends(require_scope(Scope.CONTROL)),
    ) -> Response:
        kiosk = _get_kiosk_or_404(uuid)
        success = await kiosk.press_key(body.key)
        if not success:
            raise HTTPException(status_code=500, detail="Kiosk operation failed")
        return Response(status_code=204)

    @router.post("/kiosks/{uuid}/screenshot", response_class=StreamingResponse)
    async def screenshot(
        uuid: str,
        _=Depends(require_scope(Scope.CONTROL)),
    ) -> StreamingResponse:
        kiosk = _get_kiosk_or_404(uuid)
        try:
            data = await kiosk.screenshot()
        except RuntimeError:
            raise HTTPException(status_code=500, detail="Kiosk operation failed")
        return StreamingResponse(
            io.BytesIO(data),
            media_type="image/png",
            headers={"Content-Disposition": 'attachment; filename="screenshot.png"'},
        )

    return router
