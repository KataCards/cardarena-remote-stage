from __future__ import annotations

from typing import TYPE_CHECKING

from src.kiosk.kiosk.base import Kiosk
from src.utils import ErrorCode, raise_http

if TYPE_CHECKING:
    from ..registry import KioskRegistry


def get_kiosk_or_404(registry: "KioskRegistry", uuid: str) -> Kiosk:
    kiosk = registry.get(uuid)
    if kiosk is None:
        raise_http(
            404,
            ErrorCode.not_found,
            f"Kiosk not found: {uuid}",
            context={"kiosk_uuid": uuid},
        )
    return kiosk
