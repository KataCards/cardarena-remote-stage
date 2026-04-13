from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.exc import IntegrityError

from src.api.routes.openapi import error_responses
from ...base.principal import Scope
from ...dependencies import require_scope
from src.utils import ErrorCode, raise_http
from .models import ApiKeyCreate, ApiKeyCreated, ApiKeyRecord
from .repository import ApiKeyRepository


def build_router(repo: ApiKeyRepository) -> APIRouter:
    """Build the API keys router."""
    router = APIRouter(
        prefix="/security/keys",
        tags=["API Keys"],
        responses=error_responses(401, 403, 404, 409, 422),
    )

    @router.post("", response_model=ApiKeyCreated, status_code=201, summary="Create API key")
    async def create_key(
        entry: ApiKeyCreate,
        _=Depends(require_scope(Scope.ADMIN)),
    ) -> ApiKeyCreated:
        """Create a new API key."""
        try:
            return repo.create(entry)
        except IntegrityError:
            raise_http(
                409,
                ErrorCode.conflict,
                f"API key '{entry.name}' already exists",
            )

    @router.get("", response_model=list[ApiKeyRecord], summary="List API keys")
    async def list_keys(
        _=Depends(require_scope(Scope.ADMIN)),
    ) -> list[ApiKeyRecord]:
        """List all API keys."""
        return repo.list_all()

    @router.delete("/{name}", status_code=204, summary="Revoke API key")
    async def revoke_key(
        name: str,
        _=Depends(require_scope(Scope.ADMIN)),
    ) -> None:
        """Revoke an API key."""
        if not repo.revoke(name):
            raise_http(404, ErrorCode.not_found, f"API key '{name}' not found")

    @router.delete("/{name}/hard", status_code=204, summary="Delete API key")
    async def delete_key(
        name: str,
        _=Depends(require_scope(Scope.ADMIN)),
    ) -> None:
        """Permanently delete an API key."""
        if not repo.hard_delete(name):
            raise_http(404, ErrorCode.not_found, f"API key '{name}' not found")

    return router
