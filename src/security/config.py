"""Security configuration loaded from environment variables."""

from functools import lru_cache

from pydantic import ConfigDict
from pydantic_settings import BaseSettings

from .base.provider import SecurityProvider


class SecuritySettings(BaseSettings):
    """Environment-driven security configuration."""

    model_config = ConfigDict(env_file=".env", extra="ignore")

    security_provider: str = "api_key"
    apikey_db_path: str = "./security.db"
    apikey_db_type: str = "sqlite"


@lru_cache
def get_settings() -> SecuritySettings:
    """Return the cached security settings instance."""
    return SecuritySettings()


def get_active_provider() -> SecurityProvider:
    """Instantiate and return the configured security provider.

    Reads SECURITY_PROVIDER from env to select the implementation.
    NOTE: Only "api_key" is supported today. Other provider names raise ValueError.

    Returns:
        A fully initialised SecurityProvider instance.

    Raises:
        ValueError: If SECURITY_PROVIDER names an unknown provider.
    """
    settings = get_settings()

    if settings.security_provider == "api_key":
        from .providers.api_keys.db import ApiKeyDatabase
        from .providers.api_keys.provider import ApiKeyProvider
        from .providers.api_keys.repository import ApiKeyRepository

        db = ApiKeyDatabase(settings.apikey_db_path)
        db.initialise()
        repo = ApiKeyRepository(db)
        return ApiKeyProvider(repo)

    raise ValueError(
        f"Unknown security provider: '{settings.security_provider}'. "
        f"Supported: 'api_key'"
    )