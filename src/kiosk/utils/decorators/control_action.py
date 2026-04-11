from __future__ import annotations

import functools
import logging
from typing import Awaitable, Callable, ParamSpec


P = ParamSpec("P")
logger = logging.getLogger(__name__)

def control_action(func: Callable[P, Awaitable[bool]],) -> Callable[P, Awaitable[bool]]:
    """Wrap a control action with consistent soft-failure handling.

    ValueError and RuntimeError are intentionally re-raised so callers can
    surface deterministic validation/lifecycle failures, while unexpected
    exceptions are logged and converted to False.
    """
    @functools.wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> bool:
        try:
            return await func(*args, **kwargs)
        except (ValueError, RuntimeError):
            raise
        except Exception:
            logger.exception("Control action '%s' failed", func.__name__)
            return False

    return wrapper
