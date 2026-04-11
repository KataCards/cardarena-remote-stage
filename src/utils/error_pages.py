from __future__ import annotations

from pathlib import Path


def build_error_map(folder: str) -> tuple[dict[str, str], dict[int, str]]:
    """Build PlaywrightEngine resources and error_map from a folder."""
    root = Path(folder)
    if not root.exists() or not root.is_dir():
        return {}, {}

    resources: dict[str, str] = {}
    error_map: dict[int, str] = {}

    for entry in sorted(root.iterdir(), key=lambda path: path.name):
        if not entry.is_dir():
            continue

        try:
            status_code = int(entry.name)
        except ValueError:
            continue

        if not (100 <= status_code <= 599):
            continue

        index_file = entry / "index.html"
        if not index_file.is_file():
            continue

        resource_key = entry.name
        resources[resource_key] = str(index_file)
        error_map[status_code] = resource_key

    return resources, error_map
