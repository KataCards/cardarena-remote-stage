from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError

from ...base.principal import Scope
from ...dependencies import require_scope
from .models import ApiKeyCreate, ApiKeyCreated, ApiKeyRecord
from .repository import ApiKeyRepository


def build_router(repo: ApiKeyRepository) -> APIRouter:
    """Build and configure the API keys router.

    Args:
        repo: Pre-configured API key repository instance

    Returns:
        Configured APIRouter with all API key endpoints
    """
    router = APIRouter(prefix="/security/keys", tags=["API Keys"])


    @router.post("", response_model=ApiKeyCreated, status_code=201)
    async def create_key(
        entry: ApiKeyCreate,
        _=Depends(require_scope(Scope.ADMIN)),
    ) -> ApiKeyCreated:
        """Create a new API key.

        Returns the raw key — this is the ONLY time it will be visible.

        Raises:
            HTTPException: 409 if a key with the same name already exists
        """
        try:
            return repo.create(entry)
        except IntegrityError:
            raise HTTPException(
                status_code=409, detail=f"API key with name '{entry.name}' already exists"
            )


    @router.get("", response_model=list[ApiKeyRecord])
    async def list_keys(
        _=Depends(require_scope(Scope.ADMIN)),
    ) -> list[ApiKeyRecord]:
        """List all API keys.

        Returns list of all API key records (no raw keys or hashes).
        """
        return repo.list_all()


    @router.delete("/{name}", status_code=204)
    async def revoke_key(
        name: str,
        _=Depends(require_scope(Scope.ADMIN)),
    ) -> None:
        """Revoke an API key (soft delete).

        Sets revoked=True, preventing future authentication.

        Raises:
            HTTPException: 404 if key not found
        """
        if not repo.revoke(name):
            raise HTTPException(status_code=404, detail=f"API key '{name}' not found")


    @router.delete("/{name}/hard", status_code=204)
    async def delete_key(
        name: str,
        _=Depends(require_scope(Scope.ADMIN)),
    ) -> None:
        """Permanently delete an API key (hard delete).

        Raises:
            HTTPException: 404 if key not found
        """
        if not repo.hard_delete(name):
            raise HTTPException(status_code=404, detail=f"API key '{name}' not found")

    return router