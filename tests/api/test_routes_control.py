"""Tests for POST /kiosks/{uuid}/navigate and /reload."""
from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock

from src.api.registry import KioskRegistry
from src.api.routes.control import build_router
from src.security.base.principal import Principal, Scope
from src.security.dependencies import get_principal


def _make_app(registry: KioskRegistry, scopes: list[Scope]) -> FastAPI:
    app = FastAPI()
    app.include_router(build_router(registry))

    async def _mock_principal() -> Principal:
        return Principal(id="test", auth_method="api_key", scopes=scopes)

    app.dependency_overrides[get_principal] = _mock_principal
    return app


def _make_kiosk(navigate_result: bool = True, reload_result: bool = True) -> MagicMock:
    kiosk = MagicMock()
    kiosk.navigate = AsyncMock(return_value=navigate_result)
    kiosk.reload = AsyncMock(return_value=reload_result)
    return kiosk


def _registry_with(kiosk: MagicMock, uuid: str = "uuid-1") -> KioskRegistry:
    r = KioskRegistry()
    r.register(uuid, kiosk)
    return r


def test_navigate_returns_204() -> None:
    kiosk = _make_kiosk()
    registry = _registry_with(kiosk)
    response = TestClient(_make_app(registry, [Scope.CONTROL])).post(
        "/kiosks/uuid-1/navigate", json={"url": "https://example.com"}
    )
    assert response.status_code == 204
    kiosk.navigate.assert_called_once_with("https://example.com")


def test_navigate_unknown_uuid_returns_404() -> None:
    response = TestClient(_make_app(KioskRegistry(), [Scope.CONTROL])).post(
        "/kiosks/bad-uuid/navigate", json={"url": "https://example.com"}
    )
    assert response.status_code == 404


def test_navigate_kiosk_failure_returns_500() -> None:
    kiosk = _make_kiosk(navigate_result=False)
    registry = _registry_with(kiosk)
    response = TestClient(
        _make_app(registry, [Scope.CONTROL]), raise_server_exceptions=False
    ).post("/kiosks/uuid-1/navigate", json={"url": "https://example.com"})
    assert response.status_code == 500
    kiosk.navigate.assert_called_once_with("https://example.com")


def test_reload_returns_204() -> None:
    kiosk = _make_kiosk()
    registry = _registry_with(kiosk)
    response = TestClient(_make_app(registry, [Scope.CONTROL])).post("/kiosks/uuid-1/reload")
    assert response.status_code == 204
    kiosk.reload.assert_called_once_with()


def test_reload_unknown_uuid_returns_404() -> None:
    response = TestClient(_make_app(KioskRegistry(), [Scope.CONTROL])).post(
        "/kiosks/bad-uuid/reload"
    )
    assert response.status_code == 404


def test_reload_kiosk_failure_returns_500() -> None:
    kiosk = _make_kiosk(reload_result=False)
    registry = _registry_with(kiosk)
    response = TestClient(
        _make_app(registry, [Scope.CONTROL]), raise_server_exceptions=False
    ).post("/kiosks/uuid-1/reload")
    assert response.status_code == 500


def test_control_requires_control_scope() -> None:
    app = FastAPI()
    app.include_router(build_router(KioskRegistry()))

    async def _read_only() -> Principal:
        return Principal(id="test", auth_method="api_key", scopes=[Scope.READ])

    app.dependency_overrides[get_principal] = _read_only
    response = TestClient(app, raise_server_exceptions=False).post(
        "/kiosks/any/navigate", json={"url": "https://example.com"}
    )
    assert response.status_code == 403


def test_control_requires_auth() -> None:
    app = FastAPI()
    app.include_router(build_router(KioskRegistry()))

    async def _no_auth():
        raise HTTPException(status_code=401, detail="Unauthorized")

    app.dependency_overrides[get_principal] = _no_auth
    response = TestClient(app, raise_server_exceptions=False).post(
        "/kiosks/any/navigate", json={"url": "https://example.com"}
    )
    assert response.status_code == 401
