from __future__ import annotations

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from ..monitoring.logging import _decode_pydantic_error, get_logger
from .errors import ErrorCode, ErrorResponse, _STATUS_TO_CODE


logger = get_logger(__name__)


def _request_log_fields(request: Request) -> dict[str, str]:
    return {
        "path": request.url.path,
        "method": request.method,
    }


async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    """Render HTTP exceptions into the standard error response shape."""
    logger.warning(
        "http_exception",
        status_code=exc.status_code,
        **_request_log_fields(request),
    )

    if isinstance(exc.detail, dict):
        content = exc.detail
    else:
        code = _STATUS_TO_CODE.get(exc.status_code, ErrorCode.operation_failed)
        content = ErrorResponse(code=code, message=str(exc.detail)).model_dump()

    return JSONResponse(status_code=exc.status_code, content=content)


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Render request validation errors into the standard error response shape."""
    decoded = _decode_pydantic_error(exc)
    content = ErrorResponse(
        code=ErrorCode.validation_error,
        message=decoded,
        context={"fields": [str(error["loc"]) for error in exc.errors()]},
    ).model_dump()

    logger.warning(
        "request_validation_failed",
        message=decoded,
        **_request_log_fields(request),
    )

    return JSONResponse(status_code=422, content=content)


async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Render unexpected exceptions as generic internal error responses."""
    logger.error(
        "unhandled_exception",
        **_request_log_fields(request),
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            code=ErrorCode.internal_error,
            message="Internal server error",
        ).model_dump(),
    )
