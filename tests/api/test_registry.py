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
    assert registry.list_all() == {"a": k1, "b": k2}


def test_list_is_shallow_copy() -> None:
    registry = KioskRegistry()
    registry.register("a", _FakeKiosk())
    listing = registry.list_all()
    listing["injected"] = _FakeKiosk()
    assert registry.get("injected") is None


def test_deregister_leaves_others() -> None:
    registry = KioskRegistry()
    k1, k2 = _FakeKiosk(), _FakeKiosk()
    registry.register("a", k1)
    registry.register("b", k2)
    registry.deregister("a")
    assert registry.get("b") is k2


# --- Activity log lifecycle tests
def test_register_creates_activity_log() -> None:
    """Registering a kiosk creates an associated activity log."""
    registry = KioskRegistry()
    registry.register("uuid-1", _FakeKiosk())
    log = registry.get_log("uuid-1")
    assert log is not None


def test_get_log_returns_none_for_nonexistent() -> None:
    """get_log returns None for UUIDs that were never registered."""
    registry = KioskRegistry()
    assert registry.get_log("nonexistent") is None


def test_activity_log_records_events() -> None:
    """Activity log can record and retrieve events."""
    registry = KioskRegistry()
    registry.register("uuid-1", _FakeKiosk())
    log = registry.get_log("uuid-1")
    assert log is not None
    
    log.record("test_event", success=True, detail="test")
    events = log.list_all()
    
    assert len(events) == 1
    assert events[0].event == "test_event"
    assert events[0].success is True
    assert events[0].context["detail"] == "test"


def test_deregister_removes_activity_log() -> None:
    """Deregistering a kiosk removes its activity log."""
    registry = KioskRegistry()
    registry.register("uuid-1", _FakeKiosk())
    
    # Verify log exists
    assert registry.get_log("uuid-1") is not None
    
    # Deregister and verify log is removed
    registry.deregister("uuid-1")
    assert registry.get_log("uuid-1") is None


def test_deregister_removes_only_target_log() -> None:
    """Deregistering one kiosk doesn't affect other kiosks' logs."""
    registry = KioskRegistry()
    registry.register("a", _FakeKiosk())
    registry.register("b", _FakeKiosk())
    
    log_a = registry.get_log("a")
    log_b = registry.get_log("b")
    assert log_a is not None
    assert log_b is not None
    
    # Record events in both logs
    log_a.record("event_a")
    log_b.record("event_b")
    
    # Deregister 'a' and verify 'b' log is intact
    registry.deregister("a")
    assert registry.get_log("a") is None
    assert registry.get_log("b") is log_b
    assert len(log_b.list_all()) == 1