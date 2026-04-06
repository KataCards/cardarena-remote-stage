"""API configuration loaded from environment / .env file."""
from __future__ import annotations

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class ApiSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    kiosk_allowed_urls: list[str] = Field(default_factory=list)
    kiosk_error_page: str = ""
    kiosk_default_url: str = "https://example.com"  # must be https?:// or file:///
    kiosk_name: str = "default"

    @field_validator("kiosk_allowed_urls", mode="before")
    @classmethod
    def _parse_comma_separated(cls, v: object) -> list[str]:
        if isinstance(v, str):
            return [u.strip() for u in v.split(",") if u.strip()]
        return list(v)  # type: ignore[arg-type]


@lru_cache
def get_settings() -> ApiSettings:
    return ApiSettings()
