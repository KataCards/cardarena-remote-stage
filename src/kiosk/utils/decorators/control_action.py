from __future__ import annotations

from typing import Callable, Awaitable, ParamSpec
import functools


P = ParamSpec("P")

def control_action(func: Callable[P, Awaitable[bool]],) -> Callable[P, Awaitable[bool]]:
    """
    Decorator for PlaywrightControls action methods.

    Wraps async control methods with consistent error handling:
    - ValueError and RuntimeError propagate to the caller unchanged
    - All other exceptions are treated as soft failures and return False

    Args:
        func: The async method to wrap.

    Returns:
        The wrapped coroutine function.

    Example:
```python
        @control_action
        async def reload(self) -> bool:
            await self.engine.get_page().reload()
            return True
```
    """
    @functools.wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> bool:
        try:
            return await func(*args, **kwargs)
        except (ValueError, RuntimeError):
            raise
        except Exception:
            return False

    return wrapper