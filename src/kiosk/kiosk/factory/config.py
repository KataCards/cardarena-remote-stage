from __future__ import annotations

import shlex
from functools import lru_cache
from typing import Annotated, Literal

from pydantic import ConfigDict, Field, field_validator
from pydantic_settings import BaseSettings, NoDecode


class PlaywrightFactorySettings(BaseSettings):
    """Playwright-factory specific settings loaded from environment or .env."""

    model_config = ConfigDict(env_file=".env", extra="ignore")

    kiosk_playwright_browser_type: Literal["chromium", "firefox", "webkit"] = "chromium"
    kiosk_playwright_launch_args: Annotated[list[str], NoDecode] = Field(default_factory=list)

    @field_validator("kiosk_playwright_launch_args", mode="before")
    @classmethod
    def _parse_launch_args(cls, v: object) -> list[str]:
        if isinstance(v, str):
            return shlex.split(v)
        return list(v)  # type: ignore[arg-type]


@lru_cache
def get_playwright_factory_settings() -> PlaywrightFactorySettings:
    """Get cached Playwright-factory settings instance."""
    return PlaywrightFactorySettings()
