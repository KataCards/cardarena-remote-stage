from __future__ import annotations

from abc import ABC, abstractmethod
from types import TracebackType
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ..controls.base import Controls
from ..engine.base import Engine
from src.utils import get_logger, validate_url


logger = get_logger(__name__)


class Kiosk(BaseModel, ABC):
    """Abstract base class for kiosk browser orchestration."""

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
    )

    is_running: bool = Field(
        default=False,
        description="Whether the kiosk is currently running",
    )

    current_url: str = Field(
        default="",
        description="The current URL shown by the kiosk",
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

    @field_validator("default_page")
    @classmethod
    def _validate_default_page(cls, v: str) -> str:
        return validate_url(v)

    # -------------------------------------------------------------------------
    # Internal Helpers
    # -------------------------------------------------------------------------

    def _require_controls(self) -> Controls:
        """Return the mounted controls instance."""
        if self.controls is None:
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
        """Start the kiosk."""
        ...

    @abstractmethod
    async def stop(self) -> None:
        """Stop the kiosk."""
        ...

    async def restart(self) -> None:
        """Restart the kiosk."""
        await self.stop()
        await self.start()

    async def __aenter__(self) -> "Kiosk":
        """Start the kiosk in an async context manager."""
        await self.start()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Stop the kiosk in an async context manager."""
        await self.stop()

    # -------------------------------------------------------------------------
    # Health Methods
    # -------------------------------------------------------------------------

    async def is_healthy(self) -> bool:
        """Return whether the kiosk is running and healthy."""
        return self.is_running and await self.engine.is_healthy()

    # -------------------------------------------------------------------------
    # Page Methods
    # -------------------------------------------------------------------------

    async def screenshot(self) -> bytes:
        """Capture a screenshot of the current page."""
        return await self.engine.screenshot()

    async def _sync_current_url(self) -> None:
        """Refresh current_url from the underlying engine if a page is available."""
        try:
            self.current_url = await self.engine.get_current_url()
        except RuntimeError:
            self.current_url = ""

    # -------------------------------------------------------------------------
    # Navigation Methods
    # -------------------------------------------------------------------------

    async def navigate(self, url: str) -> bool:
        """Navigate to a URL if it is allowed."""
        controls = self._require_controls()
        # This is the single whitelist enforcement point for kiosk navigation.
        if self.allowed_urls and url not in self.allowed_urls:
            logger.warning(
                "navigation_blocked",
                url=url,
                kiosk_uuid=str(self.kiosk_id),
                kiosk_name=self.kiosk_name,
            )
            return False
        if not await controls.navigate(url):
            logger.error("navigation_failed", url=url)
            return False
        await self._sync_current_url()
        return True

    async def reload(self) -> bool:
        """Reload the current page."""
        if not await self._require_controls().reload():
            logger.error("operation_failed", operation="reload")
            return False
        await self._sync_current_url()
        return True

    async def go_back(self) -> bool:
        """Navigate back in browser history."""
        if not await self._require_controls().go_back():
            logger.error("operation_failed", operation="go_back")
            return False
        await self._sync_current_url()
        return True

    async def go_forward(self) -> bool:
        """Navigate forward in browser history."""
        if not await self._require_controls().go_forward():
            logger.error("operation_failed", operation="go_forward")
            return False
        await self._sync_current_url()
        return True

    @abstractmethod
    async def go_home(self) -> bool:
        """Navigate to the default page."""
        ...

    # -------------------------------------------------------------------------
    # Interaction Methods
    # -------------------------------------------------------------------------

    async def click(self, x: int, y: int) -> bool:
        """Click at the given coordinates."""
        if not await self._require_controls().click(x, y):
            logger.error("interaction_failed", operation="click")
            return False
        return True

    async def type_text(self, text: str) -> bool:
        """Type text into the focused element."""
        if not await self._require_controls().type_text(text):
            logger.error("interaction_failed", operation="type_text")
            return False
        return True

    async def scroll(
        self,
        direction: Literal["up", "down", "left", "right"],
        amount: int,
    ) -> bool:
        """Scroll the page in the given direction."""
        if not await self._require_controls().scroll(direction, amount):
            logger.error("interaction_failed", operation="scroll")
            return False
        return True

    async def press_key(self, key: str) -> bool:
        """Press a keyboard key."""
        if not await self._require_controls().press_key(key):
            logger.error("interaction_failed", operation="press_key")
            return False
        return True

    # -------------------------------------------------------------------------
    # Waiting Methods
    # -------------------------------------------------------------------------

    async def wait_for_navigation(self) -> bool:
        """Wait for navigation to complete."""
        return await self._require_controls().wait_for_navigation()
