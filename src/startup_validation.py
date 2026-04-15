from __future__ import annotations

import os
from pathlib import Path

from src.api.registry import KioskRegistry
from src.config import Settings
from src.security.config import SecuritySettings


def check_app_config(settings: Settings) -> None:
    """Raise if required filesystem paths referenced in app config do not exist."""
    if settings.kiosk_error_routing and settings.kiosk_error_pages_dir:
        path = Path(settings.kiosk_error_pages_dir)
        if not path.is_dir():
            raise RuntimeError(
                f"kiosk_error_pages_dir does not exist or is not a directory: {path}"
            )


def check_security_config(settings: SecuritySettings) -> None:
    """Raise if the active security provider is misconfigured."""
    provider = settings.security_provider

    if provider not in ("api_key", "ip_whitelist"):
        raise RuntimeError(
            f"Unknown security_provider '{provider}'. "
            "Supported values: 'api_key', 'ip_whitelist'."
        )

    if provider == "api_key":
        if not settings.apikey_secret.get_secret_value():
            raise RuntimeError(
                "apikey_secret is empty — all authentication would fail. "
                "Set a non-empty value for APIKEY_SECRET."
            )
        db_file = Path(settings.apikey_db_path)
        target = db_file if db_file.exists() else db_file.parent
        if not os.access(target, os.W_OK):
            raise RuntimeError(
                f"API key database path is not writable: {settings.apikey_db_path}"
            )

    elif provider == "ip_whitelist":
        if not settings.allowed_ips:
            raise RuntimeError(
                "ip_whitelist provider has no allowed_ips — every request would be "
                "rejected with 403. Set ALLOWED_IPS to a comma-separated list of "
                "authorised IP addresses."
            )


def check_registry_populated(registry: KioskRegistry) -> None:
    """Raise if no kiosks were registered after startup."""
    if not registry.list_all():
        raise RuntimeError(
            "Registry is empty after startup — no kiosks were registered. "
            "Check factory configuration."
        )
