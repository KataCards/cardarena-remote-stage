from __future__ import annotations

from collections import deque
from datetime import datetime, timezone

from .models import ActivityEvent


class ActivityLog:
    """Bounded ring buffer of ActivityEvent records for a single kiosk."""

    def __init__(self, maxsize: int = 100) -> None:
        self._buffer: deque[ActivityEvent] = deque(maxlen=maxsize)

    def record(self, event: str, success: bool = True, **context) -> None:
        """Append a new event timestamped to the current UTC time."""
        self._buffer.append(
            ActivityEvent(
                timestamp=datetime.now(timezone.utc),
                event=event,
                success=success,
                context=context,
            )
        )

    def list_all(self) -> list[ActivityEvent]:
        """Return all events as a list, newest first."""
        return list(reversed(self._buffer))
