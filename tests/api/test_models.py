"""Tests for API Pydantic models."""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from src.api.models.kiosk import KioskStatus, KioskSummary, NavigateRequest
from src.api.models.schedule import AdBreak, ScheduleEntry, ScheduleRequest


def test_navigate_request_valid_https() -> None:
    req = NavigateRequest(url="https://example.com/page")
    assert req.url == "https://example.com/page"


def test_navigate_request_valid_http() -> None:
    req = NavigateRequest(url="http://localhost:8080")
    assert req.url == "http://localhost:8080"


def test_navigate_request_rejects_bare_string() -> None:
    with pytest.raises(ValidationError):
        NavigateRequest(url="not-a-url")


def test_navigate_request_rejects_missing_scheme() -> None:
    with pytest.raises(ValidationError):
        NavigateRequest(url="example.com")


def test_navigate_request_is_frozen() -> None:
    req = NavigateRequest(url="https://example.com")
    with pytest.raises(Exception):
        req.url = "https://other.com"  # type: ignore[misc]


def test_kiosk_status_fields() -> None:
    status = KioskStatus(
        uuid="abc",
        current_url="https://example.com",
        is_running=True,
        error=None,
    )
    assert status.uuid == "abc"
    assert status.error is None


def test_kiosk_status_is_frozen() -> None:
    status = KioskStatus(uuid="x", current_url="https://a.com", is_running=False, error=None)
    with pytest.raises(Exception):
        status.uuid = "y"  # type: ignore[misc]


def test_kiosk_summary_fields() -> None:
    s = KioskSummary(uuid="u1", is_running=True, current_url="https://ex.com")
    assert s.uuid == "u1"
    assert s.is_running is True


def test_schedule_entry_fields() -> None:
    entry = ScheduleEntry(url="https://a.com", duration_seconds=30, order=1)
    assert entry.order == 1


def test_ad_break_fields() -> None:
    ad = AdBreak(url="https://ad.com", duration_seconds=15)
    assert ad.duration_seconds == 15


def test_schedule_request_entries() -> None:
    req = ScheduleRequest(entries=[
        ScheduleEntry(url="https://a.com", duration_seconds=10, order=1),
        ScheduleEntry(url="https://b.com", duration_seconds=20, order=2),
    ])
    assert len(req.entries) == 2


def test_schedule_models_are_frozen() -> None:
    entry = ScheduleEntry(url="https://a.com", duration_seconds=10, order=1)
    with pytest.raises(Exception):
        entry.order = 99  # type: ignore[misc]
