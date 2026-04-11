"""Tests for application Settings."""
from __future__ import annotations

from src.config import Settings


def test_error_routing_defaults_to_true() -> None:
    assert Settings().kiosk_error_routing is True


def test_error_routing_can_be_disabled() -> None:
    assert Settings(kiosk_error_routing=False).kiosk_error_routing is False
