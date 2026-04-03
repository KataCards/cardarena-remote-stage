from pydantic import BaseModel, ConfigDict, Field
from abc import ABC, abstractmethod
from typing import Literal
from ..engine.base import Engine

class Controls(BaseModel, ABC):
    """
    Abstract base class for browser control implementations.

    This class defines the interface for browser interaction operations including
    navigation, user input simulation, and waiting for page state changes.

    Attributes:
        engine: The browser engine instance to control.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=True,
        frozen=False,
        extra="forbid",
    )

    control_type: str = Field(
        ...,
        description="The type of browser controls",
        min_length=1,
    )

    engine: Engine = Field(
        ...,
        description="The browser engine instance this controls implementation operates on",
    )

    # -------------------------------------------------------------------------
    # Navigation Methods
    # -------------------------------------------------------------------------

    @abstractmethod
    async def navigate(self, url: str) -> bool:
        """
        Navigate to the specified URL.

        Args:
            url: The URL to navigate to.

        Returns:
            True if navigation succeeded, False if navigation failed softly (e.g., timeout).

        Raises:
            ValueError: If the URL is invalid.
            RuntimeError: If a hard failure occurs (e.g., engine not running, browser crashed).
        """
        ...

    @abstractmethod
    async def reload(self) -> bool:
        """
        Reload the current page.

        Returns:
            True if reload succeeded, False if reload times out.

        Raises:
            RuntimeError: If a hard failure occurs (e.g., no page is active, engine not running).
        """
        ...

    @abstractmethod
    async def go_back(self) -> bool:
        """
        Navigate back in the browser history.

        Returns:
            True if navigation succeeded, False if no history is available.

        Raises:
            RuntimeError: If a hard failure occurs (e.g., engine not running).
        """
        ...

    @abstractmethod
    async def go_forward(self) -> bool:
        """
        Navigate forward in the browser history.

        Returns:
            True if navigation succeeded, False if no forward history exists.

        Raises:
            RuntimeError: If a hard failure occurs (e.g., engine not running).
        """
        ...

    # -------------------------------------------------------------------------
    # Interaction Methods
    # -------------------------------------------------------------------------

    @abstractmethod
    async def click(self, x: int, y: int) -> bool:
        """
        Click at the specified coordinates.

        Args:
            x: The x-coordinate to click.
            y: The y-coordinate to click.

        Returns:
            True if click succeeded, False if click could not be performed (e.g., element not ready).

        Raises:
            ValueError: If coordinates are invalid.
            RuntimeError: If a hard failure occurs (e.g., engine not running).
        """
        ...

    @abstractmethod
    async def type_text(self, text: str) -> bool:
        """
        Type the specified text into the currently focused element.

        Args:
            text: The text to type.

        Returns:
            True if typing succeeded, False if nothing is focused.

        Raises:
            RuntimeError: If a hard failure occurs (e.g., engine not running).
        """
        ...

    @abstractmethod
    async def scroll(
        self,
        direction: Literal["up", "down", "left", "right"],
        amount: int,
    ) -> bool:
        """
        Scroll the page in the specified direction by the given amount.

        The default direction literals are up, down, left, right. Implementations
        may extend or replace this with their own direction scheme if needed.

        Args:
            direction: The direction to scroll.
            amount: The amount to scroll in pixels. Must be greater than 0.

        Returns:
            True if scroll succeeded, False if page cannot scroll in that direction.

        Raises:
            ValueError: If amount is negative or zero.
            RuntimeError: If a hard failure occurs (e.g., engine not running).
        """
        if amount <= 0:
            raise ValueError(f"Scroll amount must be greater than 0, got {amount}")
        ...

    @abstractmethod
    async def press_key(self, key: str) -> bool:
        """
        Press the specified keyboard key.

        Args:
            key: The key to press (e.g., 'Enter', 'Escape', 'ArrowDown').

        Returns:
            True if key press succeeded, False if key could not be sent.

        Raises:
            ValueError: If key is invalid.
            RuntimeError: If a hard failure occurs (e.g., engine not running).
        """
        ...

    # -------------------------------------------------------------------------
    # Waiting Methods
    # -------------------------------------------------------------------------

    @abstractmethod
    async def wait_for_navigation(self) -> bool:
        """
        Wait for a navigation event to complete.

        Returns:
            True if navigation completed, False if timeout reached.

        Raises:
            RuntimeError: If a hard failure occurs (e.g., engine not running).
        """
        ...