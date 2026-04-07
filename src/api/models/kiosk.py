from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, field_validator

from src.utils import validate_url


class KioskStatus(BaseModel):
    """Full status snapshot of a single kiosk instance."""

    model_config = ConfigDict(frozen=True)

    uuid: str
    engine_type: str
    current_url: str
    is_running: bool
    error: str | None = None


class KioskSummary(BaseModel):
    """Lightweight summary of a kiosk instance for list views."""

    model_config = ConfigDict(frozen=True)

    uuid: str
    engine_type: str
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


class ClickRequest(BaseModel):
    """Request payload for clicking at coordinates."""

    model_config = ConfigDict(frozen=True)

    x: int
    y: int


class TypeTextRequest(BaseModel):
    """Request payload for typing text."""

    model_config = ConfigDict(frozen=True)

    text: str


class ScrollRequest(BaseModel):
    """Request payload for scrolling."""

    model_config = ConfigDict(frozen=True)

    direction: Literal["up", "down", "left", "right"]
    amount: int


class PressKeyRequest(BaseModel):
    """Request payload for pressing a key."""

    model_config = ConfigDict(frozen=True)

    key: str
