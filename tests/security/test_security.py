"""Minimum viable tests for the security package.

All database tests use ApiKeyDatabase(":memory:") — no filesystem side effects.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from src.security.base.principal import Principal, Scope
from src.security.providers.api_keys.db import ApiKeyDatabase
from src.security.providers.api_keys.models import ApiKeyCreate
from src.security.providers.api_keys.provider import ApiKeyProvider
from src.security.providers.api_keys.repository import ApiKeyRepository
from src.security.providers.api_keys.utils import hash_key


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def db() -> ApiKeyDatabase:
    """In-memory database, schema created, no filesystem side effects."""
    database = ApiKeyDatabase(":memory:")
    database.initialise()
    return database


_TEST_SECRET = "test-secret-value"


@pytest.fixture
def repo(db: ApiKeyDatabase) -> ApiKeyRepository:
    return ApiKeyRepository(db, _TEST_SECRET)


@pytest.fixture
def provider(repo: ApiKeyRepository) -> ApiKeyProvider:
    return ApiKeyProvider(repo, _TEST_SECRET)


@pytest.fixture
def mock_request() -> MagicMock:
    return MagicMock()


# ---------------------------------------------------------------------------
# Principal
# ---------------------------------------------------------------------------

class TestPrincipalHasScope:
    def test_returns_true_for_granted_scope(self):
        p = Principal(id="x", auth_method="api_key", scopes=[Scope.READ, Scope.ADMIN])
        assert p.has_scope(Scope.READ) is True
        assert p.has_scope(Scope.ADMIN) is True

    def test_returns_false_for_missing_scope(self):
        p = Principal(id="x", auth_method="api_key", scopes=[Scope.READ])
        assert p.has_scope(Scope.CONTROL) is False


class TestPrincipalRequireScope:
    def test_passes_when_scope_present(self):
        p = Principal(id="x", auth_method="api_key", scopes=[Scope.ADMIN])
        p.require_scope(Scope.ADMIN)  # should not raise

    def test_raises_value_error_on_missing_scope(self):
        p = Principal(id="x", auth_method="api_key", scopes=[Scope.READ])
        with pytest.raises(ValueError, match="lacks required scope"):
            p.require_scope(Scope.CONTROL)

    def test_frozen_model_raises_on_mutation(self):
        p = Principal(id="x", auth_method="api_key", scopes=[Scope.READ])
        with pytest.raises(Exception):  # ValidationError or TypeError from frozen=True
            p.id = "other"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# ApiKeyRepository
# ---------------------------------------------------------------------------

class TestApiKeyRepositoryCreate:
    def test_returns_raw_key_and_populates_created_at(self, repo: ApiKeyRepository):
        entry = ApiKeyCreate(name="test-key", scopes=[Scope.READ])
        result = repo.create(entry)

        assert result.id == "test-key"
        assert result.raw_key  # non-empty string
        assert len(result.raw_key) > 10
        assert result.scopes == [Scope.READ]
        assert result.created_at is not None
        assert result.revoked is False

    def test_raw_key_hashes_to_stored_hash(self, repo: ApiKeyRepository):
        entry = ApiKeyCreate(name="hash-check", scopes=[Scope.CONTROL])
        result = repo.create(entry)

        record = repo._get_by_hash(hash_key(result.raw_key, _TEST_SECRET))
        assert record is not None
        assert record.id == "hash-check"


class TestApiKeyRepositoryGetByHash:
    def test_returns_record_on_valid_hash(self, repo: ApiKeyRepository):
        entry = ApiKeyCreate(name="lookup-key", scopes=[Scope.READ])
        created = repo.create(entry)

        record = repo._get_by_hash(hash_key(created.raw_key, _TEST_SECRET))
        assert record is not None
        assert record.id == "lookup-key"

    def test_returns_none_on_unknown_hash(self, repo: ApiKeyRepository):
        record = repo._get_by_hash(hash_key("nonexistent-key-value", _TEST_SECRET))
        assert record is None


# ---------------------------------------------------------------------------
# ApiKeyProvider.verify
# ---------------------------------------------------------------------------

class TestApiKeyProviderVerify:
    @pytest.mark.asyncio
    async def test_valid_key_returns_principal(
        self, repo: ApiKeyRepository, provider: ApiKeyProvider, mock_request: MagicMock
    ):
        entry = ApiKeyCreate(name="valid-key", scopes=[Scope.READ, Scope.CONTROL])
        created = repo.create(entry)

        principal = await provider.verify(created.raw_key, mock_request)

        assert isinstance(principal, Principal)
        assert principal.auth_method == "api_key"
        assert Scope.READ in principal.scopes
        assert Scope.CONTROL in principal.scopes

    @pytest.mark.asyncio
    async def test_missing_credentials_raises_401(
        self, provider: ApiKeyProvider, mock_request: MagicMock
    ):
        with pytest.raises(HTTPException) as exc_info:
            await provider.verify(None, mock_request)
        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_invalid_key_raises_401(
        self, provider: ApiKeyProvider, mock_request: MagicMock
    ):
        with pytest.raises(HTTPException) as exc_info:
            await provider.verify("not-a-real-key", mock_request)
        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_revoked_key_raises_401(
        self, repo: ApiKeyRepository, provider: ApiKeyProvider, mock_request: MagicMock
    ):
        entry = ApiKeyCreate(name="revoke-me", scopes=[Scope.READ])
        created = repo.create(entry)
        repo.revoke("revoke-me")

        with pytest.raises(HTTPException) as exc_info:
            await provider.verify(created.raw_key, mock_request)
        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_expired_key_raises_401(
        self, repo: ApiKeyRepository, provider: ApiKeyProvider, mock_request: MagicMock
    ):
        past = datetime.now(timezone.utc) - timedelta(hours=1)
        entry = ApiKeyCreate(name="expired-key", scopes=[Scope.READ], expires_at=past)
        created = repo.create(entry)

        with pytest.raises(HTTPException) as exc_info:
            await provider.verify(created.raw_key, mock_request)
        assert exc_info.value.status_code == 401
