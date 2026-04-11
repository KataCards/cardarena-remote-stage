from __future__ import annotations

from fastapi import Request
from fastapi.openapi.models import APIKey, APIKeyIn
from fastapi.security.base import SecurityBase


class NoCredentialsScheme(SecurityBase):
    """Security scheme that requires no credentials."""

    def __init__(self) -> None:
        """Initialize a synthetic API-key model for OpenAPI compatibility."""
        self.model = APIKey(
            type="apiKey",
            **{"in": APIKeyIn.header},
            name="X-Forwarded-For",
            description="Used only for documentation. IP whitelist auth checks the client IP.",
        )
        self.scheme_name = "IpWhitelist"

    async def __call__(self, request: Request) -> None:
        """Return no explicit credentials for IP-based authentication."""
        return None
