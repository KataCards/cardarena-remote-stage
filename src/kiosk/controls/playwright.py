from __future__ import annotations

from ..utils.decorators.control_action import control_action
from ..engine.playwright import PlaywrightEngine
from .base import Controls
from pydantic import Field
from typing import Literal

from src.utils import validate_url


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

class PlaywrightControls(Controls):
    """Playwright-based implementation of browser controls."""

    control_type: str = Field(
        default="playwright",
        description="The type of browser controls",
        min_length=1,
    )

    engine: PlaywrightEngine = Field(
        ...,
        description="The PlaywrightEngine instance powering the kiosk",
    )

    # -------------------------------------------------------------------------
    # Validators
    # -------------------------------------------------------------------------

    @staticmethod
    def _is_valid_url(url: str) -> bool:
        """Validate URL format for basic safety checks."""
        try:
            validate_url(url)
        except ValueError:
            return False
        return True

    # -------------------------------------------------------------------------
    # Navigation
    # -------------------------------------------------------------------------

    @control_action
    async def navigate(self, url: str) -> bool:
        """Navigate to a URL."""
        if not url:
            raise ValueError(f"Invalid URL: {url}")
        if not self._is_valid_url(url):
            raise ValueError(f"Malformed URL: {url}")

        await self.engine._require_page().goto(url)
        return True

    @control_action
    async def reload(self) -> bool:
        """Reload the current page."""
        await self.engine._require_page().reload()
        return True

    @control_action
    async def go_back(self) -> bool:
        """Navigate back in browser history."""
        await self.engine._require_page().go_back()
        return True

    @control_action
    async def go_forward(self) -> bool:
        """Navigate forward in browser history."""
        await self.engine._require_page().go_forward()
        return True

    # -------------------------------------------------------------------------
    # Interaction
    # -------------------------------------------------------------------------

    @control_action
    async def click(self, x: int, y: int) -> bool:
        """Click at the given coordinates."""
        if x < 0 or y < 0:
            raise ValueError(f"Coordinates must be non-negative, got ({x}, {y})")

        await self.engine._require_page().mouse.click(x, y)
        return True

    @control_action
    async def type_text(self, text: str) -> bool:
        """Type text into the focused element."""
        await self.engine._require_page().keyboard.type(text)
        return True

    @control_action
    async def scroll(
        self,
        direction: Literal["up", "down", "left", "right"],
        amount: int,
    ) -> bool:
        """Scroll the page in the given direction."""
        if amount <= 0:
            raise ValueError(f"Scroll amount must be greater than 0, got {amount}")

        delta_x_unit, delta_y_unit = _SCROLL_MAP[direction]
        await self.engine._require_page().mouse.wheel(
            delta_x_unit * amount,
            delta_y_unit * amount,
        )
        return True

    @control_action
    async def press_key(self, key: str) -> bool:
        """Press a keyboard key."""
        if not key:
            raise ValueError(f"Invalid key: {key}")

        await self.engine._require_page().keyboard.press(key)
        return True

    # -------------------------------------------------------------------------
    # Waiting
    # -------------------------------------------------------------------------

    @control_action
    async def wait_for_navigation(self) -> bool:
        """Wait for navigation to complete."""
        await self.engine._require_page().wait_for_load_state()
        return True
