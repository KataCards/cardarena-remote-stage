from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Annotated

from pydantic import ConfigDict, Field, field_validator
from pydantic_settings import BaseSettings, NoDecode

from src.utils import parse_comma_separated_list, validate_url


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file."""

    model_config = ConfigDict(env_file=".env", extra="ignore")

    host: str = "0.0.0.0"
    port: int = 8000
    kiosk_allowed_urls: Annotated[list[str], NoDecode] = Field(default_factory=list)
    kiosk_error_pages_dir: str | None = None
    kiosk_default_url: str = "https://example.com"
    kiosk_name: str = "default"
    kiosk_headless: bool = False
    kiosk_fullscreen: bool = False
    kiosk_error_routing: bool = True

    @field_validator("kiosk_allowed_urls", mode="before")
    @classmethod
    def _parse_comma_separated(cls, v: object) -> list[str]:
        """Parse comma-separated string into list of URLs."""
        return parse_comma_separated_list(v)

    @field_validator("kiosk_default_url")
    @classmethod
    def _validate_url_protocol(cls, v: str) -> str:
        if not v.startswith(("http://", "https://", "file://")):
            resolved = Path(v).resolve()
            if not resolved.exists():
                raise ValueError(f"Relative path does not exist: {v}")
            v = resolved.as_uri()
        return validate_url(v)


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings instance."""
    return Settings()
