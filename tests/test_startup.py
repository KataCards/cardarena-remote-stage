from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

from src.api.registry import KioskRegistry
from src.kiosk.kiosk.factory.base import KioskFactory
from src.startup import KioskStartupService


def _make_service() -> tuple[KioskStartupService, KioskRegistry, MagicMock]:
    registry = KioskRegistry()
    factory = MagicMock(spec=KioskFactory)
    return KioskStartupService(registry, factory), registry, factory


def test_startup_service_stores_registry_and_factory() -> None:
    service, registry, factory = _make_service()
    assert service._registry is registry
    assert service._factory is factory


def test_build_lifespan_returns_callable() -> None:
    service, _, _ = _make_service()
    assert callable(service.build_lifespan())


async def test_lifespan_builds_and_registers_kiosk() -> None:
    service, registry, factory = _make_service()
    mock_kiosk = MagicMock()
    mock_kiosk.start = AsyncMock()
    mock_kiosk.stop = AsyncMock()
    factory.build.return_value = mock_kiosk

    with (
        patch("src.startup.get_settings", return_value=MagicMock()),
        patch("src.startup.get_security_settings", return_value=MagicMock()),
        patch("src.startup.check_app_config"),
        patch("src.startup.check_security_config"),
    ):
        async with service.build_lifespan()(MagicMock()):
            factory.build.assert_called_once()
            mock_kiosk.start.assert_awaited_once()
            assert mock_kiosk in registry.list_all().values()

    mock_kiosk.stop.assert_awaited_once()


async def test_lifespan_stops_all_kiosks_on_exit() -> None:
    service, _, factory = _make_service()
    mock_kiosk = MagicMock()
    mock_kiosk.start = AsyncMock()
    mock_kiosk.stop = AsyncMock()
    factory.build.return_value = mock_kiosk

    with (
        patch("src.startup.get_settings", return_value=MagicMock()),
        patch("src.startup.get_security_settings", return_value=MagicMock()),
        patch("src.startup.check_app_config"),
        patch("src.startup.check_security_config"),
    ):
        async with service.build_lifespan()(MagicMock()):
            pass

    mock_kiosk.stop.assert_awaited_once()
