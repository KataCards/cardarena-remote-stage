from __future__ import annotations

from copy import deepcopy
from typing import Any

from src.utils import ErrorCode, ErrorResponse


_ERROR_RESPONSES: dict[int, dict[str, Any]] = {
    401: {
        "model": ErrorResponse,
        "description": "Authentication failed or credentials were not provided.",
        "content": {
            "application/json": {
                "example": {
                    "code": ErrorCode.unauthorised.value,
                    "message": "Missing API key",
                    "context": {},
                }
            }
        },
    },
    403: {
        "model": ErrorResponse,
        "description": "Authenticated, but the caller does not have enough permissions.",
        "content": {
            "application/json": {
                "example": {
                    "code": ErrorCode.forbidden.value,
                    "message": "Insufficient permissions",
                    "context": {},
                }
            }
        },
    },
    404: {
        "model": ErrorResponse,
        "description": "Requested resource was not found.",
        "content": {
            "application/json": {
                "example": {
                    "code": ErrorCode.not_found.value,
                    "message": "Kiosk not found: abc",
                    "context": {"kiosk_uuid": "abc"},
                }
            }
        },
    },
    409: {
        "model": ErrorResponse,
        "description": "Request conflicts with current resource state.",
        "content": {
            "application/json": {
                "example": {
                    "code": ErrorCode.conflict.value,
                    "message": "API key 'my-key' already exists",
                    "context": {},
                }
            }
        },
    },
    422: {
        "model": ErrorResponse,
        "description": "Request validation failed for one or more fields.",
        "content": {
            "application/json": {
                "example": {
                    "code": ErrorCode.validation_error.value,
                    "message": "field 'body.url': Field required",
                    "context": {"fields": ["('body', 'url')"]},
                }
            }
        },
    },
    500: {
        "model": ErrorResponse,
        "description": "Operation failed or an unexpected internal server error occurred.",
        "content": {
            "application/json": {
                "examples": {
                    "operation_failed": {
                        "summary": "Known operation failure",
                        "value": {
                            "code": ErrorCode.operation_failed.value,
                            "message": "Kiosk operation failed",
                            "context": {"kiosk_uuid": "abc"},
                        },
                    },
                    "internal_error": {
                        "summary": "Unhandled server error",
                        "value": {
                            "code": ErrorCode.internal_error.value,
                            "message": "Internal server error",
                            "context": {},
                        },
                    },
                }
            }
        },
    },
}


def error_responses(*status_codes: int) -> dict[int, dict[str, Any]]:
    """Return shared OpenAPI error response metadata for selected status codes."""
    unknown_codes = [code for code in status_codes if code not in _ERROR_RESPONSES]
    if unknown_codes:
        raise ValueError(f"Unsupported error status codes: {unknown_codes}")
    return {code: deepcopy(_ERROR_RESPONSES[code]) for code in status_codes}
