from __future__ import annotations

import asyncio
import contextvars
from typing import TYPE_CHECKING

from .models import AdBreak, ScheduleRequest
from src.utils import get_logger

if TYPE_CHECKING:
    from .registry import KioskRegistry


logger = get_logger(__name__)


class KioskScheduler:
    """Manages one background asyncio.Task per kiosk UUID for continuous schedule loops."""

    def __init__(self, registry: "KioskRegistry") -> None:
        self._registry = registry
        self._tasks: dict[str, asyncio.Task[None]] = {}

    def run_schedule(self, uuid: str, request: ScheduleRequest) -> None:
        """Start (or replace) a continuous schedule loop for the given kiosk."""
        self.cancel(uuid)
        logger.info("schedule_started", kiosk_uuid=uuid, entry_count=len(request.entries))
        # Copy context and clear request-scoped vars to prevent request_id leaking into background task
        ctx = contextvars.copy_context()
        self._tasks[uuid] = asyncio.create_task(ctx.run(self._loop_schedule, uuid, request))

    async def _loop_schedule(self, uuid: str, request: ScheduleRequest) -> None:
        kiosk = self._registry.get(uuid)
        if kiosk is None:
            raise ValueError(f"Kiosk not found: {uuid}")
        sorted_entries = sorted(request.entries, key=lambda e: e.order)
        try:
            while True:
                for entry in sorted_entries:
                    if not await kiosk.navigate(entry.url):
                        logger.error("navigation_failed", kiosk_uuid=uuid, url=entry.url)
                        continue
                    await asyncio.sleep(entry.duration_seconds)
        except asyncio.CancelledError:
            # Preserve task cancellation semantics so callers can shut loops down cleanly.
            raise
        except Exception:
            logger.error("schedule_crashed", kiosk_uuid=uuid, exc_info=True)
            raise

    async def run_ad_break(self, uuid: str, ad: AdBreak) -> None:
        """Navigate to the ad URL, wait, then return to the URL that was showing."""
        kiosk = self._registry.get(uuid)
        if kiosk is None:
            raise ValueError(f"Kiosk not found: {uuid}")
        current_url = kiosk.current_url
        if not current_url:
            raise ValueError(f"Kiosk has no current URL to return to: {uuid}")
        logger.info(
            "ad_break_started",
            kiosk_uuid=uuid,
            url=ad.url,
            duration_seconds=ad.duration_seconds,
        )
        await kiosk.navigate(ad.url)
        await asyncio.sleep(ad.duration_seconds)
        await kiosk.navigate(current_url)
        logger.info("ad_break_ended", kiosk_uuid=uuid, url=ad.url)

    def cancel(self, uuid: str) -> bool:
        """Cancel the running schedule task for the given UUID.

        Returns True if a task was cancelled, False if none was running.
        """
        task = self._tasks.get(uuid)
        if task is None or task.done():
            if uuid in self._tasks:
                del self._tasks[uuid]
            return False
        task.cancel()
        del self._tasks[uuid]
        logger.info("schedule_cancelled", kiosk_uuid=uuid)
        return True