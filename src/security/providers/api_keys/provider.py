from datetime import datetime, timezone

from fastapi import HTTPException, Request
from fastapi.security import APIKeyHeader

from ...base.principal import Principal
from ...base.provider import SecurityProvider
from ...config import get_settings
from .repository import ApiKeyRepository
from .utils import hash_key


class ApiKeyProvider(SecurityProvider):
    """API Key authentication provider.

    Validates API keys via X-API-Key header, checking against hashed
    values in the database. Enforces revocation and expiration.

    Attributes:
        repo: ApiKeyRepository instance for database access
    """

    def __init__(self, repo: ApiKeyRepository):
        """Initialize the provider with a repository.

        Args:
            repo: ApiKeyRepository instance
        """
        self.repo = repo
        self.settings = get_settings()
        self._scheme = APIKeyHeader(name="X-API-Key", auto_error=False)

    @property
    def openapi_scheme(self) -> APIKeyHeader:
        """Return the OpenAPI security scheme.

        Returns:
            APIKeyHeader scheme for X-API-Key header
        """
        return self._scheme

    async def verify(self, credentials: str | None, request: Request) -> Principal:
        """Verify API key credentials and return a Principal.

        Args:
            credentials: Raw API key from X-API-Key header
            request: FastAPI request object (unused, required by interface)

        Returns:
            Principal with scopes from the API key record

        Raises:
            HTTPException: 401 if credentials are missing, invalid, revoked, or expired
        """
        if credentials is None:
            raise HTTPException(status_code=401, detail="Missing API key")

        # Hash the incoming key
        key_hash = hash_key(credentials)

        # Lookup by hash
        record = self.repo._get_by_hash(key_hash)
        if record is None:
            raise HTTPException(status_code=401, detail="Invalid API key")

        # Check revocation
        if record.revoked:
            raise HTTPException(status_code=401, detail="API key has been revoked")

        # Check expiration
        if record.expires_at is not None:
            now = datetime.now(timezone.utc)
            # SQLite doesn't store timezone info, so we need to make expires_at timezone-aware
            # This workaround is only needed for SQLite databases
            expires_at = record.expires_at
            if self.settings.apikey_db_type == "sqlite" and expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            if now >= expires_at:
                raise HTTPException(status_code=401, detail="API key has expired")

        # All checks passed — return Principal
        return Principal(
            id=f"apikey:{record.id}",
            auth_method="api_key",
            scopes=record.scopes,
            metadata={"key_name": record.id},
        )