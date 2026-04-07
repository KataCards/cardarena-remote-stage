from __future__ import annotations

"""Utility functions for API key operations."""

import hashlib
import hmac


def hash_key(raw_key: str, secret: str) -> str:
    """Hash a raw API key with HMAC-SHA256."""
    return hmac.new(secret.encode(), raw_key.encode(), hashlib.sha256).hexdigest()
