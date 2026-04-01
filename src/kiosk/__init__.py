"""
Kiosk - Production-ready browser automation framework.

This package provides abstract base classes for building browser-based kiosk
applications with Playwright, featuring URL whitelisting, lifecycle management,
and comprehensive error handling.

Public API:
    - Engine: Abstract browser engine base class
    - Controls: Abstract browser controls base class
    - Kiosk: Abstract kiosk orchestration base class
"""

from .controls import Controls
from .engine import Engine
from .kiosk import Kiosk

__all__ = ["Engine", "Controls", "Kiosk"]