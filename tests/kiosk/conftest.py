"""Shared fixtures for the kiosk test suite."""
from __future__ import annotations

from pathlib import Path
from typing import Any, AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.kiosk.controls.base import Controls
from src.kiosk.controls.playwright import PlaywrightControls
from src.kiosk.engine.base import Engine
from src.kiosk.engine.playwright import PlaywrightEngine
from src.kiosk.kiosk.base import Kiosk
from src.kiosk.kiosk.playwright import PlaywrightKiosk


# ---------------------------------------------------------------------------
# Concrete stub classes (module-level so tests can reference them as types)
# ---------------------------------------------------------------------------

class ConcreteEngine(Engine):
    """Minimal Engine subclass for testing base-class logic."""

    def _require_page(self) -> None: return None  # no-op stub for tests
    async def launch(self) -> None: ...
    async def close(self) -> None: ...
    async def get_current_url(self) -> str: return ""
    async def screenshot(self) -> bytes: return b""
    async def get_cookies(self) -> list[dict[str, Any]]: return []
    async def set_cookies(self, cookies: list[dict[str, Any]]) -> None: ...
    async def clear_cookies(self) -> None: ...
    async def is_healthy(self) -> bool: return True


class ConcreteControls(Controls):
    """Minimal Controls subclass that delegates scroll validation to super()."""

    async def navigate(self, url: str) -> bool: return True
    async def reload(self) -> bool: return True
    async def go_back(self) -> bool: return True
    async def go_forward(self) -> bool: return True
    async def go_home(self) -> bool: return True
    async def click(self, x: int, y: int) -> bool: return True
    async def type_text(self, text: str) -> bool: return True

    async def scroll(self, direction: Any, amount: int) -> bool:
        await super().scroll(direction, amount)
        return True

    async def press_key(self, key: str) -> bool: return True
    async def wait_for_navigation(self) -> bool: return True


class ConcretePlaywrightControls(PlaywrightControls):
    """
    Concrete PlaywrightControls with a go_home stub.

    PlaywrightControls does not implement go_home (home navigation is managed
    at the Kiosk layer), so it remains abstract. This subclass adds a minimal
    stub so the class can be instantiated in tests and in PlaywrightKiosk.start().
    """

    async def go_home(self) -> bool:
        return False


class ConcreteKiosk(Kiosk):
    """Minimal Kiosk subclass for testing base-class logic."""

    async def start(self) -> None:
        self.is_running = True

    async def stop(self) -> None:
        self.is_running = False
        self.controls = None


class ConcretePlaywrightKiosk(PlaywrightKiosk):
    """
    PlaywrightKiosk that instantiates ConcretePlaywrightControls instead of the
    abstract PlaywrightControls.
    """

    async def start(self) -> None:
        self.controls = ConcretePlaywrightControls(engine=self.engine)
        await self.engine.launch()
        await self._navigate_with_retry(self.default_page)
        self.is_running = True


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def tmp_html(tmp_path: Path) -> Path:
    """Create a minimal HTML file on disk and return its path."""
    f = tmp_path / "error.html"
    f.write_text("<html><body>Error</body></html>")
    return f


@pytest.fixture
def engine_with_resources(tmp_html: Path) -> ConcreteEngine:
    """ConcreteEngine with valid resources and error_map."""
    return ConcreteEngine(
        engine_type="test",
        resources={"not_found": str(tmp_html)},
        error_map={404: "not_found"},
    )


@pytest.fixture
def mock_pw_engine(tmp_html: Path) -> PlaywrightEngine:
    """
    PlaywrightEngine whose private runtime attrs are replaced with mocks so no
    real browser is required.
    """
    engine = PlaywrightEngine(
        browser_type="chromium",
        resources={"not_found": str(tmp_html)},
        error_map={404: "not_found"},
    )

    mock_page = MagicMock()
    mock_page.url = "https://example.com"
    mock_page.is_closed.return_value = False
    mock_page.goto = AsyncMock(return_value=None)
    mock_page.reload = AsyncMock(return_value=None)
    mock_page.go_back = AsyncMock(return_value=None)
    mock_page.go_forward = AsyncMock(return_value=None)
    mock_page.screenshot = AsyncMock(return_value=b"png_bytes")
    mock_page.keyboard = MagicMock()
    mock_page.keyboard.type = AsyncMock(return_value=None)
    mock_page.keyboard.press = AsyncMock(return_value=None)
    mock_page.mouse = MagicMock()
    mock_page.mouse.click = AsyncMock(return_value=None)
    mock_page.mouse.wheel = AsyncMock(return_value=None)
    mock_page.wait_for_load_state = AsyncMock(return_value=None)
    mock_page.context = MagicMock()
    mock_page.context.cookies = AsyncMock(return_value=[])
    mock_page.context.add_cookies = AsyncMock(return_value=None)
    mock_page.context.clear_cookies = AsyncMock(return_value=None)

    mock_browser = MagicMock()
    mock_browser.is_connected.return_value = True

    engine._page = mock_page
    engine._browser = mock_browser
    engine._playwright = MagicMock()
    return engine


@pytest.fixture
def mock_pw_controls(mock_pw_engine: PlaywrightEngine) -> ConcretePlaywrightControls:
    """ConcretePlaywrightControls backed by mock_pw_engine."""
    return ConcretePlaywrightControls(engine=mock_pw_engine)


@pytest.fixture
async def running_kiosk(tmp_path: Path) -> AsyncGenerator[ConcretePlaywrightKiosk, None]:
    """
    A fully started ConcretePlaywrightKiosk using a real headless Chromium browser.
    Marked e2e — skip unless running with -m e2e.
    """
    html_file = tmp_path / "404.html"
    html_file.write_text("<html><body>Not Found</body></html>")

    engine = PlaywrightEngine(
        browser_type="chromium",
        headless=True,
        resources={"not_found": str(html_file)},
        error_map={404: "not_found"},
    )
    kiosk = ConcretePlaywrightKiosk(
        engine=engine,
        default_page="https://example.com",
        kiosk_name="test-kiosk",
    )
    async with kiosk:
        yield kiosk
