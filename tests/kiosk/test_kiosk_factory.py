from __future__ import annotations

import pytest

from src.kiosk.kiosk.factory.base import KioskFactory


def test_kiosk_factory_cannot_be_instantiated() -> None:
    with pytest.raises(TypeError):
        KioskFactory()  # type: ignore[abstract]


def test_concrete_factory_without_build_cannot_be_instantiated() -> None:
    class Incomplete(KioskFactory):
        pass

    with pytest.raises(TypeError):
        Incomplete()
