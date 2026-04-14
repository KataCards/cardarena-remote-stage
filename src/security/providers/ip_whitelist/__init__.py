"""IP whitelist security provider.

This module provides IP-based authentication where requests are authenticated
based on the client's IP address against a whitelist.
"""

from __future__ import annotations

from .provider import IpWhitelistProvider
from .scheme import NoCredentialsScheme

__all__ = ["IpWhitelistProvider", "NoCredentialsScheme"]
