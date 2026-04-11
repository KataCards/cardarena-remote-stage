from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field
from abc import ABC, abstractmethod
from typing import Literal
from ..engine.base import Engine

class Controls(BaseModel, ABC):
    """Abstract base class for browser control implementations."""

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
        """Navigate to a URL."""
        ...

    @abstractmethod
    async def reload(self) -> bool:
        """Reload the current page."""
        ...

    @abstractmethod
    async def go_back(self) -> bool:
        """Navigate back in browser history."""
        ...

    @abstractmethod
    async def go_forward(self) -> bool:
        """Navigate forward in browser history."""
        ...

    # -------------------------------------------------------------------------
    # Interaction Methods
    # -------------------------------------------------------------------------

    @abstractmethod
    async def click(self, x: int, y: int) -> bool:
        """Click at the given coordinates."""
        ...

    @abstractmethod
    async def type_text(self, text: str) -> bool:
        """Type text into the focused element."""
        ...

    @abstractmethod
    async def scroll(
        self,
        direction: Literal["up", "down", "left", "right"],
        amount: int,
    ) -> bool:
        """Scroll the page in the given direction."""
        ...

    @abstractmethod
    async def press_key(self, key: str) -> bool:
        """Press a keyboard key."""
        ...

    # -------------------------------------------------------------------------
    # Waiting Methods
    # -------------------------------------------------------------------------

    @abstractmethod
    async def wait_for_navigation(self) -> bool:
        """Wait for navigation to complete."""
        ...
