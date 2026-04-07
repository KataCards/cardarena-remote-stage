from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.utils import validate_url


class ScheduleEntry(BaseModel):
    """A single scheduled content item with URL, duration, and display order."""

    model_config = ConfigDict(frozen=True)

    url: str
    duration_seconds: int = Field(gt=0)
    order: int = Field(ge=0)

    @field_validator("url")
    @classmethod
    def _validate_url(cls, v: str) -> str:
        return validate_url(v)


class AdBreak(BaseModel):
    """An advertisement break with URL and duration to be inserted between schedule entries."""

    model_config = ConfigDict(frozen=True)

    url: str
    duration_seconds: int = Field(gt=0)

    @field_validator("url")
    @classmethod
    def _validate_url(cls, v: str) -> str:
        return validate_url(v)


class ScheduleRequest(BaseModel):
    """Request payload for setting a kiosk's content schedule."""

    model_config = ConfigDict(frozen=True)

    entries: list[ScheduleEntry] = Field(min_length=1)
