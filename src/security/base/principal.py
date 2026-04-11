from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field
from enum import StrEnum

class Scope(StrEnum):
    """Permission scopes for access control."""

    READ = "read"
    CONTROL = "control"
    ADMIN = "admin"


class Principal(BaseModel):
    """Immutable representation of an authenticated entity."""

    model_config = ConfigDict(frozen=True)

    id: str
    auth_method: str
    scopes: list[Scope]
    metadata: dict = Field(default_factory=dict)

    def has_scope(self, scope: Scope) -> bool:
        """Return whether the principal has the given scope."""
        return scope in self.scopes

    def require_scope(self, scope: Scope) -> None:
        """Raise if the principal lacks the given scope."""
        if not self.has_scope(scope):
            raise ValueError(
                f"Principal '{self.id}' lacks required scope '{scope}'. "
                f"Granted: {list(self.scopes)}"
            )
