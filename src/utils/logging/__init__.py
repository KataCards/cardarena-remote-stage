"""Logging utilities module.

This module provides logging-related utilities including RFC 5424 compliant
log level definitions and logging configuration.
"""

from .log_levels import LogLevel, RFC5424Level

__all__ = ["LogLevel", "RFC5424Level"]