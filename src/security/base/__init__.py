"""Security base module - core primitives for authentication and authorization."""

from .principal import Principal, Scope
from .provider import SecurityProvider

__all__ = ["Principal", "Scope", "SecurityProvider"]