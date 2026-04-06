"""Tests for KioskRegistry."""
from __future__ import annotations

import pytest
from src.api.registry import KioskRegistry


class _FakeKiosk:
    """Stand-in — avoids importing Playwright at test time."""


def test_register_and_get() -> None:
    registry = KioskRegistry()
    kiosk = _FakeKiosk()
    registry.register("uuid-1", kiosk)
    assert registry.get("uuid-1") is kiosk


def test_get_missing_returns_none() -> None:
    registry = KioskRegistry()
    assert registry.get("nonexistent") is None


def test_duplicate_register_raises() -> None:
    registry = KioskRegistry()
    registry.register("uuid-1", _FakeKiosk())
    with pytest.raises(ValueError, match="uuid-1"):
        registry.register("uuid-1", _FakeKiosk())


def test_deregister_existing() -> None:
    registry = KioskRegistry()
    registry.register("uuid-1", _FakeKiosk())
    assert registry.deregister("uuid-1") is True
    assert registry.get("uuid-1") is None


def test_deregister_nonexistent() -> None:
    registry = KioskRegistry()
    assert registry.deregister("nonexistent") is False


def test_list_returns_all() -> None:
    registry = KioskRegistry()
    k1, k2 = _FakeKiosk(), _FakeKiosk()
    registry.register("a", k1)
    registry.register("b", k2)
    assert registry.list() == {"a": k1, "b": k2}


def test_list_is_shallow_copy() -> None:
    registry = KioskRegistry()
    registry.register("a", _FakeKiosk())
    listing = registry.list()
    listing["injected"] = _FakeKiosk()
    assert registry.get("injected") is None


def test_deregister_leaves_others() -> None:
    registry = KioskRegistry()
    k1, k2 = _FakeKiosk(), _FakeKiosk()
    registry.register("a", k1)
    registry.register("b", k2)
    registry.deregister("a")
    assert registry.get("b") is k2
