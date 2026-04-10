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


async def test_get_page_raises_before_launch(tmp_html: Path) -> None:
    engine = _engine(tmp_html)
    with pytest.raises(RuntimeError, match="not running"):
        engine.get_page()


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
        await mock_pw_engine._handle_response(mock_response)

    callback.assert_not_awaited()
