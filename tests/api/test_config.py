"""Tests for ApiSettings."""
from __future__ import annotations

from src.api.config import ApiSettings


def test_defaults() -> None:
    settings = ApiSettings(kiosk_error_page="", kiosk_allowed_urls=[])
    assert settings.kiosk_allowed_urls == []
    assert settings.kiosk_error_page == ""
    assert settings.kiosk_default_url == "https://example.com"
    assert settings.kiosk_name == "default"


def test_allowed_urls_parsed_from_comma_string() -> None:
    settings = ApiSettings(
        kiosk_allowed_urls="https://a.com, https://b.com, ",
        kiosk_error_page="",
    )
    assert settings.kiosk_allowed_urls == ["https://a.com", "https://b.com"]


def test_allowed_urls_accepts_list() -> None:
    settings = ApiSettings(
        kiosk_allowed_urls=["https://a.com", "https://b.com"],
        kiosk_error_page="",
    )
    assert settings.kiosk_allowed_urls == ["https://a.com", "https://b.com"]
