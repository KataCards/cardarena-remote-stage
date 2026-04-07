"""Kiosk API request/response models."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, field_validator

from src.utils import validate_url


class KioskStatus(BaseModel):
    """Full status snapshot of a single kiosk instance."""

    model_config = ConfigDict(frozen=True)

    uuid: str
    current_url: str
    is_running: bool
    error: str | None = None


class KioskSummary(BaseModel):
    """Lightweight summary of a kiosk instance for list views."""

    model_config = ConfigDict(frozen=True)

    uuid: str
    is_running: bool
    current_url: str


class NavigateRequest(BaseModel):
    """Request payload for navigating a kiosk to a new URL."""

    model_config = ConfigDict(frozen=True)

    url: str

    @field_validator("url")
    @classmethod
    def _validate_url(cls, v: str) -> str:
        return validate_url(v)
