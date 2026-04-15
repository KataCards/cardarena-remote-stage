from __future__ import annotations

import logging
import sys
from typing import cast

import structlog
from fastapi.exceptions import RequestValidationError
from structlog.contextvars import merge_contextvars
from structlog.dev import ConsoleRenderer
from structlog.processors import (
    ExceptionRenderer,
    JSONRenderer,
    StackInfoRenderer,
    TimeStamper,
)
from structlog.stdlib import BoundLogger, add_log_level, add_logger_name


def configure_logging(log_level: str, log_format: str) -> None:
    """Configure structlog and stdlib logging with a shared processor chain."""
    level_name = log_level if isinstance(log_level, str) else "INFO"
    configured_level = getattr(logging, level_name.upper(), logging.INFO)
    if not isinstance(configured_level, int):
        configured_level = logging.INFO

    format_name = log_format if isinstance(log_format, str) else "json"
    renderer = JSONRenderer() if format_name.lower() == "json" else ConsoleRenderer()
    shared_processors = [
        merge_contextvars,
        add_log_level,
        add_logger_name,
        TimeStamper(fmt="iso"),
        StackInfoRenderer(),
        ExceptionRenderer(),
    ]

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        wrapper_class=BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(configured_level)

    for logger_name in (
        "uvicorn",
        "uvicorn.error",
        "uvicorn.access",
        "sqlalchemy",
        "sqlalchemy.engine",
    ):
        external_logger = logging.getLogger(logger_name)
        external_logger.handlers.clear()
        external_logger.propagate = True


def get_logger(name: str) -> BoundLogger:
    """Return a structlog logger for a module name."""
    return cast(BoundLogger, structlog.get_logger(name))


def _decode_pydantic_error(exc: RequestValidationError) -> str:
    """Flatten a RequestValidationError into compact field-level messages."""
    decoded_errors: list[str] = []
    for error in exc.errors():
        location = ".".join(str(part) for part in error.get("loc", ()))
        field = location or "unknown"
        message = str(error.get("msg", "invalid value"))
        decoded_errors.append(f"field '{field}': {message}")
    return "; ".join(decoded_errors)