from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import HTTPException

from src.kiosk.kiosk.base import Kiosk

if TYPE_CHECKING:
    from ..registry import KioskRegistry


def get_kiosk_or_404(registry: "KioskRegistry", uuid: str) -> Kiosk:
    kiosk = registry.get(uuid)
    if kiosk is None:
        raise HTTPException(status_code=404, detail=f"Kiosk not found: {uuid}")
    return kiosk