from __future__ import annotations

from pathlib import Path

import pytest

from src.config import Settings
from src.kiosk.kiosk.factory.base import KioskFactory
from src.kiosk.kiosk.factory.playwright import PlaywrightKioskFactory
from src.kiosk.kiosk.playwright import PlaywrightKiosk


def test_kiosk_factory_cannot_be_instantiated() -> None:
    with pytest.raises(TypeError):
        KioskFactory()  # type: ignore[abstract]


def test_concrete_factory_without_build_cannot_be_instantiated() -> None:
    class Incomplete(KioskFactory):
        pass

    with pytest.raises(TypeError):
        Incomplete()


def test_build_returns_playwright_kiosk() -> None:
    factory = PlaywrightKioskFactory()
    kiosk = factory.build(Settings())
    assert isinstance(kiosk, PlaywrightKiosk)


def test_build_kiosk_name_and_url_from_settings() -> None:
    kiosk = PlaywrightKioskFactory().build(
        Settings(kiosk_default_url="https://example.com", kiosk_name="my-kiosk")
    )
    assert kiosk.kiosk_name == "my-kiosk"
    assert kiosk.default_page == "https://example.com"


def test_build_allowed_urls_from_settings() -> None:
    kiosk = PlaywrightKioskFactory().build(
        Settings(kiosk_allowed_urls=["https://example.com", "https://other.com"])
    )
    assert kiosk.allowed_urls == ["https://example.com", "https://other.com"]


def test_build_with_error_pages_dir(tmp_path: Path) -> None:
    page_404 = tmp_path / "404"
    page_404.mkdir()
    (page_404 / "index.html").write_text("<html><body>Not Found</body></html>")
    kiosk = PlaywrightKioskFactory().build(
        Settings(kiosk_error_pages_dir=str(tmp_path))
    )
    assert 404 in kiosk.engine.error_map
    assert "404" in kiosk.engine.resources


def test_build_no_resources_when_no_error_config() -> None:
    kiosk = PlaywrightKioskFactory().build(Settings(kiosk_error_pages_dir=None))
    assert kiosk.engine.resources == {}
    assert kiosk.engine.error_map == {}


def test_build_fullscreen_does_not_inject_default_launch_args(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KIOSK_PLAYWRIGHT_LAUNCH_ARGS", "")
    kiosk = PlaywrightKioskFactory().build(Settings(kiosk_fullscreen=True))
    assert kiosk.engine.launch_args == []


def test_build_headless_forwarded_to_engine() -> None:
    kiosk = PlaywrightKioskFactory().build(Settings(kiosk_headless=True))
    assert kiosk.engine.headless is True


def test_build_browser_type_forwarded_to_engine(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KIOSK_PLAYWRIGHT_BROWSER_TYPE", "firefox")
    kiosk = PlaywrightKioskFactory().build(Settings())
    assert kiosk.engine.browser_type == "firefox"


def test_build_custom_launch_args_forwarded_to_engine(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(
        "KIOSK_PLAYWRIGHT_LAUNCH_ARGS",
        "--window-size=1920,1080 --incognito",
    )
    kiosk = PlaywrightKioskFactory().build(Settings())
    assert "--window-size=1920,1080" in kiosk.engine.launch_args
    assert "--incognito" in kiosk.engine.launch_args


def test_build_fullscreen_uses_only_explicit_custom_args(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KIOSK_PLAYWRIGHT_LAUNCH_ARGS", "--incognito")
    kiosk = PlaywrightKioskFactory().build(
        Settings(kiosk_fullscreen=True)
    )
    assert kiosk.engine.launch_args == ["--incognito"]


def test_build_no_error_map_when_routing_disabled(tmp_path: Path) -> None:
    """error_routing=False must produce empty resources/error_map even if dir is set."""
    page_404 = tmp_path / "404"
    page_404.mkdir()
    (page_404 / "index.html").write_text("<html><body>Not Found</body></html>")

    kiosk = PlaywrightKioskFactory().build(
        Settings(kiosk_error_pages_dir=str(tmp_path), kiosk_error_routing=False)
    )
    assert kiosk.engine.resources == {}
    assert kiosk.engine.error_map == {}
