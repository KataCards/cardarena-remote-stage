import argparse
import sys
from datetime import datetime

from sqlalchemy.exc import IntegrityError

from ...base.principal import Scope
from ...config import get_settings
from .db import ApiKeyDatabase
from .models import ApiKeyCreate
from .repository import ApiKeyRepository


class ApiKeyCLI:
    """CLI interface for API key management."""

    def __init__(self) -> None:
        """Initialize CLI with database and repository."""
        settings = get_settings()
        db = ApiKeyDatabase(settings.apikey_db_path)
        db.initialise()
        self.repo = ApiKeyRepository(db)

    def create_key(self, name: str, scopes: list[str], expires: str | None = None) -> None:
        """Create a new API key and print the raw key.

        Args:
            name: Human-readable key name
            scopes: List of scope strings (e.g., ["read", "control"])
            expires: Optional ISO 8601 expiration date
        """
        # Parse scopes
        try:
            scope_enums = [Scope(s) for s in scopes]
        except ValueError:
            print(f"Error: Invalid scope. Valid scopes: {[s.value for s in Scope]}")
            sys.exit(1)

        # Parse expiration
        expires_at = None
        if expires:
            try:
                expires_at = datetime.fromisoformat(expires)
            except ValueError:
                print(f"Error: Invalid date format. Use ISO 8601 (e.g., 2024-12-31T23:59:59)")
                sys.exit(1)

        # Create key
        entry = ApiKeyCreate(name=name, scopes=scope_enums, expires_at=expires_at)
        try:
            result = self.repo.create(entry)
        except IntegrityError:
            print(f"Error: API key with name '{name}' already exists")
            sys.exit(1)

        # Print raw key (only time it's visible)
        print(f"\n✓ API key created: {result.id}")
        print(f"  Scopes: {[s.value for s in result.scopes]}")
        if result.expires_at:
            print(f"  Expires: {result.expires_at.isoformat()}")
        print(f"\n  Raw key (save this, it won't be shown again):")
        print(f"  {result.raw_key}\n")

    def list_keys(self) -> None:
        """List all API keys in a table format."""
        keys = self.repo.list_all()

        if not keys:
            print("No API keys found.")
            return

        # Print table header
        print(f"\n{'Name':<20} {'Scopes':<30} {'Revoked':<10} {'Expires':<20}")
        print("-" * 80)

        # Print rows
        for key in keys:
            scopes_str = ",".join([s.value for s in key.scopes])
            revoked_str = "✓" if key.revoked else ""
            expires_str = key.expires_at.isoformat() if key.expires_at else "Never"
            print(f"{key.id:<20} {scopes_str:<30} {revoked_str:<10} {expires_str:<20}")

        print()

    def revoke_key(self, name: str) -> None:
        """Revoke an API key (soft delete).

        Args:
            name: API key name to revoke
        """
        if self.repo.revoke(name):
            print(f"✓ API key '{name}' revoked")
        else:
            print(f"Error: API key '{name}' not found")
            sys.exit(1)

    def delete_key(self, name: str) -> None:
        """Permanently delete an API key (hard delete).

        Args:
            name: API key name to delete
        """
        if self.repo.hard_delete(name):
            print(f"✓ API key '{name}' deleted")
        else:
            print(f"Error: API key '{name}' not found")
            sys.exit(1)


def main() -> None:
    """CLI entry point with basic argument parsing."""
    # --- Setup ---
    parser = argparse.ArgumentParser(description="API Key Management CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- Commands ---
    # create command
    create_parser = subparsers.add_parser("create", help="Create a new API key")
    create_parser.add_argument("--name", required=True, help="Key name (e.g., 'dashboard')")
    create_parser.add_argument(
        "--scopes",
        required=True,
        help="Comma-separated scopes (e.g., 'read,control,admin')",
    )
    create_parser.add_argument("--expires", help="Expiration date (ISO 8601)")

    # list command
    subparsers.add_parser("list", help="List all API keys")

    # revoke command
    revoke_parser = subparsers.add_parser("revoke", help="Revoke an API key")
    revoke_parser.add_argument("--name", required=True, help="Key name to revoke")

    # delete command
    delete_parser = subparsers.add_parser("delete", help="Delete an API key")
    delete_parser.add_argument("--name", required=True, help="Key name to delete")

    args = parser.parse_args()

    # --- Dispatch ---
    cli = ApiKeyCLI()

    if args.command == "create":
        scopes = [s.strip() for s in args.scopes.split(",")]
        cli.create_key(args.name, scopes, args.expires)
    elif args.command == "list":
        cli.list_keys()
    elif args.command == "revoke":
        cli.revoke_key(args.name)
    elif args.command == "delete":
        cli.delete_key(args.name)


if __name__ == "__main__":
    main()