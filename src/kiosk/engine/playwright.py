from __future__ import annotations

from pydantic import Field, PrivateAttr
from playwright.async_api import (
    async_playwright,
    Playwright,
    Browser,
    Page,
    Response,
)
from typing import Any, Literal
from .base import Engine


class PlaywrightEngine(Engine):
    """
    Playwright-based browser automation engine.

    This engine uses Playwright's async API to manage Chromium, Firefox, or WebKit
    browsers. It provides full lifecycle management, error handling via response
    listeners, and cookie/storage management.

    The engine automatically wires a response listener during launch() that monitors
    HTTP responses and triggers error handling for configured error codes.

    Attributes:
        browser_type: Browser to launch ('chromium', 'firefox', or 'webkit').
        headless: Whether to run browser in headless mode (no visible UI).

    Example:
        ```python
        async with PlaywrightEngine(
            browser_type="chromium",
            headless=True,
            default_page="https://example.com",
            error_map={404: "not_found"},
            resources={"not_found": "/path/to/404.html"},
            on_error=lambda code: print(f"Error {code}"),
        ) as engine:
            url = await engine.get_current_url()
            screenshot = await engine.screenshot()
        ```
    """

    browser_type: Literal["chromium", "firefox", "webkit"] = Field(
        default="chromium",
        description="Browser engine to use",
    )

    headless: bool = Field(
        default=True,
        description="Run browser in headless mode",
    )

    launch_args: list[str] = Field(
        default_factory=list,
        description="Additional command-line arguments to pass to the browser",
    )

    engine_type: str = Field(
        default="",
        description="The type of browser engine",
        min_length=0,
    )

    # Private runtime state - populated during launch(), cleared during close()
    _playwright: Playwright | None = PrivateAttr(default=None)
    _browser: Browser | None = PrivateAttr(default=None)
    _page: Page | None = PrivateAttr(default=None)

    def model_post_init(self, _: Any) -> None:
        """Post-init hook to populate engine_type from browser_type."""
        self.engine_type = f"playwright-{self.browser_type}"

    # -------------------------------------------------------------------------
    # Lifecycle Methods
    # -------------------------------------------------------------------------

    async def launch(self) -> None:
        """
        Launch the Playwright browser engine.

        Execution order:
        1. Check if already launched (idempotent guard)
        2. Start Playwright async instance
        3. Launch browser using configured browser_type and headless flag
        4. Create new page
        5. Wire response listener (monitors HTTP responses, calls handle_error on errors)

        The response listener is critical: it intercepts all HTTP responses and
        triggers error handling for any status code configured in error_map.

        Note: The response listener is synchronous and calls handle_error directly.

        Raises:
            RuntimeError: If Playwright fails to start, browser fails to launch,
                         or navigation to default_page fails.
        """
        # Idempotent guard - prevent duplicate browser instances
        if self._browser is not None:
            return

        try:
            self._playwright = await async_playwright().start()
            browser_launcher = getattr(self._playwright, self.browser_type)
            self._browser = await browser_launcher.launch(
                headless=self.headless,
                args=self.launch_args,
            )

            self._page = await self._browser.new_page()
            self._page.on("response", self._handle_response)

        except Exception as e:
            # Clean up partial state on failure
            await self.close()
            raise RuntimeError(f"Failed to launch Playwright engine: {e}") from e

    async def close(self) -> None:
        """
        Close the Playwright browser engine and release all resources.

        Execution order:
        1. Close page
        2. Close browser
        3. Stop Playwright instance
        4. Reset all private attributes to None

        This method is idempotent - safe to call multiple times.

        Raises:
            RuntimeError: If cleanup fails (all errors collected and raised together).
        """
        errors: list[str] = []

        if self._page is not None:
            try:
                await self._page.close()
            except Exception as e:
                errors.append(f"Failed to close page: {e}")
            finally:
                self._page = None

        if self._browser is not None:
            try:
                await self._browser.close()
            except Exception as e:
                errors.append(f"Failed to close browser: {e}")
            finally:
                self._browser = None

        if self._playwright is not None:
            try:
                await self._playwright.stop()
            except Exception as e:
                errors.append(f"Failed to stop Playwright: {e}")
            finally:
                self._playwright = None

        if errors:
            raise RuntimeError(f"Errors during engine shutdown: {'; '.join(errors)}")

    # -------------------------------------------------------------------------
    # Page State Methods
    # -------------------------------------------------------------------------

    async def get_current_url(self) -> str:
        """
        Get the current URL of the active page.

        Returns:
            Current page URL as a string.

        Raises:
            RuntimeError: If engine is not running or page is not available.
        """
        return self._require_page().url

    async def screenshot(self) -> bytes:
        """
        Capture a screenshot of the current page.

        Returns:
            Screenshot as raw PNG bytes.

        Raises:
            RuntimeError: If engine is not running, page is not available,
                         or screenshot capture fails.
        """
        try:
            return await self._require_page().screenshot()
        except Exception as e:
            raise RuntimeError(f"Failed to capture screenshot: {e}") from e

    # -------------------------------------------------------------------------
    # Storage Methods
    # -------------------------------------------------------------------------

    async def get_cookies(self) -> list[dict[str, Any]]:
        """
        Retrieve all cookies from the current browser context.

        Returns:
            List of cookie dictionaries. Each cookie contains keys like:
            'name', 'value', 'domain', 'path', 'expires', 'httpOnly', 'secure', 'sameSite'.

        Raises:
            RuntimeError: If engine is not running or page is not available.
        """
        return await self._require_page().context.cookies()

    async def set_cookies(self, cookies: list[dict[str, Any]]) -> None:
        """
        Set cookies in the current browser context.

        Args:
            cookies: List of cookie dictionaries. Each cookie must contain at minimum:
                    - 'name': Cookie name
                    - 'value': Cookie value
                    - 'url' OR 'domain': Cookie scope
                    Optional keys: 'path', 'expires', 'httpOnly', 'secure', 'sameSite'

        Raises:
            RuntimeError: If engine is not running, page is not available,
                         or Playwright fails to set cookies.
        """
        try:
            await self._require_page().context.add_cookies(cookies)
        except Exception as e:
            raise RuntimeError(f"Failed to set cookies: {e}") from e

    async def clear_cookies(self) -> None:
        """
        Clear all cookies from the current browser context.

        Raises:
            RuntimeError: If engine is not running or page is not available.
        """
        await self._require_page().context.clear_cookies()

    # -------------------------------------------------------------------------
    # Health Methods
    # -------------------------------------------------------------------------

    async def is_healthy(self) -> bool:
        """
        Check if the engine is running and healthy.

        Performs comprehensive health check with exception safety:
        - Page exists and is not closed
        - Browser exists and is connected

        Note: Playwright methods can throw exceptions even when checking state,
        so we wrap in try/except to ensure this method never raises.

        Returns:
            True if page exists, is not closed, and browser is connected; False otherwise.
        """
        if self._page is None or self._browser is None:
            return False

        try:
            # Check both browser connection AND page state
            # Both methods can throw if browser/page is in invalid state
            return self._browser.is_connected() and not self._page.is_closed()
        except Exception:
            # Playwright can throw even on state checks - treat as unhealthy
            return False

    # -------------------------------------------------------------------------
    # Public Page Access
    # -------------------------------------------------------------------------

    def _require_page(self) -> Page:
        return self.get_page()

    def get_page(self) -> Page:
        """
        Get the active Playwright Page instance.

        Returns:
            The active Page instance.

        Raises:
            RuntimeError: If engine is not running or page is not available.
        """
        if self._page is None:
            raise RuntimeError(
                "Engine not running. Call launch() or use async context manager."
            )
        return self._page

    async def _handle_response(self, response: Response) -> None:
        """
        Response event handler for HTTP error monitoring.

        Monitors all HTTP responses and triggers error handling for status codes
        configured in error_map.

        Args:
            response: Playwright Response object.
        """
        if response.status in self.error_map:
            await self.handle_error(response.status)