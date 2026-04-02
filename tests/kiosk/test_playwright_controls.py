"""Unit tests for PlaywrightControls."""
from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.kiosk.engine.playwright import PlaywrightEngine
from src.kiosk.utils.decorators.control_action import control_action
from src.kiosk.controls.playwright import PlaywrightControls


# ---------------------------------------------------------------------------
# Validation — scroll
# ---------------------------------------------------------------------------

async def test_scroll_zero_raises(mock_pw_controls: PlaywrightControls) -> None:
    with pytest.raises(ValueError, match="greater than 0"):
        await mock_pw_controls.scroll("down", 0)


async def test_scroll_negative_raises(mock_pw_controls: PlaywrightControls) -> None:
    with pytest.raises(ValueError, match="greater than 0"):
        await mock_pw_controls.scroll("up", -5)


# ---------------------------------------------------------------------------
# Validation — click
# ---------------------------------------------------------------------------

async def test_click_negative_x_raises(mock_pw_controls: PlaywrightControls) -> None:
    with pytest.raises(ValueError, match="non-negative"):
        await mock_pw_controls.click(-1, 0)


async def test_click_negative_y_raises(mock_pw_controls: PlaywrightControls) -> None:
    with pytest.raises(ValueError, match="non-negative"):
        await mock_pw_controls.click(0, -1)


# ---------------------------------------------------------------------------
# Validation — navigate
# ---------------------------------------------------------------------------

async def test_navigate_empty_string_raises(mock_pw_controls: PlaywrightControls) -> None:
    with pytest.raises(ValueError, match="Invalid URL"):
        await mock_pw_controls.navigate("")


async def test_navigate_no_protocol_raises(mock_pw_controls: PlaywrightControls) -> None:
    with pytest.raises(ValueError, match="Malformed URL"):
        await mock_pw_controls.navigate("example.com")


async def test_navigate_ftp_raises(mock_pw_controls: PlaywrightControls) -> None:
    with pytest.raises(ValueError, match="Malformed URL"):
        await mock_pw_controls.navigate("ftp://example.com")


# ---------------------------------------------------------------------------
# Dispatch — navigate
# ---------------------------------------------------------------------------

async def test_navigate_https_calls_goto(mock_pw_controls: PlaywrightControls) -> None:
    result = await mock_pw_controls.navigate("https://example.com")
    assert result is True
    mock_pw_controls.engine.get_page().goto.assert_awaited_once_with("https://example.com")


async def test_navigate_file_url_calls_goto(mock_pw_controls: PlaywrightControls, tmp_html) -> None:
    url = f"file://{tmp_html}"
    result = await mock_pw_controls.navigate(url)
    assert result is True
    mock_pw_controls.engine.get_page().goto.assert_awaited_once_with(url)




# ---------------------------------------------------------------------------
# Dispatch — scroll
# ---------------------------------------------------------------------------

async def test_scroll_down_dispatches_wheel(mock_pw_controls: PlaywrightControls) -> None:
    await mock_pw_controls.scroll("down", 200)
    mock_pw_controls.engine.get_page().mouse.wheel.assert_awaited_once_with(0, 200)


async def test_scroll_left_dispatches_wheel(mock_pw_controls: PlaywrightControls) -> None:
    await mock_pw_controls.scroll("left", 100)
    mock_pw_controls.engine.get_page().mouse.wheel.assert_awaited_once_with(-100, 0)


# ---------------------------------------------------------------------------
# control_action decorator behaviour
# ---------------------------------------------------------------------------

async def test_soft_exception_returns_false(mock_pw_engine: PlaywrightEngine) -> None:
    """Unexpected exceptions from a control method must be swallowed → False."""

    class BrokenControls(PlaywrightControls):
        @control_action
        async def navigate(self, url: str) -> bool:  # type: ignore[override]
            raise ConnectionError("network gone")

    controls = BrokenControls(engine=mock_pw_engine)
    result = await controls.navigate("http://example.com")
    assert result is False


async def test_value_error_propagates(mock_pw_controls: PlaywrightControls) -> None:
    with pytest.raises(ValueError):
        await mock_pw_controls.navigate("")


async def test_runtime_error_propagates(tmp_html) -> None:
    """get_page() raises RuntimeError when engine has no page (before launch)."""
    engine = PlaywrightEngine(
        browser_type="chromium",
        resources={"not_found": str(tmp_html)},
        error_map={404: "not_found"},
    )
    controls = PlaywrightControls(engine=engine)
    with pytest.raises(RuntimeError, match="not running"):
        await controls.navigate(f"file://{tmp_html}")
