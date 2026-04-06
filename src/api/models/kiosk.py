"""Kiosk API request/response models."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, HttpUrl, field_validator


class KioskStatus(BaseModel):
    model_config = ConfigDict(frozen=True)

    uuid: str
    current_url: str
    is_running: bool
    error: str | None


class KioskSummary(BaseModel):
    model_config = ConfigDict(frozen=True)

    uuid: str
    is_running: bool
    current_url: str


class NavigateRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    url: str

    @field_validator("url")
    @classmethod
    def _validate_url(cls, v: str) -> str:
        HttpUrl(v)  # raises ValidationError directly if the URL is structurally invalid
        return v
