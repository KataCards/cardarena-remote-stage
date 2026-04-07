from __future__ import annotations

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Engine,
    MetaData,
    Table,
    Text,
    create_engine,
    func,
)


class ApiKeyDatabase:
    """SQLAlchemy-based database for API key storage."""

    def __init__(self, db_path: str) -> None:
        """Prepare the engine and table definition."""
        self.engine: Engine = create_engine(
            f"sqlite:///{db_path}",
            echo=False,
            connect_args={"check_same_thread": False},
        )
        self.metadata = MetaData()
        self.table = Table(
            "api_keys",
            self.metadata,
            Column("id", Text, primary_key=True),  # human-readable name e.g. "dashboard"
            Column("key_hash", Text, nullable=False),  # HMAC-SHA256 of raw key
            Column("scopes", Text, nullable=False),  # JSON array e.g. ["read", "control"]
            Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
            Column("expires_at", DateTime(timezone=True), nullable=True),  # None = no expiry
            Column("revoked", Boolean, nullable=False, default=False),
        )

    def initialise(self) -> None:
        """Create the database schema. Must be called once at app startup."""
        self.metadata.create_all(self.engine)
