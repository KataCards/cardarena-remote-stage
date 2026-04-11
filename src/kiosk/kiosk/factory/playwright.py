from __future__ import annotations

from src.config import Settings
from src.kiosk.engine.playwright import PlaywrightEngine
from src.kiosk.kiosk.base import Kiosk
from src.kiosk.kiosk.factory.base import KioskFactory
from src.kiosk.kiosk.playwright import PlaywrightKiosk
from src.utils import build_error_map


class PlaywrightKioskFactory(KioskFactory):
    """Builds a PlaywrightKiosk from application settings."""

    def build(self, settings: Settings) -> Kiosk:
        launch_args = (
            ["--kiosk", "--disable-infobars", "--no-first-run"]
            if settings.kiosk_fullscreen
            else []
        )
        if settings.kiosk_error_routing and settings.kiosk_error_pages_dir:
            resources, error_map = build_error_map(settings.kiosk_error_pages_dir)
        else:
            resources = {}
            error_map = {}

        engine = PlaywrightEngine(
            engine_type="playwright",
            resources=resources,
            error_map=error_map,
            headless=settings.kiosk_headless,
            fullscreen=settings.kiosk_fullscreen,
            launch_args=launch_args,
        )
        return PlaywrightKiosk(
            engine=engine,
            default_page=settings.kiosk_default_url,
            kiosk_name=settings.kiosk_name,
            allowed_urls=settings.kiosk_allowed_urls,
        )
