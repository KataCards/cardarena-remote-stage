from __future__ import annotations


def parse_comma_separated_list(value: object) -> list[str]:
    """Parse comma-separated text into a list of trimmed non-empty items."""
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    return list(value)  # type: ignore[arg-type]
