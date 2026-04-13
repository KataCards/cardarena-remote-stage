from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

from pydantic import Field

from .base import Kiosk
from ..controls.playwright import PlaywrightControls
from ..engine.playwright import PlaywrightEngine
from src.utils import get_logger


logger = get_logger(__name__)


class PlaywrightKiosk(Kiosk):
    """Playwright-based kiosk orchestration layer."""

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
        """Wire error callback to engine only when an error map is configured."""
        if self.engine.error_map:
            self.engine.on_error = self._on_error

    # -------------------------------------------------------------------------
    # Lifecycle Methods
    # -------------------------------------------------------------------------

    async def start(self) -> None:
        """Start the kiosk."""
        self.controls = PlaywrightControls(engine=self.engine)
        await self.engine.launch()
        await self._navigate_with_retry(self.default_page)
        await self._sync_current_url()
        self.is_running = True
        logger.info(
            "kiosk_started",
            kiosk_uuid=str(self.kiosk_id),
            kiosk_name=self.kiosk_name,
        )

    async def stop(self) -> None:
        """Stop the kiosk."""
        self.is_running = False
        self.current_url = ""
        self.controls = None
        try:
            await self.engine.close()
        finally:
            logger.info(
                "kiosk_stopped",
                kiosk_uuid=str(self.kiosk_id),
                kiosk_name=self.kiosk_name,
            )

    # -------------------------------------------------------------------------
    # Error Handling
    # -------------------------------------------------------------------------

    async def _on_error(self, error_code: int) -> None:
        """Navigate to the configured error page for a response code."""
        # Ignore early errors before controls are mounted.
        if self.controls is None:
            return

        path = await self.engine.handle_error(error_code)
        # Convert to absolute path and format as proper file:/// URL
        absolute_path = Path(path).resolve()
        file_url = absolute_path.as_uri()
        try:
            await self.controls.navigate(file_url)
        except Exception:
            logger.exception(
                "error_page_navigation_failed",
                error_code=error_code,
                file_url=file_url,
            )

    # -------------------------------------------------------------------------
    # Navigation with Retry
    # -------------------------------------------------------------------------

    async def _navigate_with_retry(self, url: str) -> None:
        """Navigate to a URL with exponential-backoff retries."""
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
        """Navigate to the default page."""
        try:
            await self._navigate_with_retry(self.default_page)
        except RuntimeError:
            logger.error("operation_failed", operation="go_home")
            return False
        return True
