"""Tests for KioskScheduler."""
from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock

from src.api.models.schedule import AdBreak, ScheduleEntry, ScheduleRequest
from src.api.registry import KioskRegistry
from src.api.scheduler import KioskScheduler


def _registry_with_kiosk(current_url: str = "https://current.com") -> tuple[KioskRegistry, MagicMock]:
    registry = KioskRegistry()
    kiosk = MagicMock()
    kiosk.navigate = AsyncMock(return_value=True)
    kiosk.engine = MagicMock()
    kiosk.engine.get_current_url = AsyncMock(return_value=current_url)
    registry.register("uuid-1", kiosk)
    return registry, kiosk


async def test_run_schedule_calls_navigate() -> None:
    registry, kiosk = _registry_with_kiosk()
    scheduler = KioskScheduler(registry)
    request = ScheduleRequest(entries=[
        ScheduleEntry(url="https://a.com", duration_seconds=0, order=1),
        ScheduleEntry(url="https://b.com", duration_seconds=0, order=2),
    ])
    scheduler.run_schedule("uuid-1", request)
    await asyncio.sleep(0.05)
    scheduler.cancel("uuid-1")
    assert kiosk.navigate.called


async def test_schedule_entries_sorted_by_order() -> None:
    registry, kiosk = _registry_with_kiosk()
    scheduler = KioskScheduler(registry)
    # Entries given out of order — scheduler must sort by `order` field
    request = ScheduleRequest(entries=[
        ScheduleEntry(url="https://b.com", duration_seconds=0, order=2),
        ScheduleEntry(url="https://a.com", duration_seconds=0, order=1),
    ])
    scheduler.run_schedule("uuid-1", request)
    await asyncio.sleep(0.05)
    scheduler.cancel("uuid-1")
    first_call_url = kiosk.navigate.call_args_list[0].args[0]
    assert first_call_url == "https://a.com"


async def test_cancel_returns_true_when_running() -> None:
    registry, _ = _registry_with_kiosk()
    scheduler = KioskScheduler(registry)
    scheduler.run_schedule("uuid-1", ScheduleRequest(entries=[
        ScheduleEntry(url="https://a.com", duration_seconds=60, order=1),
    ]))
    await asyncio.sleep(0.01)
    assert scheduler.cancel("uuid-1") is True


async def test_cancel_returns_false_when_not_running() -> None:
    registry, _ = _registry_with_kiosk()
    scheduler = KioskScheduler(registry)
    assert scheduler.cancel("uuid-1") is False


async def test_run_schedule_replaces_existing_task() -> None:
    registry, _ = _registry_with_kiosk()
    scheduler = KioskScheduler(registry)
    request = ScheduleRequest(entries=[
        ScheduleEntry(url="https://a.com", duration_seconds=60, order=1),
    ])
    scheduler.run_schedule("uuid-1", request)
    await asyncio.sleep(0.01)
    scheduler.run_schedule("uuid-1", request)  # must not raise
    await asyncio.sleep(0.01)
    assert scheduler.cancel("uuid-1") is True


async def test_ad_break_navigates_to_ad_then_returns() -> None:
    registry, kiosk = _registry_with_kiosk(current_url="https://current.com")
    scheduler = KioskScheduler(registry)
    await scheduler.run_ad_break("uuid-1", AdBreak(url="https://ad.com", duration_seconds=0))
    calls = [c.args[0] for c in kiosk.navigate.call_args_list]
    assert calls[0] == "https://ad.com"
    assert calls[1] == "https://current.com"
