"""Security package for the kiosk system.

This package provides authentication and authorization primitives for
securing the remote-controllable kiosk system.
"""

from .base import Principal, Scope, SecurityProvider

__all__ = ["Principal", "Scope", "SecurityProvider"]