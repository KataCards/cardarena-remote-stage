from __future__ import annotations

from functools import lru_cache

from pydantic import ConfigDict, Field, field_validator
from pydantic_settings import BaseSettings

from src.utils import validate_url


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file."""
    
    model_config = ConfigDict(env_file=".env", extra="ignore")

    kiosk_allowed_urls: list[str] = Field(default_factory=list)
    kiosk_error_page: str | None = None
    kiosk_default_url: str = "https://example.com"
    kiosk_name: str = "default"
    kiosk_headless: bool = False

    @field_validator("kiosk_allowed_urls", mode="before")
    @classmethod
    def _parse_comma_separated(cls, v: object) -> list[str]:
        """Parse comma-separated string into list of URLs."""
        if isinstance(v, str):
            return [u.strip() for u in v.split(",") if u.strip()]
        return list(v)  # type: ignore[arg-type]

    @field_validator("kiosk_default_url")
    @classmethod
    def _validate_url_protocol(cls, v: str) -> str:
        return validate_url(v)


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings instance."""
    return Settings()
