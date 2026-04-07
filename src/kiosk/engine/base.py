from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from collections.abc import Callable
from abc import ABC, abstractmethod
from typing import Any, Awaitable
from pathlib import Path


class Engine(BaseModel, ABC):
    """Abstract base class for browser engine implementations."""

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=True,
        frozen=False,
        extra="forbid",
    )

    engine_type: str = Field(
        ...,
        description="The type of browser engine",
        min_length=1,
    )

    resources: dict[str, str] = Field(
        default_factory=dict,
        description="Mapping of resource names to local HTML file paths",
    )

    error_map: dict[int, str] = Field(
        default_factory=dict,
        description="Mapping of HTTP error codes to resource keys",
    )

    on_error: Callable[[int], Awaitable[None]] | None = Field(
        default=None,
        description="Callback function invoked when an error occurs",
    )

    fullscreen: bool = Field(
        default=False,
        description="Force the browser into fullscreen after launch. Each engine handles this differently.",
    )

    # -------------------------------------------------------------------------
    # Validators
    # -------------------------------------------------------------------------

    @field_validator("error_map")
    @classmethod
    def validate_error_codes(cls, v: dict[int, str]) -> dict[int, str]:
        """Validate that all error codes are valid HTTP status codes."""
        for code in v.keys():
            if not (100 <= code <= 599):
                raise ValueError(
                    f"Invalid HTTP status code: {code}. Must be between 100 and 599."
                )
        return v

    @field_validator("resources")
    @classmethod
    def validate_resource_paths(cls, v: dict[str, str]) -> dict[str, str]:
        """Validate that all resource file paths exist on disk."""
        for key, path in v.items():
            if not Path(path).exists():
                raise ValueError(
                    f"Resource '{key}' points to a file that does not exist: {path}"
                )
        return v

    @model_validator(mode="after")
    def validate_error_map_keys_exist_in_resources(self) -> "Engine":
        """Validate that all error-map keys exist in resources."""
        for code, resource_key in self.error_map.items():
            if resource_key not in self.resources:
                raise ValueError(
                    f"Error code {code} maps to resource key '{resource_key}' "
                    f"which does not exist in resources. "
                    f"Available resources: {sorted(self.resources.keys())}"
                )
        return self

    # -------------------------------------------------------------------------
    # Lifecycle Methods
    # -------------------------------------------------------------------------

    @abstractmethod
    async def launch(self) -> None:
        """Launch the browser engine."""
        ...

    @abstractmethod
    async def close(self) -> None:
        """Close the browser engine."""
        ...

    async def __aenter__(self) -> "Engine":
        """Launch the engine in an async context manager."""
        await self.launch()
        return self

    async def __aexit__(
        self,
        exc_type,
        exc_val,
        exc_tb,
    ) -> None:
        """Close the engine in an async context manager."""
        await self.close()

    # -------------------------------------------------------------------------
    # Page Access
    # -------------------------------------------------------------------------

    @abstractmethod
    def _require_page(self) -> Any:
        """Return the active page object."""
        ...

    # -------------------------------------------------------------------------
    # Page State Methods
    # -------------------------------------------------------------------------

    @abstractmethod
    async def get_current_url(self) -> str:
        """Return the current URL."""
        ...

    @abstractmethod
    async def screenshot(self) -> bytes:
        """Capture a screenshot of the current page."""
        ...

    # -------------------------------------------------------------------------
    # Storage Methods
    # -------------------------------------------------------------------------

    @abstractmethod
    async def get_cookies(self) -> list[dict[str, Any]]:
        """Return all cookies from the current browser context."""
        ...

    @abstractmethod
    async def set_cookies(self, cookies: list[dict[str, Any]]) -> None:
        """Set cookies in the current browser context."""
        ...

    @abstractmethod
    async def clear_cookies(self) -> None:
        """Clear all cookies from the current browser context."""
        ...

    # -------------------------------------------------------------------------
    # Health Methods
    # -------------------------------------------------------------------------

    @abstractmethod
    async def is_healthy(self) -> bool:
        """Return whether the engine is healthy."""
        ...

    # -------------------------------------------------------------------------
    # Error Handling
    # -------------------------------------------------------------------------

    async def handle_error(self, error_code: int) -> str:
        """Resolve the local HTML file path for an HTTP error code."""
        if error_code not in self.error_map:
            raise KeyError(
                f"Error code {error_code} not found in error_map. "
                f"Available error codes: {sorted(self.error_map.keys())}"
            )

        resource_key = self.error_map[error_code]

        if resource_key not in self.resources:
            raise ValueError(
                f"Resource key '{resource_key}' (for error code {error_code}) "
                f"not found in resources. Available resources: {sorted(self.resources.keys())}"
            )

        if self.on_error:
            await self.on_error(error_code)
        return self.resources[resource_key]
