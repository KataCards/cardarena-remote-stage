"""
Kiosk - Production-ready browser automation framework.

This package provides abstract base classes for building browser-based kiosk
applications with Playwright, featuring URL whitelisting, lifecycle management,
and comprehensive error handling.

Public API:
    - Engine: Abstract browser engine base class
    - Controls: Abstract browser controls base class
    - Kiosk: Abstract kiosk orchestration base class
    - PlaywrightEngine: Playwright-based browser engine implementation
    - PlaywrightControls: Playwright-based browser controls implementation
    - PlaywrightKiosk: Playwright-based kiosk orchestration implementation
"""

from .controls import Controls
from .engine import Engine, PlaywrightEngine
from .kiosk import Kiosk, PlaywrightKiosk

__all__ = ["Engine", "Controls", "Kiosk", "PlaywrightEngine", "PlaywrightKiosk"]