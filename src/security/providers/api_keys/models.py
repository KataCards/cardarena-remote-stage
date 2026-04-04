from datetime import datetime

from pydantic import BaseModel, Field

from ...base.principal import Scope


class ApiKeyCreate(BaseModel):
    """Request model for creating a new API key."""

    name: str = Field(..., min_length=1, max_length=255)
    scopes: list[Scope]
    expires_at: datetime | None = None


class ApiKeyRecord(BaseModel):
    """Database record representation (no key_hash exposed)."""

    id: str
    scopes: list[Scope]
    created_at: datetime
    expires_at: datetime | None
    revoked: bool


class ApiKeyCreated(ApiKeyRecord):
    """Response model returned only on key creation.
    
    Includes the raw key — this is the ONLY time it's visible.
    """

    raw_key: str