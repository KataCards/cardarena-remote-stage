"""Unit tests for PlaywrightControls."""
from __future__ import annotations

import logging
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
    mock_pw_controls.engine._require_page().goto.assert_awaited_once_with("https://example.com")


async def test_navigate_file_url_calls_goto(mock_pw_controls: PlaywrightControls, tmp_html) -> None:
    url = f"file://{tmp_html}"
    result = await mock_pw_controls.navigate(url)
    assert result is True
    mock_pw_controls.engine._require_page().goto.assert_awaited_once_with(url)




# ---------------------------------------------------------------------------
# Dispatch — scroll
# ---------------------------------------------------------------------------

async def test_scroll_down_dispatches_wheel(mock_pw_controls: PlaywrightControls) -> None:
    await mock_pw_controls.scroll("down", 200)
    mock_pw_controls.engine._require_page().mouse.wheel.assert_awaited_once_with(0, 200)


async def test_scroll_left_dispatches_wheel(mock_pw_controls: PlaywrightControls) -> None:
    await mock_pw_controls.scroll("left", 100)
    mock_pw_controls.engine._require_page().mouse.wheel.assert_awaited_once_with(-100, 0)


# ---------------------------------------------------------------------------
# control_action decorator behaviour
# ---------------------------------------------------------------------------

async def test_soft_exception_returns_false_and_logs(
    mock_pw_engine: PlaywrightEngine, caplog: pytest.LogCaptureFixture
) -> None:
    """Unexpected exceptions from a control method must be swallowed → False."""

    class BrokenControls(PlaywrightControls):
        @control_action
        async def navigate(self, url: str) -> bool:  # type: ignore[override]
            raise ConnectionError("network gone")

    controls = BrokenControls(engine=mock_pw_engine)
    with caplog.at_level(logging.ERROR):
        result = await controls.navigate("http://example.com")

    assert result is False
    assert "Control action 'navigate' failed" in caplog.text


async def test_value_error_propagates(mock_pw_controls: PlaywrightControls) -> None:
    with pytest.raises(ValueError):
        await mock_pw_controls.navigate("")


async def test_runtime_error_propagates(tmp_html) -> None:
    """_require_page() raises RuntimeError when engine has no page (before launch)."""
    engine = PlaywrightEngine(
        browser_type="chromium",
        resources={"not_found": str(tmp_html)},
        error_map={404: "not_found"},
    )
    controls = PlaywrightControls(engine=engine)
    with pytest.raises(RuntimeError, match="not running"):
        await controls.navigate(f"file://{tmp_html}")


# ---------------------------------------------------------------------------
# Headless integration tests — real Chromium, no display required
# ---------------------------------------------------------------------------

@pytest.mark.headless
class TestPlaywrightControlsHeadless:
    """Integration tests: each control method exercised against real headless Chromium."""

    async def test_navigate_changes_url(
        self, headless_controls: PlaywrightControls, local_http_server: str
    ) -> None:
        url = f"{local_http_server}/index.html"
        result = await headless_controls.navigate(url)
        assert result is True
        current = await headless_controls.engine.get_current_url()
        assert current == url

    async def test_reload_returns_true(
        self, headless_controls: PlaywrightControls, local_http_server: str
    ) -> None:
        await headless_controls.navigate(f"{local_http_server}/index.html")
        assert await headless_controls.reload() is True

    async def test_go_back_after_two_navigations(
        self, headless_controls: PlaywrightControls, local_http_server: str
    ) -> None:
        url1 = f"{local_http_server}/index.html"
        url2 = f"{local_http_server}/page2.html"
        await headless_controls.navigate(url1)
        await headless_controls.navigate(url2)
        result = await headless_controls.go_back()
        assert result is True
        assert await headless_controls.engine.get_current_url() == url1

    async def test_go_forward_after_go_back(
        self, headless_controls: PlaywrightControls, local_http_server: str
    ) -> None:
        url1 = f"{local_http_server}/index.html"
        url2 = f"{local_http_server}/page2.html"
        await headless_controls.navigate(url1)
        await headless_controls.navigate(url2)
        await headless_controls.go_back()
        result = await headless_controls.go_forward()
        assert result is True
        assert await headless_controls.engine.get_current_url() == url2

    async def test_scroll_down_returns_true(
        self, headless_controls: PlaywrightControls, local_http_server: str
    ) -> None:
        await headless_controls.navigate(f"{local_http_server}/index.html")
        assert await headless_controls.scroll("down", 200) is True

    async def test_scroll_up_returns_true(
        self, headless_controls: PlaywrightControls, local_http_server: str
    ) -> None:
        await headless_controls.navigate(f"{local_http_server}/index.html")
        await headless_controls.scroll("down", 200)
        assert await headless_controls.scroll("up", 200) is True

    async def test_scroll_left_returns_true(
        self, headless_controls: PlaywrightControls, local_http_server: str
    ) -> None:
        await headless_controls.navigate(f"{local_http_server}/index.html")
        assert await headless_controls.scroll("left", 100) is True

    async def test_scroll_right_returns_true(
        self, headless_controls: PlaywrightControls, local_http_server: str
    ) -> None:
        await headless_controls.navigate(f"{local_http_server}/index.html")
        assert await headless_controls.scroll("right", 100) is True

    async def test_click_returns_true(
        self, headless_controls: PlaywrightControls, local_http_server: str
    ) -> None:
        await headless_controls.navigate(f"{local_http_server}/index.html")
        assert await headless_controls.click(100, 100) is True

    async def test_type_text_returns_true(
        self, headless_controls: PlaywrightControls, local_http_server: str
    ) -> None:
        await headless_controls.navigate(f"{local_http_server}/index.html")
        page = headless_controls.engine._require_page()
        await page.click("#inp")
        assert await headless_controls.type_text("hello") is True

    async def test_press_key_returns_true(
        self, headless_controls: PlaywrightControls, local_http_server: str
    ) -> None:
        await headless_controls.navigate(f"{local_http_server}/index.html")
        assert await headless_controls.press_key("Tab") is True

    async def test_wait_for_navigation_returns_true(
        self, headless_controls: PlaywrightControls, local_http_server: str
    ) -> None:
        await headless_controls.navigate(f"{local_http_server}/index.html")
        assert await headless_controls.wait_for_navigation() is True
