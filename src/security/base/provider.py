from __future__ import annotations

from abc import ABC, abstractmethod

from fastapi.security.base import SecurityBase
from fastapi import Request

from .principal import Principal


class SecurityProvider(ABC):
    """Abstract base class for security providers."""

    @property
    @abstractmethod
    def openapi_scheme(self) -> SecurityBase:
        """Return the OpenAPI security scheme for this provider."""
        ...

    @abstractmethod
    async def verify(self, credentials: object | None, request: Request) -> Principal:
        """Verify credentials and return a principal."""
        ...
