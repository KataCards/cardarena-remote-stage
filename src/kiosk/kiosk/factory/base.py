from __future__ import annotations

from abc import ABC, abstractmethod

from src.config import Settings
from src.kiosk.kiosk.base import Kiosk


class KioskFactory(ABC):
    """Abstract factory for constructing Kiosk instances from application settings."""

    @abstractmethod
    def build(self, settings: Settings) -> Kiosk:
        """Build and return a fully-configured Kiosk instance."""
        ...
