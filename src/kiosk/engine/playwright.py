from __future__ import annotations

import logging
from typing import Any, Literal

from playwright.async_api import (
    Browser,
    Page,
    Playwright,
    Response,
    async_playwright,
)
from pydantic import Field, PrivateAttr

from .base import Engine


logger = logging.getLogger(__name__)


class PlaywrightEngine(Engine):
    """Playwright-based browser automation engine."""

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
        default="playwright",
        description="The type of browser engine",
        min_length=1,
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
        """Launch the Playwright browser engine."""
        # Idempotent guard to prevent duplicate browser instances.
        if self._browser is not None:
            return

        try:
            self._playwright = await async_playwright().start()
            browser_launcher = getattr(self._playwright, self.browser_type)
            self._browser = await browser_launcher.launch(
                headless=self.headless,
                args=self.launch_args,
            )

            # Setting no_viewport=True preserves the browser window size from launch args.
            self._page = await self._browser.new_page(no_viewport=True)
            self._page.on("response", self._handle_response)

            # Chromium can fullscreen via CDP; other engines fall back to F11.
            if self.fullscreen and not self.headless:
                if self.browser_type == "chromium":
                    cdp = await self._page.context.new_cdp_session(self._page)
                    result = await cdp.send("Browser.getWindowForTarget")
                    await cdp.send("Browser.setWindowBounds", {
                        "windowId": result["windowId"],
                        "bounds": {"windowState": "fullscreen"},
                    })
                    await cdp.detach()
                else:
                    await self._page.keyboard.press("F11")

        except Exception as e:
            # Clean up partial state on failure.
            await self.close()
            raise RuntimeError(f"Failed to launch Playwright engine: {e}") from e

    async def close(self) -> None:
        """Close the Playwright browser engine."""
        if self._page is not None:
            try:
                await self._page.close()
            except Exception:
                logger.exception("Failed to close page during engine shutdown")
            finally:
                self._page = None

        if self._browser is not None:
            try:
                await self._browser.close()
            except Exception:
                logger.exception("Failed to close browser during engine shutdown")
            finally:
                self._browser = None

        if self._playwright is not None:
            try:
                await self._playwright.stop()
            except Exception:
                logger.exception("Failed to stop Playwright during engine shutdown")
            finally:
                self._playwright = None

    # -------------------------------------------------------------------------
    # Page State Methods
    # -------------------------------------------------------------------------

    async def get_current_url(self) -> str:
        """Return the current URL."""
        return self._require_page().url

    async def screenshot(self) -> bytes:
        """Capture a screenshot of the current page."""
        try:
            return await self._require_page().screenshot()
        except Exception as e:
            raise RuntimeError(f"Failed to capture screenshot: {e}") from e

    # -------------------------------------------------------------------------
    # Storage Methods
    # -------------------------------------------------------------------------

    async def get_cookies(self) -> list[dict[str, Any]]:
        """Return all cookies from the current browser context."""
        return await self._require_page().context.cookies()

    async def set_cookies(self, cookies: list[dict[str, Any]]) -> None:
        """Set cookies in the current browser context."""
        try:
            await self._require_page().context.add_cookies(cookies)
        except Exception as e:
            raise RuntimeError(f"Failed to set cookies: {e}") from e

    async def clear_cookies(self) -> None:
        """Clear all cookies from the current browser context."""
        await self._require_page().context.clear_cookies()

    # -------------------------------------------------------------------------
    # Health Methods
    # -------------------------------------------------------------------------

    async def is_healthy(self) -> bool:
        """Return whether the engine is healthy."""
        if self._page is None or self._browser is None:
            return False

        try:
            # Both state checks can raise if Playwright is partially torn down.
            return self._browser.is_connected() and not self._page.is_closed()
        except Exception:
            # Treat unexpected Playwright state errors as unhealthy.
            return False

    # -------------------------------------------------------------------------
    # Page Access
    # -------------------------------------------------------------------------

    def _require_page(self) -> Page:
        if self._page is None:
            raise RuntimeError(
                "Engine not running. Call launch() or use async context manager."
            )
        return self._page

    async def _handle_response(self, response: Response) -> None:
        """Handle main-frame HTTP responses that match configured error codes."""
        if response.request.resource_type != "document":
            return
        if self._page is not None and response.frame != self._page.main_frame:
            return
        if response.status in self.error_map and self.on_error:
            await self.on_error(response.status)
