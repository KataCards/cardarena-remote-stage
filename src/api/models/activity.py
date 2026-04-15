from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ActivityEvent(BaseModel):
    """Immutable record of a single kiosk activity."""

    model_config = ConfigDict(frozen=True)

    timestamp: datetime
    event: str
    success: bool = True
    context: dict = Field(default_factory=dict)
