"""Utility functions for API key operations."""

import hashlib


def hash_key(raw_key: str) -> str:
    """Hash a raw API key using SHA-256.

    Args:
        raw_key: The raw API key string

    Returns:
        Hexadecimal SHA-256 hash
    """
    return hashlib.sha256(raw_key.encode()).hexdigest()