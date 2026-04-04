import json
import secrets

from sqlalchemy import delete as sa_delete
from sqlalchemy import select, update

from .models import ApiKeyCreate, ApiKeyCreated, ApiKeyRecord
from ...base.principal import Scope
from .db import ApiKeyDatabase
from .utils import hash_key

class ApiKeyRepository:
    """Repository for API key CRUD operations.
    
    Encapsulates all database interactions for API keys using SQLAlchemy Core.
    """

    def __init__(self, db: ApiKeyDatabase) -> None:
        """Initialize the repository with a database instance.

        Args:
            db: ApiKeyDatabase instance managing engine and table schema
        """
        self.db = db

    def _row_to_record(self, row) -> ApiKeyRecord:
        """Convert a database row to an ApiKeyRecord.

        Args:
            row: SQLAlchemy row result

        Returns:
            ApiKeyRecord instance
        """
        scopes = [Scope(s) for s in json.loads(row.scopes)]
        return ApiKeyRecord(
            id=row.id,
            scopes=scopes,
            created_at=row.created_at,
            expires_at=row.expires_at,
            revoked=row.revoked,
        )

    def create(self, entry: ApiKeyCreate) -> ApiKeyCreated:
        """Create a new API key.

        Generates a secure random key, hashes it immediately, and stores the record.
        The database generates the created_at timestamp.

        Args:
            entry: API key creation request

        Returns:
            ApiKeyCreated with the raw key (only time it's visible)

        Raises:
            IntegrityError: If a key with the same name already exists
        """
        raw_key = secrets.token_urlsafe(32)
        key_hash = hash_key(raw_key)
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

        return ApiKeyCreated(
            id=result.id,
            scopes=entry.scopes,
            created_at=result.created_at,
            expires_at=result.expires_at,
            revoked=result.revoked,
            raw_key=raw_key,
        )

    def _get_by_hash(self, key_hash: str) -> ApiKeyRecord | None:
        """Retrieve an API key record by its hash.

        Primary lookup path for verify() operations.

        Args:
            key_hash: SHA-256 hash of the raw key

        Returns:
            ApiKeyRecord if found, None otherwise
        """
        with self.db.engine.connect() as conn:
            result = conn.execute(
                select(self.db.table).where(self.db.table.c.key_hash == key_hash)
            ).fetchone()

        if result is None:
            return None

        return self._row_to_record(result)

    def list_all(self) -> list[ApiKeyRecord]:
        """List all API keys in the database.

        Returns:
            List of all API key records
        """
        with self.db.engine.connect() as conn:
            results = conn.execute(select(self.db.table)).fetchall()

        return [self._row_to_record(row) for row in results]

    def revoke(self, name: str) -> bool:
        """Revoke an API key (soft delete).

        Sets revoked=True, preventing future authentication.

        Args:
            name: API key name (id)

        Returns:
            True if key was found and revoked, False if not found
        """
        with self.db.engine.begin() as conn:
            result = conn.execute(
                update(self.db.table)
                .where(self.db.table.c.id == name)
                .values(revoked=True)
            )
        return result.rowcount > 0

    def hard_delete(self, name: str) -> bool:
        """Permanently delete an API key (hard delete).

        Args:
            name: API key name (id)

        Returns:
            True if key was found and deleted, False if not found
        """
        with self.db.engine.begin() as conn:
            result = conn.execute(
                sa_delete(self.db.table).where(self.db.table.c.id == name)
            )
        return result.rowcount > 0