from __future__ import annotations

from enum import StrEnum
from typing import Never

from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict, Field


class ErrorCode(StrEnum):
    """Known API error code values."""

    not_found = "not_found"
    unauthorised = "unauthorised"
    forbidden = "forbidden"
    conflict = "conflict"
    validation_error = "validation_error"
    operation_failed = "operation_failed"
    internal_error = "internal_error"


class ErrorResponse(BaseModel):
    """Standard error response payload."""

    model_config = ConfigDict(frozen=True)

    code: ErrorCode
    message: str
    context: dict = Field(default_factory=dict)


_STATUS_TO_CODE: dict[int, ErrorCode] = {
    401: ErrorCode.unauthorised,
    403: ErrorCode.forbidden,
    404: ErrorCode.not_found,
    409: ErrorCode.conflict,
    500: ErrorCode.internal_error,
}


def raise_http(
    status: int,
    code: ErrorCode,
    message: str,
    context: dict | None = None,
) -> Never:
    """Raise an HTTPException using the standard error response payload."""
    response = ErrorResponse(code=code, message=message, context=context or {})
    raise HTTPException(status_code=status, detail=response.model_dump())
