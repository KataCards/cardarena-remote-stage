from abc import ABC, abstractmethod

from fastapi.security.base import SecurityBase
from fastapi import Request

from .principal import Principal


class SecurityProvider(ABC):
    """Abstract base class for security providers.

    A SecurityProvider is responsible for:
    1. Defining the OpenAPI security scheme (e.g., API key, Bearer token)
    2. Verifying credentials and returning a Principal

    Concrete implementations must provide both methods.

    Note on auto_error:
        Implementations should set auto_error=False on their security schemes
        to prevent FastAPI from automatically raising 401 errors. This allows
        the provider's verify() method to handle authentication failures with
        custom error messages and proper distinction between 401 (invalid
        credentials) and 403 (insufficient scope).
    """

    @property
    @abstractmethod
    def openapi_scheme(self) -> SecurityBase:
        """Return the OpenAPI security scheme for this provider.

        This method defines how the security scheme appears in OpenAPI docs
        and what type of credentials the provider expects.

        Returns:
            A FastAPI SecurityBase instance (e.g., APIKeyHeader, HTTPBearer)

        Example:
            return APIKeyHeader(name="X-API-Key", auto_error=False)
        """
        ...

    @abstractmethod
    async def verify(self, credentials, request: Request) -> Principal:
        """Verify credentials and return a Principal.

        This method receives credentials extracted by the OpenAPI scheme
        and validates them. The type of 'credentials' depends on the scheme:
        - APIKeyHeader/APIKeyQuery: str
        - HTTPBearer: HTTPAuthorizationCredentials
        - HTTPBasic: HTTPBasicCredentials

        Args:
            credentials: The credentials extracted by the security scheme.
                Type varies by provider implementation.
            request: The FastAPI Request object for additional context

        Returns:
            A verified Principal with id, auth_method, scopes, and metadata

        Raises:
            HTTPException: 401 for invalid/missing credentials
            HTTPException: 403 for valid credentials with insufficient scope

        Example:
            if not self.is_valid(credentials):
                raise HTTPException(status_code=401, detail="Invalid API key")
            return Principal(
                id=f"apikey:{key_id}",
                auth_method="api_key",
                scopes=[Scope.READ],
                metadata={"key": credentials}
            )
        """
        ...