"""Tests for schedule, cancel, and ad-break routes."""
from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock

from src.api.registry import KioskRegistry
from src.api.routes.schedule import build_router
from src.api.scheduler import KioskScheduler
from src.security.base.principal import Principal, Scope
from src.security.dependencies import get_principal


def _make_scheduler() -> MagicMock:
    scheduler = MagicMock(spec=KioskScheduler)
    scheduler.run_schedule = MagicMock()
    scheduler.cancel = MagicMock(return_value=True)
    scheduler.run_ad_break = AsyncMock()
    return scheduler


def _make_app(
    registry: KioskRegistry,
    scheduler: MagicMock,
    scopes: list[Scope],
) -> FastAPI:
    app = FastAPI()
    app.include_router(build_router(registry, scheduler))

    async def _mock_principal() -> Principal:
        return Principal(id="test", auth_method="api_key", scopes=scopes)

    app.dependency_overrides[get_principal] = _mock_principal
    return app


def _registry_with_kiosk(uuid: str = "uuid-1") -> KioskRegistry:
    registry = KioskRegistry()
    registry.register(uuid, MagicMock())
    return registry


def test_post_schedule_returns_204() -> None:
    registry = _registry_with_kiosk()
    scheduler = _make_scheduler()
    body = {"entries": [{"url": "https://a.com", "duration_seconds": 10, "order": 1}]}
    response = TestClient(_make_app(registry, scheduler, [Scope.CONTROL])).post(
        "/kiosks/uuid-1/schedule", json=body
    )
    assert response.status_code == 204
    scheduler.run_schedule.assert_called_once()


def test_post_schedule_unknown_uuid_returns_404() -> None:
    scheduler = _make_scheduler()
    body = {"entries": [{"url": "https://a.com", "duration_seconds": 10, "order": 1}]}
    response = TestClient(_make_app(KioskRegistry(), scheduler, [Scope.CONTROL])).post(
        "/kiosks/bad-uuid/schedule", json=body
    )
    assert response.status_code == 404


def test_post_schedule_cancel_returns_204() -> None:
    registry = _registry_with_kiosk()
    scheduler = _make_scheduler()
    response = TestClient(_make_app(registry, scheduler, [Scope.CONTROL])).post(
        "/kiosks/uuid-1/schedule/cancel"
    )
    assert response.status_code == 204
    scheduler.cancel.assert_called_once_with("uuid-1")


def test_post_ad_break_returns_204() -> None:
    registry = _registry_with_kiosk()
    scheduler = _make_scheduler()
    body = {"url": "https://ad.com", "duration_seconds": 0}
    response = TestClient(_make_app(registry, scheduler, [Scope.CONTROL])).post(
        "/kiosks/uuid-1/ad-break", json=body
    )
    assert response.status_code == 204
    scheduler.run_ad_break.assert_called_once()


def test_post_ad_break_unknown_uuid_returns_404() -> None:
    scheduler = _make_scheduler()
    body = {"url": "https://ad.com", "duration_seconds": 5}
    response = TestClient(_make_app(KioskRegistry(), scheduler, [Scope.CONTROL])).post(
        "/kiosks/bad-uuid/ad-break", json=body
    )
    assert response.status_code == 404


def test_schedule_requires_control_scope() -> None:
    registry = _registry_with_kiosk()
    app = FastAPI()
    app.include_router(build_router(registry, _make_scheduler()))

    async def _read_only() -> Principal:
        return Principal(id="test", auth_method="api_key", scopes=[Scope.READ])

    app.dependency_overrides[get_principal] = _read_only
    body = {"entries": [{"url": "https://a.com", "duration_seconds": 10, "order": 1}]}
    response = TestClient(app, raise_server_exceptions=False).post(
        "/kiosks/uuid-1/schedule", json=body
    )
    assert response.status_code == 403
