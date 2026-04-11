from __future__ import annotations

import json
import secrets
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import delete as sa_delete
from sqlalchemy import select, update
from sqlalchemy.engine import Row

from .models import ApiKeyCreate, ApiKeyCreated, ApiKeyRecord
from ...base.principal import Scope
from .db import ApiKeyDatabase
from .utils import hash_key


class ApiKeyRepository:
    """Repository for API key CRUD operations."""

    # -------------------------------------------------------------------------
    # Construction
    # -------------------------------------------------------------------------

    def __init__(self, db: ApiKeyDatabase, secret: str) -> None:
        """Initialize the repository."""
        self.db = db
        self._secret = secret

    # -------------------------------------------------------------------------
    # Internal Helpers
    # -------------------------------------------------------------------------

    @staticmethod
    def _ensure_tz_aware(value: datetime | None) -> datetime | None:
        """Normalize naive datetimes from SQLite to UTC-aware values."""
        if value is not None and value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value

    def _row_to_record(self, row: Row[Any]) -> ApiKeyRecord:
        """Convert a database row to an API key record."""
        scopes = [Scope(s) for s in json.loads(row.scopes)]
        return ApiKeyRecord(
            id=row.id,
            scopes=scopes,
            created_at=self._ensure_tz_aware(row.created_at),
            expires_at=self._ensure_tz_aware(row.expires_at),
            revoked=row.revoked,
        )

    # -------------------------------------------------------------------------
    # CRUD Operations
    # -------------------------------------------------------------------------

    def create(self, entry: ApiKeyCreate) -> ApiKeyCreated:
        """Create and persist a new API key."""
        raw_key = secrets.token_urlsafe(32)
        key_hash = hash_key(raw_key, self._secret)
        scopes_json = json.dumps([s.value for s in entry.scopes])

        with self.db.engine.begin() as conn:
            conn.execute(
                self.db.table.insert().values(
                    id=entry.name,
                    key_hash=key_hash,
                    scopes=scopes_json,
                    expires_at=entry.expires_at,
                    revoked=False,
                )
            )

            # Fetch the row back to get DB-generated created_at
            result = conn.execute(
                select(self.db.table).where(self.db.table.c.id == entry.name)
            ).fetchone()

        if result is None:
            raise RuntimeError(
                f"Failed to create API key '{entry.name}': inserted row could not be retrieved"
            )

        return ApiKeyCreated(
            id=result.id,
            scopes=entry.scopes,
            created_at=result.created_at,
            expires_at=result.expires_at,
            revoked=result.revoked,
            raw_key=raw_key,
        )

    # -------------------------------------------------------------------------
    # Lookup Operations
    # -------------------------------------------------------------------------

    def get_by_hash(self, key_hash: str) -> ApiKeyRecord | None:
        """Return an API key record by its hash."""
        with self.db.engine.connect() as conn:
            result = conn.execute(
                select(self.db.table).where(self.db.table.c.key_hash == key_hash)
            ).fetchone()

        if result is None:
            return None

        return self._row_to_record(result)

    def list_all(self) -> list[ApiKeyRecord]:
        """Return all API keys."""
        with self.db.engine.connect() as conn:
            results = conn.execute(select(self.db.table)).fetchall()

        return [self._row_to_record(row) for row in results]

    # -------------------------------------------------------------------------
    # Mutation Operations
    # -------------------------------------------------------------------------

    def revoke(self, name: str) -> bool:
        """Revoke an API key."""
        with self.db.engine.begin() as conn:
            result = conn.execute(
                update(self.db.table)
                .where(self.db.table.c.id == name)
                .values(revoked=True)
            )
        return result.rowcount > 0

    def hard_delete(self, name: str) -> bool:
        """Permanently delete an API key."""
        with self.db.engine.begin() as conn:
            result = conn.execute(
                sa_delete(self.db.table).where(self.db.table.c.id == name)
            )
        return result.rowcount > 0
