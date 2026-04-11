"""Unit tests for Controls abstract base class."""
from __future__ import annotations

import pytest

from src.kiosk.controls.base import Controls
from tests.kiosk.conftest import ConcreteControls, ConcreteEngine


# ---------------------------------------------------------------------------
# Instantiation guard
# ---------------------------------------------------------------------------

def test_cannot_instantiate_directly(engine_with_resources) -> None:
    with pytest.raises(TypeError):
        Controls(control_type="test", engine=engine_with_resources)  # type: ignore[abstract]


# ---------------------------------------------------------------------------
# Concrete implementation behavior
# ---------------------------------------------------------------------------

async def test_concrete_scroll_returns_true(engine_with_resources: ConcreteEngine) -> None:
    controls = ConcreteControls(control_type="test", engine=engine_with_resources)
    result = await controls.scroll("down", 100)
    assert result is True
