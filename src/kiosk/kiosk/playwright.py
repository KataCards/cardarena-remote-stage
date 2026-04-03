from __future__ import annotations

from ..controls.playwright import PlaywrightControls
from ..engine.playwright import PlaywrightEngine
from pydantic import Field
from .base import Kiosk
from typing import Any
import asyncio


class PlaywrightKiosk(Kiosk):
    """
    Playwright-based kiosk orchestration layer.

    This is the concrete implementation of the abstract Kiosk base class. It wires
    together PlaywrightEngine and PlaywrightControls into a single orchestration
    layer exposed to the API.

    Features:
    - Automatic error page navigation via injected async callback
    - Retry logic for navigation failures with exponential backoff
    - Type-safe engine and controls binding

    Attributes:
        engine: The PlaywrightEngine instance powering the kiosk.
        controls: The PlaywrightControls instance (None until start() is called).
        max_retries: Maximum number of navigation retry attempts.
        retry_delay: Base delay in seconds between retries (exponential backoff).

    Example:
        ```python
        async with PlaywrightKiosk(
            engine=PlaywrightEngine(
                browser_type="chromium",
                headless=True,
                default_page="https://example.com",
                error_map={404: "not_found"},
                resources={"not_found": "/path/to/404.html"},
            ),
            default_page="https://example.com",
            kiosk_name="Main Kiosk",
            max_retries=3,
            retry_delay=1.0,
        ) as kiosk:
            await kiosk.navigate("https://example.com/page")
            screenshot = await kiosk.screenshot()
        ```
    """

    engine: PlaywrightEngine = Field(
        ...,
        description="The PlaywrightEngine instance powering the kiosk",
    )

    controls: PlaywrightControls | None = Field(
        default=None,
        description="The PlaywrightControls instance (None until start() is called)",
    )

    max_retries: int = Field(
        default=3,
        ge=1,
        description="Maximum number of navigation retry attempts",
    )

    retry_delay: float = Field(
        default=1.0,
        gt=0,
        description="Base delay in seconds between retries (exponential backoff)",
    )

    def model_post_init(self, _: Any) -> None:
        """Wire error callback to engine after initialization."""
        self.engine.on_error = self._on_error

    # -------------------------------------------------------------------------
    # Lifecycle Methods
    # -------------------------------------------------------------------------

    async def start(self) -> None:
        """
        Start the kiosk by launching the engine and mounting controls.

        Execution order:
        1. Mount PlaywrightControls with engine reference
        2. Launch the browser engine
        3. Navigate to default_page with retry logic
        4. Set is_running to True

        Raises:
            RuntimeError: If engine launch fails or navigation exhausts all retries.
        """
        self.controls = PlaywrightControls(engine=self.engine)
        await self.engine.launch()
        await self._navigate_with_retry(self.default_page)
        self.is_running = True

    async def stop(self) -> None:
        """
        Stop the kiosk by closing the engine and unmounting controls.

        Execution order:
        1. Set is_running to False
        2. Unmount controls (set to None)
        3. Close the browser engine

        Raises:
            RuntimeError: If engine shutdown fails.
        """
        self.is_running = False
        self.controls = None
        await self.engine.close()

    # -------------------------------------------------------------------------
    # Error Handling
    # -------------------------------------------------------------------------

    async def _on_error(self, error_code: int) -> None:
        """
        Async callback injected into engine for error page navigation.

        Triggered by the engine's response listener when an HTTP error occurs.
        Navigates to the error page resource mapped to the error code.

        Note:
            If controls are not mounted (before `start()` is called), the error is silently ignored.

        Args:
            error_code: HTTP status code that triggered the error.
        """
        if self.controls is None:
            return

        path = await self.engine.handle_error(error_code)
        await self.controls.navigate(f"file://{path}")

    # -------------------------------------------------------------------------
    # Navigation with Retry
    # -------------------------------------------------------------------------

    async def _navigate_with_retry(self, url: str) -> None:
        """
        Navigate to URL with exponential backoff retry logic.

        Attempts navigation up to max_retries times. On failure, waits
        retry_delay * 2^attempt seconds before retrying.

        Args:
            url: The URL to navigate to.

        Raises:
            RuntimeError: If all retry attempts are exhausted.
        """
        controls = self._require_controls()
        for attempt in range(self.max_retries):
            if await controls.navigate(url):
                return

            if attempt < self.max_retries - 1:
                await asyncio.sleep(self.retry_delay * (2 ** attempt))

        raise RuntimeError(
            f"Failed to navigate to '{url}' after {self.max_retries} attempts"
        )

    # -------------------------------------------------------------------------
    # Navigation Methods
    # -------------------------------------------------------------------------

    async def go_home(self) -> bool:
        """
        Navigate to the default page.

        Returns:
            True if navigation succeeded.

        Raises:
            RuntimeError: If controls are not mounted or navigation fails.
        """
        await self._navigate_with_retry(self.default_page)
        return True