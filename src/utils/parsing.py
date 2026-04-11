from __future__ import annotations


def parse_comma_separated_list(v: object) -> list[str]:
    if isinstance(v, str):
        return [item.strip() for item in v.split(",") if item.strip()]
    return list(v)  # type: ignore[arg-type]