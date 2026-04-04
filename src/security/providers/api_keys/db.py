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
    """SQLAlchemy-based database for API key storage.

    Manages the engine, metadata, and table schema for API keys.
    The database is initialized and ready to use immediately after instantiation.
    """

    def __init__(self, db_path: str) -> None:
        """Initialize the database with the given path.

        Args:
            db_path: Path to the SQLite database file
        """
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
            Column("key_hash", Text, nullable=False),  # sha256 of raw key
            Column("scopes", Text, nullable=False),  # JSON array e.g. ["read", "control"]
            Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
            Column("expires_at", DateTime(timezone=True), nullable=True),  # None = no expiry
            Column("revoked", Boolean, nullable=False, default=False),
        )
        self.metadata.create_all(self.engine)