from __future__ import annotations

import re

_URL_PATTERN = re.compile(
    r"^("
    r"https?://([a-zA-Z0-9.-]+|\[[0-9a-fA-F:]+\])(:[0-9]+)?(/[^\s]*)?"
    r"|file:///[^\s]*"
    r")$",
    re.IGNORECASE,
)


def validate_url(value: str) -> str:
    """Validate supported URL schemes for kiosk navigation fields."""
    if not _URL_PATTERN.match(value):
        raise ValueError(
            f"URL must start with 'https://', 'http://', or 'file:///'. Got: {value}"
        )
    return value
