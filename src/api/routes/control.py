from __future__ import annotations

import io
from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends
from fastapi.responses import Response, StreamingResponse

from ..models import (
    ClickRequest,
    NavigateRequest,
    PressKeyRequest,
    ScrollRequest,
    TypeTextRequest,
)
from .openapi import error_responses
from .utils import get_kiosk_or_404
from ...security import Scope, require_scope
from src.utils import ErrorCode, raise_http

if TYPE_CHECKING:
    from ..registry import KioskRegistry


def build_router(registry: "KioskRegistry") -> APIRouter:
    """Build kiosk control routes."""
    router = APIRouter(responses=error_responses(401, 403, 404, 422, 500))

    def _assert_success(success: bool, uuid: str) -> None:
        if not success:
            raise_http(
                500,
                ErrorCode.operation_failed,
                "Kiosk operation failed",
                context={"kiosk_uuid": uuid},
            )

    @router.post("/kiosks/{uuid}/navigate", status_code=204, summary="Navigate to URL")
    async def navigate(
        uuid: str,
        body: NavigateRequest,
        _=Depends(require_scope(Scope.CONTROL)),
    ) -> Response:
        kiosk = get_kiosk_or_404(registry, uuid)
        success = await kiosk.navigate(body.url)
        if log := registry.get_log(uuid):
            log.record("navigate", success=success, url=body.url)
        _assert_success(success, uuid)
        return Response(status_code=204)

    @router.post("/kiosks/{uuid}/reload", status_code=204, summary="Reload current page")
    async def reload(
        uuid: str,
        _=Depends(require_scope(Scope.CONTROL)),
    ) -> Response:
        kiosk = get_kiosk_or_404(registry, uuid)
        success = await kiosk.reload()
        if log := registry.get_log(uuid):
            log.record("reload", success=success)
        _assert_success(success, uuid)
        return Response(status_code=204)

    @router.post("/kiosks/{uuid}/start", status_code=204, summary="Start kiosk")
    async def start(
        uuid: str,
        _=Depends(require_scope(Scope.CONTROL)),
    ) -> Response:
        kiosk = get_kiosk_or_404(registry, uuid)
        log = registry.get_log(uuid)
        try:
            await kiosk.start()
        except RuntimeError:
            if log:
                log.record("start", success=False)
            raise_http(
                500,
                ErrorCode.operation_failed,
                "Kiosk operation failed",
                context={"kiosk_uuid": uuid},
            )
        if log:
            log.record("start")
        return Response(status_code=204)

    @router.post("/kiosks/{uuid}/stop", status_code=204, summary="Stop kiosk")
    async def stop(
        uuid: str,
        _=Depends(require_scope(Scope.CONTROL)),
    ) -> Response:
        kiosk = get_kiosk_or_404(registry, uuid)
        log = registry.get_log(uuid)
        try:
            await kiosk.stop()
        except RuntimeError:
            if log:
                log.record("stop", success=False)
            raise_http(
                500,
                ErrorCode.operation_failed,
                "Kiosk operation failed",
                context={"kiosk_uuid": uuid},
            )
        if log:
            log.record("stop")
        return Response(status_code=204)

    @router.post("/kiosks/{uuid}/restart", status_code=204, summary="Restart kiosk")
    async def restart(
        uuid: str,
        _=Depends(require_scope(Scope.CONTROL)),
    ) -> Response:
        kiosk = get_kiosk_or_404(registry, uuid)
        log = registry.get_log(uuid)
        try:
            await kiosk.restart()
        except RuntimeError:
            if log:
                log.record("restart", success=False)
            raise_http(
                500,
                ErrorCode.operation_failed,
                "Kiosk operation failed",
                context={"kiosk_uuid": uuid},
            )
        if log:
            log.record("restart")
        return Response(status_code=204)

    @router.post("/kiosks/{uuid}/go-back", status_code=204, summary="Navigate back")
    async def go_back(
        uuid: str,
        _=Depends(require_scope(Scope.CONTROL)),
    ) -> Response:
        kiosk = get_kiosk_or_404(registry, uuid)
        success = await kiosk.go_back()
        if log := registry.get_log(uuid):
            log.record("go_back", success=success)
        _assert_success(success, uuid)
        return Response(status_code=204)

    @router.post("/kiosks/{uuid}/go-forward", status_code=204, summary="Navigate forward")
    async def go_forward(
        uuid: str,
        _=Depends(require_scope(Scope.CONTROL)),
    ) -> Response:
        kiosk = get_kiosk_or_404(registry, uuid)
        success = await kiosk.go_forward()
        if log := registry.get_log(uuid):
            log.record("go_forward", success=success)
        _assert_success(success, uuid)
        return Response(status_code=204)

    @router.post("/kiosks/{uuid}/go-home", status_code=204, summary="Navigate to default page")
    async def go_home(
        uuid: str,
        _=Depends(require_scope(Scope.CONTROL)),
    ) -> Response:
        kiosk = get_kiosk_or_404(registry, uuid)
        log = registry.get_log(uuid)
        try:
            success = await kiosk.go_home()
        except RuntimeError:
            if log:
                log.record("go_home", success=False)
            raise_http(
                500,
                ErrorCode.operation_failed,
                "Kiosk operation failed",
                context={"kiosk_uuid": uuid},
            )
        if log:
            log.record("go_home", success=success)
        _assert_success(success, uuid)
        return Response(status_code=204)

    @router.post("/kiosks/{uuid}/click", status_code=204, summary="Click at coordinates")
    async def click(
        uuid: str,
        body: ClickRequest,
        _=Depends(require_scope(Scope.CONTROL)),
    ) -> Response:
        kiosk = get_kiosk_or_404(registry, uuid)
        success = await kiosk.click(body.x, body.y)
        if log := registry.get_log(uuid):
            log.record("click", success=success, x=body.x, y=body.y)
        _assert_success(success, uuid)
        return Response(status_code=204)

    @router.post("/kiosks/{uuid}/type-text", status_code=204, summary="Type text")
    async def type_text(
        uuid: str,
        body: TypeTextRequest,
        _=Depends(require_scope(Scope.CONTROL)),
    ) -> Response:
        kiosk = get_kiosk_or_404(registry, uuid)
        success = await kiosk.type_text(body.text)
        if log := registry.get_log(uuid):
            log.record("type_text", success=success)
        _assert_success(success, uuid)
        return Response(status_code=204)

    @router.post("/kiosks/{uuid}/scroll", status_code=204, summary="Scroll page")
    async def scroll(
        uuid: str,
        body: ScrollRequest,
        _=Depends(require_scope(Scope.CONTROL)),
    ) -> Response:
        kiosk = get_kiosk_or_404(registry, uuid)
        success = await kiosk.scroll(body.direction, body.amount)
        if log := registry.get_log(uuid):
            log.record("scroll", success=success, direction=body.direction, amount=body.amount)
        _assert_success(success, uuid)
        return Response(status_code=204)

    @router.post("/kiosks/{uuid}/press-key", status_code=204, summary="Press keyboard key")
    async def press_key(
        uuid: str,
        body: PressKeyRequest,
        _=Depends(require_scope(Scope.CONTROL)),
    ) -> Response:
        kiosk = get_kiosk_or_404(registry, uuid)
        success = await kiosk.press_key(body.key)
        if log := registry.get_log(uuid):
            log.record("press_key", success=success, key=body.key)
        _assert_success(success, uuid)
        return Response(status_code=204)

    @router.post(
        "/kiosks/{uuid}/screenshot",
        response_class=StreamingResponse,
        summary="Capture screenshot",
        responses={
            200: {
                "description": "PNG screenshot binary stream.",
                "content": {
                    "image/png": {
                        "schema": {"type": "string", "format": "binary"}
                    }
                },
            }
        },
    )
    async def screenshot(
        uuid: str,
        _=Depends(require_scope(Scope.CONTROL)),
    ) -> StreamingResponse:
        kiosk = get_kiosk_or_404(registry, uuid)
        try:
            data = await kiosk.screenshot()
        except RuntimeError:
            raise_http(
                500,
                ErrorCode.operation_failed,
                "Kiosk operation failed",
                context={"kiosk_uuid": uuid},
            )
        return StreamingResponse(
            io.BytesIO(data),
            media_type="image/png",
            headers={"Content-Disposition": 'attachment; filename="screenshot.png"'},
        )

    @router.get(
        "/kiosks/{uuid}/health",
        response_model=dict[str, bool | str],
        summary="Get kiosk health",
    )
    async def kiosk_health(
        uuid: str,
        _=Depends(require_scope(Scope.CONTROL)),
    ) -> dict[str, bool | str]:
        kiosk = get_kiosk_or_404(registry, uuid)
        healthy = await kiosk.is_healthy()
        return {"uuid": uuid, "healthy": healthy}

    return router
