from __future__ import annotations

import threading
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.kiosk.kiosk.base import Kiosk

class KioskRegistry:
    """Thread-safe registry of active kiosk instances keyed by UUID."""

    def __init__(self) -> None:
        self._kiosks: dict[str, "Kiosk"] = {}
        self._lock = threading.Lock()

    def register(self, uuid: str, kiosk: "Kiosk") -> None:
        """Register a kiosk. Raises ValueError if UUID already registered."""
        with self._lock:
            if uuid in self._kiosks:
                raise ValueError(f"UUID already registered: {uuid}")
            self._kiosks[uuid] = kiosk

    def get(self, uuid: str) -> "Kiosk | None":
        """Return kiosk by UUID, or None if not found."""
        with self._lock:
            return self._kiosks.get(uuid)

    def deregister(self, uuid: str) -> bool:
        """Remove kiosk by UUID. Returns True if removed, False if not found."""
        with self._lock:
            if uuid not in self._kiosks:
                return False
            del self._kiosks[uuid]
            return True

    def list_all(self) -> dict[str, "Kiosk"]:
        """Return a shallow copy of all registered kiosks."""
        with self._lock:
            return dict(self._kiosks)