from __future__ import annotations

from collections.abc import Awaitable, Callable

from fastapi import Depends, HTTPException, Request

from .base.principal import Principal, Scope
from .config import get_active_provider

_provider = get_active_provider()


async def get_principal(
    request: Request,
    credentials: str | None = Depends(_provider.openapi_scheme),
) -> Principal:
    """FastAPI dependency that authenticates the request and returns a Principal.

    Delegates to the active SecurityProvider. Raises HTTPException 401/403
    on failure — never returns None.
    """
    return await _provider.verify(credentials, request)


def require_scope(scope: Scope) -> Callable[..., Awaitable[Principal]]:
    """Dependency factory that asserts the principal holds a specific scope.

    Usage:
        Depends(require_scope(Scope.CONTROL))

    Raises:
        HTTPException 403: If the principal lacks the required scope.
    """

    async def check_scope(
        principal: Principal = Depends(get_principal),
    ) -> Principal:
        try:
            principal.require_scope(scope)
        except ValueError:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return principal

    # Give the inner function a unique name for distinct dependency nodes.
    check_scope.__name__ = f"require_scope_{scope}"
    return check_scope
