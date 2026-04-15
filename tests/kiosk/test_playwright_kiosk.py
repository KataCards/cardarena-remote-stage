"""Unit and E2E tests for PlaywrightKiosk."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, patch  # AsyncMock used for asyncio.sleep patch

import pytest
from structlog.testing import capture_logs

from pydantic import PrivateAttr

from src.kiosk.engine.playwright import PlaywrightEngine
from src.kiosk.kiosk.playwright import PlaywrightKiosk
from src.kiosk.controls.playwright import PlaywrightControls
from tests.kiosk.conftest import ConcretePlaywrightKiosk


class FailingControls(PlaywrightControls):
    """Controls that always returns False from navigate and counts calls."""

    _navigate_calls: int = PrivateAttr(default=0)

    async def navigate(self, url: str) -> bool:
        self._navigate_calls += 1
        return False


class RaisingControls(PlaywrightControls):
    """Controls that raise while navigating."""

    async def navigate(self, url: str) -> bool:
        raise RuntimeError("navigation unavailable")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _engine(tmp_html: Path) -> PlaywrightEngine:
    return PlaywrightEngine(
        browser_type="chromium",
        resources={"not_found": str(tmp_html)},
        error_map={404: "not_found"},
    )


def _kiosk(tmp_html: Path, **kwargs) -> ConcretePlaywrightKiosk:
    return ConcretePlaywrightKiosk(
        engine=_engine(tmp_html),
        default_page="https://example.com",
        kiosk_name="test",
        **kwargs,
    )


# ---------------------------------------------------------------------------
# Unit — model_post_init
# ---------------------------------------------------------------------------

def test_model_post_init_does_not_wire_on_error_when_no_error_map(tmp_html: Path) -> None:
    """on_error must remain None when the engine has an empty error_map."""
    engine = PlaywrightEngine(
        browser_type="chromium",
        resources={},
        error_map={},
    )
    kiosk = ConcretePlaywrightKiosk(
        engine=engine,
        default_page="https://example.com",
        kiosk_name="test",
    )
    assert kiosk.engine.on_error is None


def test_model_post_init_wires_on_error(tmp_html: Path) -> None:
    kiosk = _kiosk(tmp_html)
    # on_error is a bound method; compare underlying function and bound instance
    assert kiosk.engine.on_error.__func__ is PlaywrightKiosk._on_error
    assert kiosk.engine.on_error.__self__ is kiosk


# ---------------------------------------------------------------------------
# Unit — _navigate_with_retry
# ---------------------------------------------------------------------------

async def test_navigate_with_retry_raises_after_exhausting_retries(
    tmp_html: Path,
) -> None:
    kiosk = _kiosk(tmp_html, max_retries=3, retry_delay=1.0)
    controls = FailingControls(engine=kiosk.engine)
    kiosk.controls = controls

    with patch("asyncio.sleep", new_callable=AsyncMock):
        with pytest.raises(RuntimeError, match="Failed to navigate"):
            await kiosk._navigate_with_retry(f"file://{tmp_html}")

    assert controls._navigate_calls == 3


async def test_go_home_syncs_current_url_after_navigation(
    mock_pw_engine: PlaywrightEngine,
) -> None:
    kiosk = PlaywrightKiosk(
        engine=mock_pw_engine,
        default_page="https://home.example",
        kiosk_name="test",
    )
    kiosk.controls = PlaywrightControls(engine=mock_pw_engine)
    kiosk.current_url = "https://stale.example"
    mock_pw_engine._require_page().url = "https://home.example"

    result = await kiosk.go_home()

    assert result is True
    assert kiosk.current_url == "https://home.example"


# ---------------------------------------------------------------------------
# Unit — _on_error
# ---------------------------------------------------------------------------

async def test_on_error_silently_ignores_if_no_controls(tmp_html: Path) -> None:
    kiosk = _kiosk(tmp_html)
    assert kiosk.controls is None
    await kiosk._on_error(404)  # must not raise


async def test_on_error_logs_when_error_page_navigation_fails(
    tmp_html: Path,
) -> None:
    kiosk = _kiosk(tmp_html)
    kiosk.controls = RaisingControls(engine=kiosk.engine)

    with capture_logs() as captured:
        await kiosk._on_error(404)

    assert any(
        entry.get("event") == "error_page_navigation_failed"
        and entry.get("error_code") == 404
        for entry in captured
    )


# ---------------------------------------------------------------------------
# E2E tests
# ---------------------------------------------------------------------------

@pytest.mark.e2e
async def test_e2e_launch_and_close_cleanly(tmp_path: Path) -> None:
    html_file = tmp_path / "404.html"
    html_file.write_text("<html/>")
    kiosk = ConcretePlaywrightKiosk(
        engine=PlaywrightEngine(
            browser_type="chromium",
            headless=True,
            resources={"not_found": str(html_file)},
            error_map={404: "not_found"},
        ),
        default_page="https://example.com",
        kiosk_name="e2e",
    )
    async with kiosk:
        assert kiosk.is_running is True
    assert kiosk.is_running is False


@pytest.mark.e2e
async def test_e2e_navigate_real_url(running_kiosk: ConcretePlaywrightKiosk) -> None:
    result = await running_kiosk.navigate("https://example.com")
    assert result is True
    url = await running_kiosk.engine.get_current_url()
    assert "example.com" in url


@pytest.mark.e2e
async def test_e2e_screenshot_returns_bytes(running_kiosk: ConcretePlaywrightKiosk) -> None:
    data = await running_kiosk.screenshot()
    assert isinstance(data, bytes)
    assert len(data) > 0


@pytest.mark.e2e
async def test_e2e_go_back_and_forward(running_kiosk: ConcretePlaywrightKiosk) -> None:
    await running_kiosk.navigate("https://example.com")
    await running_kiosk.navigate("https://www.iana.org/domains/reserved")

    back = await running_kiosk.go_back()
    assert back is True
    url_after_back = await running_kiosk.engine.get_current_url()
    assert "example.com" in url_after_back

    forward = await running_kiosk.go_forward()
    assert forward is True


@pytest.mark.e2e
async def test_e2e_click(running_kiosk: ConcretePlaywrightKiosk) -> None:
    result = await running_kiosk.click(100, 100)
    assert result is True


@pytest.mark.e2e
async def test_e2e_type_text(running_kiosk: ConcretePlaywrightKiosk) -> None:
    await running_kiosk.navigate("https://example.com")
    page = running_kiosk.engine._require_page()
    await page.evaluate("document.body.innerHTML = '<input id=\"i\" />'")
    await page.focus("#i")
    result = await running_kiosk.type_text("hello")
    assert result is True


@pytest.mark.e2e
@pytest.mark.parametrize("direction", ["up", "down", "left", "right"])
async def test_e2e_scroll_all_directions(
    running_kiosk: ConcretePlaywrightKiosk, direction: str
) -> None:
    result = await running_kiosk.scroll(direction, 100)  # type: ignore[arg-type]
    assert result is True


@pytest.mark.e2e
async def test_e2e_press_key(running_kiosk: ConcretePlaywrightKiosk) -> None:
    result = await running_kiosk.press_key("Enter")
    assert result is True


@pytest.mark.e2e
async def test_e2e_is_healthy_true_when_running(
    running_kiosk: ConcretePlaywrightKiosk,
) -> None:
    assert await running_kiosk.is_healthy() is True


@pytest.mark.e2e
async def test_e2e_is_healthy_false_after_stop(tmp_path: Path) -> None:
    html_file = tmp_path / "404.html"
    html_file.write_text("<html/>")
    kiosk = ConcretePlaywrightKiosk(
        engine=PlaywrightEngine(
            browser_type="chromium",
            headless=True,
            resources={"not_found": str(html_file)},
            error_map={404: "not_found"},
        ),
        default_page="https://example.com",
        kiosk_name="e2e",
    )
    await kiosk.start()
    assert await kiosk.is_healthy() is True
    await kiosk.stop()
    assert await kiosk.is_healthy() is False


@pytest.mark.e2e
async def test_e2e_error_page_navigation(tmp_path: Path) -> None:
    """A 404 response triggers _on_error which navigates to the local error HTML."""
    html_file = tmp_path / "404.html"
    html_file.write_text("<html><body>Not Found</body></html>")

    kiosk = ConcretePlaywrightKiosk(
        engine=PlaywrightEngine(
            browser_type="chromium",
            headless=True,
            resources={"not_found": str(html_file)},
            error_map={404: "not_found"},
        ),
        default_page="https://example.com",
        kiosk_name="e2e",
    )

    async with kiosk:
        page = kiosk.engine._require_page()

        async def route_handler(route):
            await route.fulfill(status=404, body="not found")

        await page.route("**/trigger-404", route_handler)
        await page.goto("https://example.com/trigger-404", wait_until="commit")
        await page.wait_for_load_state("load")
        final_url = page.url
        assert final_url.startswith("file://") or "404" in final_url


@pytest.mark.e2e
async def test_e2e_whitelist_blocks_url(tmp_path: Path) -> None:
    html_file = tmp_path / "404.html"
    html_file.write_text("<html/>")
    kiosk = ConcretePlaywrightKiosk(
        engine=PlaywrightEngine(
            browser_type="chromium",
            headless=True,
            resources={"not_found": str(html_file)},
            error_map={404: "not_found"},
        ),
        default_page="https://example.com",
        kiosk_name="e2e",
        allowed_urls=["https://example.com"],
    )
    async with kiosk:
        result = await kiosk.navigate("https://other.example.com")
        assert result is False


@pytest.mark.e2e
async def test_e2e_whitelist_allows_url(tmp_path: Path) -> None:
    html_file = tmp_path / "404.html"
    html_file.write_text("<html/>")
    kiosk = ConcretePlaywrightKiosk(
        engine=PlaywrightEngine(
            browser_type="chromium",
            headless=True,
            resources={"not_found": str(html_file)},
            error_map={404: "not_found"},
        ),
        default_page="https://example.com",
        kiosk_name="e2e",
        allowed_urls=["https://example.com"],
    )
    async with kiosk:
        result = await kiosk.navigate("https://example.com")
        assert result is True
