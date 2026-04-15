"""Unit tests for Kiosk abstract base class."""
from __future__ import annotations

from uuid import UUID

from pydantic import PrivateAttr

from tests.kiosk.conftest import ConcreteControls, ConcreteEngine, ConcreteKiosk


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _engine(healthy: bool = True) -> ConcreteEngine:
    """ConcreteEngine whose is_healthy() returns a fixed value."""
    class _E(ConcreteEngine):
        async def is_healthy(self) -> bool:
            return healthy

    return _E(engine_type="mock")


def _kiosk(engine: ConcreteEngine | None = None, **kwargs) -> ConcreteKiosk:
    return ConcreteKiosk(
        engine=engine or _engine(),
        default_page="https://example.com",
        kiosk_name="test",
        **kwargs,
    )


class CountingControls(ConcreteControls):
    """ConcreteControls that records navigate calls via a PrivateAttr counter."""

    _navigate_calls: list[str] = PrivateAttr(default_factory=list)

    async def navigate(self, url: str) -> bool:
        self._navigate_calls.append(url)
        return True


# ---------------------------------------------------------------------------
# kiosk_id
# ---------------------------------------------------------------------------

def test_kiosk_id_auto_generated() -> None:
    assert _kiosk().kiosk_id is not None


def test_kiosk_id_is_valid_uuid() -> None:
    assert isinstance(_kiosk().kiosk_id, UUID)


def test_two_instances_have_different_ids() -> None:
    assert _kiosk().kiosk_id != _kiosk().kiosk_id


# ---------------------------------------------------------------------------
# allowed_urls whitelist
# ---------------------------------------------------------------------------

async def test_allowed_urls_blocks_non_whitelisted() -> None:
    """Blocked URL returns False; controls.navigate is never reached."""
    engine = _engine()
    controls = CountingControls(control_type="test", engine=engine)
    kiosk = _kiosk(engine=engine, allowed_urls=["https://allowed.com"])
    kiosk.controls = controls

    result = await kiosk.navigate("https://blocked.com")

    assert result is False
    assert controls._navigate_calls == []


async def test_allowed_urls_allows_whitelisted() -> None:
    """Whitelisted URL is forwarded to controls.navigate."""
    engine = _engine()
    controls = CountingControls(control_type="test", engine=engine)
    kiosk = _kiosk(engine=engine, allowed_urls=["https://allowed.com"])
    kiosk.controls = controls

    result = await kiosk.navigate("https://allowed.com")

    assert result is True
    assert controls._navigate_calls == ["https://allowed.com"]


async def test_empty_allowed_urls_allows_any() -> None:
    """Empty whitelist means every URL is forwarded to controls."""
    engine = _engine()
    controls = CountingControls(control_type="test", engine=engine)
    kiosk = _kiosk(engine=engine, allowed_urls=[])
    kiosk.controls = controls

    result = await kiosk.navigate("https://anywhere.com")

    assert result is True
    assert len(controls._navigate_calls) == 1


# ---------------------------------------------------------------------------
# is_healthy
# ---------------------------------------------------------------------------

async def test_is_healthy_false_when_not_running() -> None:
    """is_running=False short-circuits before engine.is_healthy() is called."""
    kiosk = _kiosk(engine=_engine(healthy=True))
    kiosk.is_running = False
    # Python's `and` short-circuit ensures engine.is_healthy() is never awaited
    assert await kiosk.is_healthy() is False


async def test_is_healthy_delegates_to_engine_when_running() -> None:
    """When running, result reflects engine.is_healthy()."""
    kiosk = _kiosk(engine=_engine(healthy=True))
    kiosk.is_running = True
    assert await kiosk.is_healthy() is True
