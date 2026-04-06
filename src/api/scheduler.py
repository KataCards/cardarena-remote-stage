"""KioskScheduler — manages asyncio background tasks for per-kiosk schedule loops."""
from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from src.api.models.schedule import AdBreak, ScheduleRequest

if TYPE_CHECKING:
    from src.api.registry import KioskRegistry


class KioskScheduler:
    """Manages one background asyncio.Task per kiosk UUID for continuous schedule loops."""

    def __init__(self, registry: "KioskRegistry") -> None:
        self._registry = registry
        self._tasks: dict[str, asyncio.Task] = {}

    def run_schedule(self, uuid: str, request: ScheduleRequest) -> None:
        """Start (or replace) a continuous schedule loop for the given kiosk."""
        self.cancel(uuid)
        self._tasks[uuid] = asyncio.create_task(self._loop_schedule(uuid, request))

    async def _loop_schedule(self, uuid: str, request: ScheduleRequest) -> None:
        kiosk = self._registry.get(uuid)
        sorted_entries = sorted(request.entries, key=lambda e: e.order)
        while True:
            for entry in sorted_entries:
                await kiosk.navigate(entry.url)
                await asyncio.sleep(entry.duration_seconds)

    async def run_ad_break(self, uuid: str, ad: AdBreak) -> None:
        """Navigate to the ad URL, wait, then return to the URL that was showing."""
        kiosk = self._registry.get(uuid)
        current_url = await kiosk.engine.get_current_url()
        await kiosk.navigate(ad.url)
        await asyncio.sleep(ad.duration_seconds)
        await kiosk.navigate(current_url)

    def cancel(self, uuid: str) -> bool:
        """Cancel the running schedule task for the given UUID.

        Returns True if a task was cancelled, False if none was running.
        """
        task = self._tasks.get(uuid)
        if task is None or task.done():
            return False
        task.cancel()
        return True
