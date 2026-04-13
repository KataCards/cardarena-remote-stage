from __future__ import annotations

import threading
from typing import TYPE_CHECKING

from src.config import get_settings

from .history import ActivityLog

if TYPE_CHECKING:
    from src.kiosk.kiosk.base import Kiosk


class KioskRegistry:
    """Thread-safe registry of active kiosk instances keyed by UUID."""

    def __init__(self) -> None:
        self._kiosks: dict[str, Kiosk] = {}
        self._logs: dict[str, ActivityLog] = {}
        self._lock = threading.Lock()

    def register(self, uuid: str, kiosk: Kiosk) -> None:
        """Register a kiosk and create its activity log. Raises ValueError if UUID already registered."""
        with self._lock:
            if uuid in self._kiosks:
                raise ValueError(f"UUID already registered: {uuid}")
            self._kiosks[uuid] = kiosk
            self._logs[uuid] = ActivityLog(maxsize=get_settings().kiosk_history_size)

    def get(self, uuid: str) -> Kiosk | None:
        """Return kiosk by UUID, or None if not found."""
        with self._lock:
            return self._kiosks.get(uuid)

    def get_log(self, uuid: str) -> ActivityLog | None:
        """Return activity log for UUID, or None if not found."""
        with self._lock:
            return self._logs.get(uuid)

    def deregister(self, uuid: str) -> bool:
        """Remove kiosk and its activity log by UUID. Returns True if removed, False if not found."""
        with self._lock:
            if uuid not in self._kiosks:
                return False
            del self._kiosks[uuid]
            del self._logs[uuid]
            return True

    def list_all(self) -> dict[str, Kiosk]:
        """Return a shallow copy of all registered kiosks."""
        with self._lock:
            return dict(self._kiosks)
