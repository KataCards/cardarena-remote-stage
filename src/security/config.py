from __future__ import annotations

from functools import lru_cache
from typing import Annotated

from pydantic import ConfigDict, Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, NoDecode

from src.utils import parse_comma_separated_list

from .base.provider import SecurityProvider


class SecuritySettings(BaseSettings):
    """Environment-driven security configuration."""

    model_config = ConfigDict(env_file=".env", extra="ignore")

    security_provider: str = "api_key"
    apikey_db_path: str = "./security.db"
    apikey_db_type: str = "sqlite"
    apikey_secret: SecretStr = SecretStr("")  # Optional: only required for api_key provider
    allowed_ips: Annotated[list[str], NoDecode] = Field(default_factory=list)

    @field_validator("allowed_ips", mode="before")
    @classmethod
    def _parse_comma_separated_ips(cls, v: object) -> list[str]:
        """Parse comma-separated string into list of IP addresses."""
        return parse_comma_separated_list(v)


@lru_cache
def get_settings() -> SecuritySettings:
    """Return the cached security settings instance."""
    return SecuritySettings()


def get_active_provider() -> SecurityProvider:
    """Return the configured security provider."""
    settings = get_settings()

    if settings.security_provider == "api_key":
        from .providers.api_keys.db import ApiKeyDatabase
        from .providers.api_keys.provider import ApiKeyProvider
        from .providers.api_keys.repository import ApiKeyRepository

        db = ApiKeyDatabase(settings.apikey_db_path)
        db.initialise()
        secret = settings.apikey_secret.get_secret_value()
        repo = ApiKeyRepository(db, secret)
        return ApiKeyProvider(repo, secret)

    elif settings.security_provider == "ip_whitelist":
        from .providers.ip_whitelist.provider import IpWhitelistProvider

        return IpWhitelistProvider(allowed_ips=settings.allowed_ips)

    raise ValueError(
        f"Unknown security provider: '{settings.security_provider}'. "
        f"Supported: 'api_key', 'ip_whitelist'"
    )