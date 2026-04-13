from __future__ import annotations

from fastapi import HTTPException, Request
from fastapi.security.base import SecurityBase

from ...base.principal import Principal, Scope
from ...base.provider import SecurityProvider
from src.utils import get_logger
from .scheme import NoCredentialsScheme


logger = get_logger(__name__)


class IpWhitelistProvider(SecurityProvider):
    """IP whitelist authentication provider."""

    # -------------------------------------------------------------------------
    # Construction
    # -------------------------------------------------------------------------

    def __init__(self, allowed_ips: list[str]) -> None:
        """Initialize the provider with an IP whitelist."""
        self.allowed_ips = allowed_ips
        self._scheme = NoCredentialsScheme()

    # -------------------------------------------------------------------------
    # SecurityProvider Interface
    # -------------------------------------------------------------------------

    @property
    def openapi_scheme(self) -> SecurityBase:
        """Return the OpenAPI security scheme."""
        return self._scheme

    async def verify(self, credentials: object | None, request: Request) -> Principal:
        """Verify client IP against the configured whitelist."""
        if request.client is None:
            logger.warning(
                "auth_failed",
                auth_method="ip",
                reason="no_client",
            )
            raise HTTPException(
                status_code=401,
                detail="Unable to determine client IP address"
            )

        host = request.client.host

        if host not in self.allowed_ips:
            logger.warning(
                "auth_failed",
                auth_method="ip",
                reason="ip_not_whitelisted",
                ip=host,
            )
            raise HTTPException(
                status_code=403,
                detail="IP address not authorized"
            )

        return Principal(
            id=f"ip:{host}",
            auth_method="ip",
            scopes=[Scope.READ, Scope.CONTROL, Scope.ADMIN],
            metadata={"ip": host}
        )
