from fastapi import Depends, HTTPException, Request

from .base.principal import Principal, Scope
from .config import get_active_provider

# Build get_principal once at import time for stable Depends reference and correct OpenAPI schema.
# NOTE: This triggers DB/provider construction at import time, before app.py startup validation.
#       Step 11 startup validation will need to account for this — if DB path is wrong or env is
#       misconfigured, the error surfaces here at import, not at app startup.
_provider = get_active_provider()


async def get_principal(
    request: Request,
    credentials=Depends(_provider.openapi_scheme),
) -> Principal:
    """FastAPI dependency that authenticates the request and returns a Principal.

    Delegates to the active SecurityProvider. Raises HTTPException 401/403
    on failure — never returns None.
    """
    return await _provider.verify(credentials, request)


def require_scope(scope: Scope):
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
        except ValueError as e:
            raise HTTPException(status_code=403, detail=str(e))
        return principal

    # Give the inner function a unique name for distinct dependency nodes.
    check_scope.__name__ = f"require_scope_{scope}"
    return check_scope