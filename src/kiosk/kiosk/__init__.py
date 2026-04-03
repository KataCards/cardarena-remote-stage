"""Kiosk module - browser orchestration abstractions."""

from .base import Kiosk
from .playwright import PlaywrightKiosk

__all__ = ["Kiosk", "PlaywrightKiosk"]