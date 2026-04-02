from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field
from ..controls.base import Controls
from abc import ABC, abstractmethod
from ..engine.base import Engine
from typing import Any, Literal
from uuid import UUID, uuid4


class Kiosk(BaseModel, ABC):
    """
    Abstract base class for kiosk browser orchestration.

    This class orchestrates a browser engine and controls, providing URL whitelisting,
    lifecycle management, and a unified interface for browser interaction in kiosk mode.

    Attributes:
        engine: The browser engine powering the kiosk.
        controls: Browser controls for interaction (None until start() is called).
        default_page: URL to navigate to on start.
        is_running: Whether the kiosk is currently running.
        kiosk_id: Unique identifier for this kiosk instance (auto-generated).
        kiosk_name: Human-readable name for logging and dashboards.
        allowed_urls: URL whitelist enforced before navigation.

    Example:
        ```python
        class MyKiosk(Kiosk):
            async def start(self):
                await self.engine.launch()
                self.controls = MyControls(engine=self.engine)
                self.is_running = True
                await self.controls.navigate(self.default_page)

            async def stop(self):
                self.is_running = False
                await self.engine.close()
                self.controls = None
        ```
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=True,
        frozen=False,
        extra="forbid",
    )

    engine: Engine = Field(
        ...,
        description="The browser engine powering the kiosk",
    )

    controls: Controls | None = Field(
        default=None,
        description="Browser controls for interaction (mounted at start)",
    )

    default_page: str = Field(
        ...,
        description="URL to navigate to on start",
        pattern=r"^(https?://([a-zA-Z0-9.-]+|\[[0-9a-fA-F:]+\])(:[0-9]+)?(/[^\s]*)?|file:///[^\s]*)$",
    )

    is_running: bool = Field(
        default=False,
        description="Whether the kiosk is currently running",
    )

    kiosk_id: UUID = Field(
        default_factory=uuid4,
        description="Unique identifier for this kiosk instance",
    )

    kiosk_name: str = Field(
        ...,
        description="Human-readable name for logging and dashboards",
        min_length=1,
    )

    allowed_urls: list[str] = Field(
        default_factory=list,
        description="URL whitelist enforced before navigation",
    )

    # -------------------------------------------------------------------------
    # Internal Helpers
    # -------------------------------------------------------------------------

    def _require_controls(self) -> Controls:
        """
        Ensure controls are mounted before performing any interaction.

        Returns:
            The mounted Controls instance.

        Raises:
            RuntimeError: If controls are not mounted.
        """
        if not self.controls:
            raise RuntimeError(
                f"Kiosk '{self.kiosk_name}' ({self.kiosk_id}): "
                "Controls not mounted. Call start() first."
            )
        return self.controls

    # -------------------------------------------------------------------------
    # Lifecycle Methods
    # -------------------------------------------------------------------------

    @abstractmethod
    async def start(self) -> None:
        """
        Start the kiosk by launching the engine and mounting controls.

        This method should:
        - Launch the browser engine
        - Create and mount the controls instance
        - Set is_running to True
        - Navigate to default_page

        Raises:
            RuntimeError: If the kiosk fails to start.
        """
        ...

    @abstractmethod
    async def stop(self) -> None:
        """
        Stop the kiosk by closing the engine and unmounting controls.

        This method should:
        - Set is_running to False
        - Close the browser engine
        - Set controls to None

        Raises:
            RuntimeError: If the kiosk fails to stop properly.
        """
        ...

    async def restart(self) -> None:
        """
        Restart the kiosk by stopping and then starting it.

        Raises:
            RuntimeError: If restart fails.
        """
        await self.stop()
        await self.start()

    async def __aenter__(self) -> "Kiosk":
        """
        Async context manager entry point.

        Starts the kiosk when entering the context.

        Returns:
            The Kiosk instance.

        Raises:
            RuntimeError: If the kiosk fails to start.
        """
        await self.start()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        """
        Async context manager exit point.

        Stops the kiosk when exiting the context, regardless of whether
        an exception occurred.

        Args:
            exc_type: The type of exception that occurred, if any.
            exc_val: The exception instance that occurred, if any.
            exc_tb: The traceback object, if any.
        """
        await self.stop()

    # -------------------------------------------------------------------------
    # Health Methods
    # -------------------------------------------------------------------------

    async def is_healthy(self) -> bool:
        """
        Check if the kiosk is running and the engine is healthy.

        Returns:
            True if the kiosk is running and engine is healthy, False otherwise.
        """
        return self.is_running and await self.engine.is_healthy()

    # -------------------------------------------------------------------------
    # Status Methods
    # -------------------------------------------------------------------------

    async def get_status(self) -> dict[str, Any]:
        """
        Get the current status of the kiosk.

        Returns:
            Dictionary containing:
            - is_running: bool
            - kiosk_id: str (UUID as string)
            - kiosk_name: str
            - engine_type: str
            - controls_type: str | None
        """
        return {
            "is_running": self.is_running,
            "kiosk_id": str(self.kiosk_id),
            "kiosk_name": self.kiosk_name,
            "engine_type": self.engine.engine_type,
            "controls_type": type(self.controls).__name__ if self.controls else None,
        }

    # -------------------------------------------------------------------------
    # Page Methods
    # -------------------------------------------------------------------------

    async def screenshot(self) -> bytes:
        """
        Capture a screenshot of the current page.

        Delegates to engine.screenshot().

        Returns:
            Screenshot as raw bytes.

        Raises:
            RuntimeError: If the kiosk is not running or screenshot fails.
        """
        return await self.engine.screenshot()

    # -------------------------------------------------------------------------
    # Navigation Methods
    # -------------------------------------------------------------------------

    async def navigate(self, url: str) -> bool:
        """
        Navigate to the specified URL after validating against allowed_urls.

        This is the sole whitelist enforcement point. If the URL is not in
        allowed_urls, returns False without raising.

        Args:
            url: The URL to navigate to.

        Returns:
            True if navigation succeeded, False if URL not whitelisted or navigation failed.

        Raises:
            RuntimeError: If controls are not mounted or a hard failure occurs.
        """
        controls = self._require_controls()
        if self.allowed_urls and url not in self.allowed_urls:
            return False
        return await controls.navigate(url)

    async def reload(self) -> bool:
        """
        Reload the current page.

        Returns:
            True if reload succeeded, False if reload failed softly.

        Raises:
            RuntimeError: If controls are not mounted or a hard failure occurs.
        """
        return await self._require_controls().reload()

    async def go_back(self) -> bool:
        """
        Navigate back in the browser history.

        Returns:
            True if navigation succeeded, False if no history available.

        Raises:
            RuntimeError: If controls are not mounted or a hard failure occurs.
        """
        return await self._require_controls().go_back()

    async def go_forward(self) -> bool:
        """
        Navigate forward in the browser history.

        Returns:
            True if navigation succeeded, False if no forward history exists.

        Raises:
            RuntimeError: If controls are not mounted or a hard failure occurs.
        """
        return await self._require_controls().go_forward()

    # -------------------------------------------------------------------------
    # Interaction Methods
    # -------------------------------------------------------------------------

    async def click(self, x: int, y: int) -> bool:
        """
        Click at the specified coordinates.

        Args:
            x: The x-coordinate to click.
            y: The y-coordinate to click.

        Returns:
            True if click succeeded, False if click failed softly.

        Raises:
            ValueError: If coordinates are invalid.
            RuntimeError: If controls are not mounted or a hard failure occurs.
        """
        return await self._require_controls().click(x, y)

    async def type_text(self, text: str) -> bool:
        """
        Type the specified text into the currently focused element.

        Args:
            text: The text to type.

        Returns:
            True if typing succeeded, False if nothing is focused.

        Raises:
            RuntimeError: If controls are not mounted or a hard failure occurs.
        """
        return await self._require_controls().type_text(text)

    async def scroll(
        self,
        direction: Literal["up", "down", "left", "right"],
        amount: int,
    ) -> bool:
        """
        Scroll the page in the specified direction by the given amount.

        Args:
            direction: The direction to scroll.
            amount: The amount to scroll in pixels.

        Returns:
            True if scroll succeeded, False if page cannot scroll.

        Raises:
            ValueError: If amount is invalid.
            RuntimeError: If controls are not mounted or a hard failure occurs.
        """
        return await self._require_controls().scroll(direction, amount)

    async def press_key(self, key: str) -> bool:
        """
        Press the specified keyboard key.

        Args:
            key: The key to press (e.g., 'Enter', 'Escape', 'ArrowDown').

        Returns:
            True if key press succeeded, False if key could not be sent.

        Raises:
            ValueError: If key is invalid.
            RuntimeError: If controls are not mounted or a hard failure occurs.
        """
        return await self._require_controls().press_key(key)

    # -------------------------------------------------------------------------
    # Waiting Methods
    # -------------------------------------------------------------------------

    async def wait_for_navigation(self) -> bool:
        """
        Wait for a navigation event to complete.

        Returns:
            True if navigation completed, False if timeout reached.

        Raises:
            RuntimeError: If controls are not mounted or a hard failure occurs.
        """
        return await self._require_controls().wait_for_navigation()