"""Unit tests for PlaywrightEngine."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.kiosk.engine.playwright import PlaywrightEngine


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _engine(tmp_html: Path, **kwargs) -> PlaywrightEngine:
    return PlaywrightEngine(
        browser_type="chromium",
        resources={"not_found": str(tmp_html)},
        error_map={404: "not_found"},
        **kwargs,
    )


# ---------------------------------------------------------------------------
# model_post_init
# ---------------------------------------------------------------------------

def test_model_post_init_chromium(tmp_html: Path) -> None:
    engine = _engine(tmp_html)
    assert engine.engine_type == "playwright-chromium"


def test_model_post_init_firefox(tmp_html: Path) -> None:
    engine = PlaywrightEngine(
        browser_type="firefox",
        resources={"not_found": str(tmp_html)},
        error_map={404: "not_found"},
    )
    assert engine.engine_type == "playwright-firefox"


def test_model_post_init_webkit(tmp_html: Path) -> None:
    engine = PlaywrightEngine(
        browser_type="webkit",
        resources={"not_found": str(tmp_html)},
        error_map={404: "not_found"},
    )
    assert engine.engine_type == "playwright-webkit"


# ---------------------------------------------------------------------------
# Health / state before launch
# ---------------------------------------------------------------------------

async def test_is_healthy_false_before_launch(tmp_html: Path) -> None:
    engine = _engine(tmp_html)
    assert await engine.is_healthy() is False


async def test_require_page_raises_before_launch(tmp_html: Path) -> None:
    engine = _engine(tmp_html)
    with pytest.raises(RuntimeError, match="not running"):
        engine._require_page()


async def test_close_does_not_raise_when_shutdown_steps_fail(tmp_html: Path) -> None:
    engine = _engine(tmp_html)

    page = MagicMock()
    page.close = AsyncMock(side_effect=RuntimeError("page close failed"))

    browser = MagicMock()
    browser.close = AsyncMock(side_effect=RuntimeError("browser close failed"))

    playwright = MagicMock()
    playwright.stop = AsyncMock(side_effect=RuntimeError("stop failed"))

    engine._page = page
    engine._browser = browser
    engine._playwright = playwright

    await engine.close()  # must not raise

    assert engine._page is None
    assert engine._browser is None
    assert engine._playwright is None


# ---------------------------------------------------------------------------
# _handle_response
# ---------------------------------------------------------------------------

async def test_handle_response_calls_on_error_for_mapped_document_status(
    mock_pw_engine: PlaywrightEngine,
) -> None:
    callback = AsyncMock()
    mock_pw_engine.on_error = callback

    mock_response = MagicMock()
    mock_response.status = 404
    mock_response.request.resource_type = "document"
    mock_response.frame = mock_pw_engine._page.main_frame

    await mock_pw_engine._handle_response(mock_response)
    callback.assert_awaited_once_with(404)


async def test_handle_response_ignores_non_mapped_status(
    mock_pw_engine: PlaywrightEngine,
) -> None:
    callback = AsyncMock()
    mock_pw_engine.on_error = callback

    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.request.resource_type = "document"
    mock_response.frame = mock_pw_engine._page.main_frame

    await mock_pw_engine._handle_response(mock_response)
    callback.assert_not_awaited()


async def test_handle_response_ignores_non_document_resource_type(
    mock_pw_engine: PlaywrightEngine,
) -> None:
    callback = AsyncMock()
    mock_pw_engine.on_error = callback

    for resource_type in ("image", "stylesheet", "script", "font", "xhr"):
        mock_response = MagicMock()
        mock_response.status = 404
        mock_response.request.resource_type = resource_type
        mock_response.frame = mock_pw_engine._page.main_frame
        await mock_pw_engine._handle_response(mock_response)

    callback.assert_not_awaited()


async def test_handle_response_ignores_sub_frame_document_errors(
    mock_pw_engine: PlaywrightEngine,
) -> None:
    """Iframe 403s (e.g. YouTube consent frames) must not trigger error navigation."""
    callback = AsyncMock()
    mock_pw_engine.on_error = callback

    mock_response = MagicMock()
    mock_response.status = 403
    mock_response.request.resource_type = "document"
    mock_response.frame = MagicMock()  # a sub-frame, not main_frame

    mock_pw_engine.error_map = {403: "not_found"}

    await mock_pw_engine._handle_response(mock_response)
    callback.assert_not_awaited()


async def test_handle_response_fires_for_main_frame_document_error(
    mock_pw_engine: PlaywrightEngine,
) -> None:
    """A 403 on the main frame must still trigger error navigation."""
    callback = AsyncMock()
    mock_pw_engine.on_error = callback
    mock_pw_engine.error_map = {403: "not_found"}

    mock_response = MagicMock()
    mock_response.status = 403
    mock_response.request.resource_type = "document"
    mock_response.frame = mock_pw_engine._page.main_frame

    await mock_pw_engine._handle_response(mock_response)
    callback.assert_awaited_once_with(403)
