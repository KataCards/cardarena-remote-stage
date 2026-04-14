from __future__ import annotations

from time import perf_counter
from uuid import uuid4

from starlette.types import ASGIApp, Receive, Scope, Send
from structlog.contextvars import bind_contextvars, unbind_contextvars

from src.utils import get_logger


logger = get_logger(__name__)


class RequestContextMiddleware:
    """Bind request context, capture status code, and log request lifecycle."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id = str(uuid4())
        bind_contextvars(request_id=request_id)

        started = perf_counter()
        status_code = 500
        method = scope.get("method", "")
        path = scope.get("path", "")

        async def send_with_status(message: dict) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, send_with_status)
        finally:
            duration_ms = round((perf_counter() - started) * 1000, 2)
            logger.info(
                "request",
                method=method,
                path=path,
                status_code=status_code,
                duration_ms=duration_ms,
            )
            unbind_contextvars("request_id")