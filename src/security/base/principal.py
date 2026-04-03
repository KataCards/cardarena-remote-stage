
from pydantic import BaseModel, ConfigDict, Field
from enum import StrEnum

class Scope(StrEnum):
    """Permission scopes for access control."""

    READ = "read"
    CONTROL = "control"
    ADMIN = "admin"


class Principal(BaseModel):
    """Immutable representation of an authenticated entity.

    A Principal represents a verified identity with associated permissions.
    Once created, a Principal cannot be modified (frozen=True).

    Attributes:
        id: Unique identifier for the principal (e.g., "apikey:abc123")
        auth_method: Authentication method used (e.g., "api_key", "bearer_token")
        scopes: List of permission scopes granted to this principal
        metadata: Additional context about the principal (e.g., key value, user info)
    """

    model_config = ConfigDict(frozen=True)

    id: str
    auth_method: str
    scopes: list[Scope]
    metadata: dict = Field(default_factory=dict)

    def has_scope(self, scope: Scope) -> bool:
        """Check if the principal has a specific scope.

        Args:
            scope: The scope to check for

        Returns:
            True if the principal has the scope, False otherwise
        """
        return scope in self.scopes

    def require_scope(self, scope: Scope) -> None:
        """Require that the principal has a specific scope.

        Args:
            scope: The required scope

        Raises:
            ValueError: If the principal does not have the required scope
        """
        if not self.has_scope(scope):
            raise ValueError(
                f"Principal '{self.id}' lacks required scope '{scope}'. "
                f"Granted: {list(self.scopes)}"
            )