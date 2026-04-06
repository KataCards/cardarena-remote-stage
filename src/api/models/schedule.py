"""Schedule API request models."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class ScheduleEntry(BaseModel):
    model_config = ConfigDict(frozen=True)

    url: str
    duration_seconds: int
    order: int


class AdBreak(BaseModel):
    model_config = ConfigDict(frozen=True)

    url: str
    duration_seconds: int


class ScheduleRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    entries: list[ScheduleEntry]
