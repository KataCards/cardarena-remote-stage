from __future__ import annotations

"""API Key authentication module.

Provides database-backed API key authentication with:
- Secure key generation and hashing
- Scope-based authorization
- Revocation and expiration support
- FastAPI router for admin endpoints
- CLI for key management
"""

from .provider import ApiKeyProvider
from .models import ApiKeyCreate, ApiKeyRecord, ApiKeyCreated
from .utils import hash_key

__all__ = [
    "ApiKeyProvider",
    "ApiKeyCreate",
    "ApiKeyRecord",
    "ApiKeyCreated",
    "hash_key",
]
