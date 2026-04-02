from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from collections.abc import Callable
from abc import ABC, abstractmethod
from typing import Any, Awaitable
from pathlib import Path


class Engine(BaseModel, ABC):
    """
    Abstract base class for browser engine implementations.

    This class combines Pydantic v2's data validation capabilities with an abstract
    interface for browser automation engines. It provides error handling, resource
    management, and lifecycle management through async context managers.

    Attributes:
        engine_type: The type/name of the browser engine (e.g., 'chromium', 'firefox').
        default_page: The default URL to navigate to when launching the engine.
        resources: Mapping of resource names to local HTML file paths.
        error_map: Mapping of HTTP error codes to resource keys for error handling.
        on_error: Callback function invoked when an error occurs.

    Example:
        ```python
        class ChromiumEngine(Engine):
            async def launch(self):
                # Implementation
                pass

            async def close(self):
                # Implementation
                pass

            # ... implement other abstract methods
        ```
    """

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

    # -------------------------------------------------------------------------
    # Validators
    # -------------------------------------------------------------------------

    @field_validator("error_map")
    @classmethod
    def validate_error_codes(cls, v: dict[int, str]) -> dict[int, str]:
        """
        Validate that error codes are valid HTTP status codes.

        Args:
            v: Dictionary mapping error codes to resource keys.

        Returns:
            The validated error_map dictionary.

        Raises:
            ValueError: If any error code is not a valid HTTP status code (100-599).
        """
        for code in v.keys():
            if not (100 <= code <= 599):
                raise ValueError(
                    f"Invalid HTTP status code: {code}. Must be between 100 and 599."
                )
        return v

    @field_validator("resources")
    @classmethod
    def validate_resource_paths(cls, v: dict[str, str]) -> dict[str, str]:
        """
        Validate that all resource file paths exist on disk.

        Args:
            v: Dictionary mapping resource keys to file paths.

        Returns:
            The validated resources dictionary.

        Raises:
            ValueError: If any file path does not exist.
        """
        for key, path in v.items():
            if not Path(path).exists():
                raise ValueError(
                    f"Resource '{key}' points to a file that does not exist: {path}"
                )
        return v

    @model_validator(mode="after")
    def validate_error_map_keys_exist_in_resources(self) -> "Engine":
        """
        Validate that all resource keys referenced in error_map exist in resources.

        Raises:
            ValueError: If any error_map value is not a key in resources.
        """
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
        """
        Launch the browser engine and initialize resources.

        This method should start the browser process, create necessary contexts,
        and prepare the engine for navigation and interaction.

        Raises:
            RuntimeError: If the engine fails to launch.
        """
        ...

    @abstractmethod
    async def close(self) -> None:
        """
        Close the browser engine and clean up resources.

        This method should gracefully shut down the browser process, close all
        pages/contexts, and release any held resources.

        Raises:
            RuntimeError: If the engine fails to close properly.
        """
        ...

    async def __aenter__(self) -> "Engine":
        """
        Async context manager entry point.

        Launches the engine when entering the context.

        Returns:
            The Engine instance.

        Raises:
            RuntimeError: If the engine fails to launch.
        """
        await self.launch()
        return self

    async def __aexit__(
        self,
    ) -> None:
        """
        Async context manager exit point.

        Closes the engine when exiting the context, regardless of whether
        an exception occurred.

        """
        await self.close()

    # -------------------------------------------------------------------------
    # Page Access
    # -------------------------------------------------------------------------

    @abstractmethod
    def _require_page(self) -> Any:
        """
        Return the active page object, raising if the engine is not running.

        This is the canonical guard used by all page-state and interaction
        methods. Implementations must raise RuntimeError when no page is
        available (e.g. before launch() has been called).

        Returns:
            The engine-specific page object.

        Raises:
            RuntimeError: If no page is active or the engine is not running.
        """
        ...

    # -------------------------------------------------------------------------
    # Page State Methods
    # -------------------------------------------------------------------------

    @abstractmethod
    async def get_current_url(self) -> str:
        """
        Get the current URL of the active page.

        Returns:
            The current URL as a string.

        Raises:
            RuntimeError: If no page is active or the engine is not running.
        """
        ...

    @abstractmethod
    async def screenshot(self) -> bytes:
        """
        Capture a screenshot of the current page.

        Returns:
            Screenshot as raw bytes.

        Raises:
            RuntimeError: If no page is active or screenshot capture fails.
        """
        ...

    # -------------------------------------------------------------------------
    # Storage Methods
    # -------------------------------------------------------------------------

    @abstractmethod
    async def get_cookies(self) -> list[dict[str, Any]]:
        """
        Retrieve all cookies from the current browser context.

        Returns:
            List of cookie dictionaries containing name, value, domain, path, etc.

        Raises:
            RuntimeError: If the engine is not running.
        """
        ...

    @abstractmethod
    async def set_cookies(self, cookies: list[dict[str, Any]]) -> None:
        """
        Set cookies in the current browser context.

        Args:
            cookies: List of cookie dictionaries to set. Each cookie should contain
                    at minimum 'name', 'value', and 'domain' keys.

        Raises:
            ValueError: If cookie format is invalid.
            RuntimeError: If the engine is not running.
        """
        ...

    @abstractmethod
    async def clear_cookies(self) -> None:
        """
        Clear all cookies from the current browser context.

        Raises:
            RuntimeError: If the engine is not running.
        """
        ...

    # -------------------------------------------------------------------------
    # Health Methods
    # -------------------------------------------------------------------------

    @abstractmethod
    async def is_healthy(self) -> bool:
        """
        Check if the engine is running and healthy.

        Returns:
            True if the engine is running and responsive, False otherwise.
        """
        ...

    # -------------------------------------------------------------------------
    # Error Handling
    # -------------------------------------------------------------------------

    async def handle_error(self, error_code: int) -> str:
        """
        Resolve the local HTML file path for a given HTTP error code and invoke
        the on_error callback.

        Args:
            error_code: The HTTP error code to handle (e.g., 404, 500).

        Returns:
            The local file path to the error page HTML resource.

        Raises:
            KeyError: If the error code is not found in error_map.
            ValueError: If the resolved resource key is not found in resources.

        Example:
    ```python
            engine = MyEngine(
                error_map={404: "not_found", 500: "server_error"},
                resources={"not_found": "/path/to/404.html", "server_error": "/path/to/500.html"},
                # ... other required fields
            )
            path = await engine.handle_error(404)  # Returns "/path/to/404.html"
    ```
        """
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