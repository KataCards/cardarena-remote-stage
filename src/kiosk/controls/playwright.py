from __future__ import annotations

from ..utils.decorators.control_action import control_action
from ..engine.playwright import PlaywrightEngine
from .base import Controls
from typing import Literal
import re


# -------------------------------------------------------------------------
# Constants
# -------------------------------------------------------------------------

# Direction to (delta_x, delta_y) mapping for mouse wheel scrolling
_SCROLL_MAP: dict[str, tuple[int, int]] = {
    "up": (0, -1),
    "down": (0, 1),
    "left": (-1, 0),
    "right": (1, 0),
}

# Basic URL validation pattern (http/https/file protocols)
_URL_PATTERN = re.compile(
    r'^(https?|file)://'       # Protocol
    r'(//'                      # Optional authority for file://
    r'([a-zA-Z0-9.-]+|\[[0-9a-fA-F:]+\])'  # Domain or IPv6
    r'(:[0-9]+)?)?'             # Optional port
    r'(/.*)?$',                 # Optional path
    re.IGNORECASE
)

class PlaywrightControls(Controls):
    """
    Playwright-based implementation of browser controls.

    Bridges the abstract Controls interface with Playwright's browser automation
    capabilities. All operations are performed on the active Page instance via
    self.engine.get_page().

    Error handling:
    - ValueError / RuntimeError: always raised (invalid input or engine not running)
    - All other exceptions: soft failure, returns False

    Attributes:
        engine: The PlaywrightEngine instance providing browser automation.

    Example:
        ```python
        async with PlaywrightEngine(browser_type="chromium", ...) as engine:
            controls = PlaywrightControls(engine=engine)
            await controls.navigate("https://example.com")
            await controls.click(100, 200)
        ```
    """

    engine: PlaywrightEngine

    # -------------------------------------------------------------------------
    # Validators
    # -------------------------------------------------------------------------

    @staticmethod
    def _is_valid_url(url: str) -> bool:
        """Validate URL format for basic safety checks."""
        return bool(_URL_PATTERN.match(url))

    # -------------------------------------------------------------------------
    # Navigation
    # -------------------------------------------------------------------------

    @control_action
    async def navigate(self, url: str) -> bool:
        """
        Raises:
            ValueError: If URL is empty, not a string, or malformed.
            RuntimeError: If engine is not running.
        """
        if not url or not isinstance(url, str):
            raise ValueError(f"Invalid URL: {url}")
        if not self._is_valid_url(url):
            raise ValueError(f"Malformed URL: {url}")

        await self.engine.get_page().goto(url)
        return True

    @control_action
    async def reload(self) -> bool:
        """
        Raises:
            RuntimeError: If engine is not running.
        """
        await self.engine.get_page().reload()
        return True

    @control_action
    async def go_back(self) -> bool:
        """
        Returns False if no history is available or navigation timed out.

        Raises:
            RuntimeError: If engine is not running.
        """
        await self.engine.get_page().go_back()
        return True

    @control_action
    async def go_forward(self) -> bool:
        """
        Returns False if no forward history exists or navigation timed out.

        Raises:
            RuntimeError: If engine is not running.
        """
        await self.engine.get_page().go_forward()
        return True

    # -------------------------------------------------------------------------
    # Interaction
    # -------------------------------------------------------------------------

    @control_action
    async def click(self, x: int, y: int) -> bool:
        """
        Raises:
            ValueError: If coordinates are negative.
            RuntimeError: If engine is not running.
        """
        if x < 0 or y < 0:
            raise ValueError(f"Coordinates must be non-negative, got ({x}, {y})")

        await self.engine.get_page().mouse.click(x, y)
        return True

    @control_action
    async def type_text(self, text: str) -> bool:
        """
        Raises:
            RuntimeError: If engine is not running.
        """
        await self.engine.get_page().keyboard.type(text)
        return True

    @control_action
    async def scroll(
        self,
        direction: Literal["up", "down", "left", "right"],
        amount: int,
    ) -> bool:
        """
        Translates direction + amount into Playwright mouse.wheel(delta_x, delta_y).

        Example:
            ```python
            await controls.scroll("down", 500)
            await controls.scroll("left", 200)
            ```

        Raises:
            ValueError: If amount is zero or negative.
            RuntimeError: If engine is not running.
        """
        if amount <= 0:
            raise ValueError(f"Scroll amount must be greater than 0, got {amount}")

        delta_x_unit, delta_y_unit = _SCROLL_MAP[direction]
        await self.engine.get_page().mouse.wheel(
            delta_x_unit * amount,
            delta_y_unit * amount,
        )
        return True

    @control_action
    async def press_key(self, key: str) -> bool:
        """
        Raises:
            ValueError: If key is empty or not a string.
            RuntimeError: If engine is not running.
        """
        if not key or not isinstance(key, str):
            raise ValueError(f"Invalid key: {key}")

        await self.engine.get_page().keyboard.press(key)
        return True

    # -------------------------------------------------------------------------
    # Waiting
    # -------------------------------------------------------------------------

    @control_action
    async def wait_for_navigation(self) -> bool:
        """
        Waits for the page to reach 'load' state.

        Raises:
            RuntimeError: If engine is not running.
        """
        await self.engine.get_page().wait_for_load_state()
        return True