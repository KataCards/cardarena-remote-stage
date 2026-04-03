"""Unit tests for Engine base class — validators and handle_error."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock

import pytest
from pydantic import ValidationError

from tests.kiosk.conftest import ConcreteEngine


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _engine(tmp_html: Path, **overrides) -> ConcreteEngine:
    """Build a ConcreteEngine with sensible defaults, applying keyword overrides."""
    defaults: dict = {
        "engine_type": "test",
        "resources": {"not_found": str(tmp_html)},
        "error_map": {404: "not_found"},
    }
    defaults.update(overrides)
    return ConcreteEngine(**defaults)


# ---------------------------------------------------------------------------
# error_map validator
# ---------------------------------------------------------------------------

def test_invalid_code_below_range(tmp_html: Path) -> None:
    with pytest.raises(ValidationError, match="Invalid HTTP status code"):
        _engine(tmp_html, error_map={99: "not_found"})


def test_invalid_code_above_range(tmp_html: Path) -> None:
    with pytest.raises(ValidationError, match="Invalid HTTP status code"):
        _engine(tmp_html, error_map={600: "not_found"})


@pytest.mark.parametrize("code", [100, 404, 599])
def test_boundary_codes_accepted(tmp_html: Path, code: int) -> None:
    engine = _engine(tmp_html, error_map={code: "not_found"})
    assert code in engine.error_map


# ---------------------------------------------------------------------------
# resources validator
# ---------------------------------------------------------------------------

def test_missing_resource_path_raises(tmp_html: Path) -> None:
    with pytest.raises(ValidationError, match="does not exist"):
        _engine(tmp_html, resources={"k": "/nonexistent/path/file.html"})


def test_valid_resource_path_accepted(tmp_html: Path) -> None:
    engine = _engine(tmp_html, resources={"not_found": str(tmp_html)})
    assert "not_found" in engine.resources


# ---------------------------------------------------------------------------
# cross-field validator: error_map keys must exist in resources
# ---------------------------------------------------------------------------

def test_error_map_key_not_in_resources_raises(tmp_html: Path) -> None:
    with pytest.raises(ValidationError, match="does not exist in resources"):
        _engine(
            tmp_html,
            resources={"not_found": str(tmp_html)},
            error_map={404: "missing_key"},
        )


# ---------------------------------------------------------------------------
# handle_error
# ---------------------------------------------------------------------------

async def test_handle_error_returns_correct_path(
    engine_with_resources: ConcreteEngine,
) -> None:
    path = await engine_with_resources.handle_error(404)
    assert path == engine_with_resources.resources["not_found"]


async def test_handle_error_invokes_on_error_callback(
    engine_with_resources: ConcreteEngine,
) -> None:
    callback = AsyncMock()
    engine_with_resources.on_error = callback
    await engine_with_resources.handle_error(404)
    callback.assert_awaited_once_with(404)


async def test_handle_error_no_callback_still_returns_path(
    engine_with_resources: ConcreteEngine,
) -> None:
    assert engine_with_resources.on_error is None
    path = await engine_with_resources.handle_error(404)
    assert path == engine_with_resources.resources["not_found"]


async def test_handle_error_raises_key_error_on_unknown_code(
    engine_with_resources: ConcreteEngine,
) -> None:
    with pytest.raises(KeyError, match="999"):
        await engine_with_resources.handle_error(999)
