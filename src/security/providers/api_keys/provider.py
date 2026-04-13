from __future__ import annotations

from datetime import datetime, timezone

from fastapi import Request
from fastapi.security import APIKeyHeader

from ...base.principal import Principal
from ...base.provider import SecurityProvider
from src.utils import get_logger
from src.utils.exceptions.errors import ErrorCode, raise_http
from .repository import ApiKeyRepository
from .utils import hash_key


logger = get_logger(__name__)


class ApiKeyProvider(SecurityProvider):
    """API key authentication provider."""

    # -------------------------------------------------------------------------
    # Construction
    # -------------------------------------------------------------------------

    def __init__(self, repo: ApiKeyRepository, secret: str):
        """Initialize the provider."""
        self.repo = repo
        self._secret = secret
        self._scheme = APIKeyHeader(name="X-API-Key", auto_error=False)

    # -------------------------------------------------------------------------
    # SecurityProvider Interface
    # -------------------------------------------------------------------------

    @property
    def openapi_scheme(self) -> APIKeyHeader:
        """Return the OpenAPI security scheme."""
        return self._scheme

    async def verify(self, credentials: str | None, request: Request) -> Principal:
        """Verify API key credentials and return a principal."""
        if credentials is None:
            logger.warning(
                "auth_failed",
                auth_method="api_key",
                reason="missing_credentials",
            )
            raise_http(401, ErrorCode.unauthorised, "Missing API key")

        key_hash = hash_key(credentials, self._secret)
        record = self.repo.get_by_hash(key_hash)
        if record is None:
            logger.warning(
                "auth_failed",
                auth_method="api_key",
                reason="invalid_key",
            )
            raise_http(401, ErrorCode.unauthorised, "Invalid API key")

        if record.revoked:
            logger.warning(
                "auth_failed",
                auth_method="api_key",
                reason="revoked",
                key_name=record.id,
            )
            raise_http(401, ErrorCode.unauthorised, "API key has been revoked")

        if record.expires_at is not None:
            now = datetime.now(timezone.utc)
            if now >= record.expires_at:
                logger.warning(
                    "auth_failed",
                    auth_method="api_key",
                    reason="expired",
                    key_name=record.id,
                )
                raise_http(401, ErrorCode.unauthorised, "API key has expired")

        return Principal(
            id=f"apikey:{record.id}",
            auth_method="api_key",
            scopes=record.scopes,
            metadata={"key_name": record.id},
        )