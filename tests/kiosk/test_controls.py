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
# scroll base validation (ConcreteControls calls super().scroll())
# ---------------------------------------------------------------------------

async def test_scroll_base_raises_on_zero(engine_with_resources: ConcreteEngine) -> None:
    controls = ConcreteControls(control_type="test", engine=engine_with_resources)
    with pytest.raises(ValueError, match="greater than 0"):
        await controls.scroll("down", 0)


async def test_scroll_base_raises_on_negative(engine_with_resources: ConcreteEngine) -> None:
    controls = ConcreteControls(control_type="test", engine=engine_with_resources)
    with pytest.raises(ValueError, match="greater than 0"):
        await controls.scroll("up", -10)


async def test_scroll_base_passes_positive(engine_with_resources: ConcreteEngine) -> None:
    controls = ConcreteControls(control_type="test", engine=engine_with_resources)
    result = await controls.scroll("down", 100)
    assert result is True
