from __future__ import annotations

from typing import Callable, Awaitable, ParamSpec
import functools


P = ParamSpec("P")

def control_action(func: Callable[P, Awaitable[bool]],) -> Callable[P, Awaitable[bool]]:
    """Wrap a control action with consistent soft-failure handling."""
    @functools.wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> bool:
        try:
            return await func(*args, **kwargs)
        except (ValueError, RuntimeError):
            raise
        except Exception:
            return False

    return wrapper
