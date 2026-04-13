"""Tests for GET /kiosks and GET /kiosks/{uuid}."""
from __future__ import annotations

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

from src.api.registry import KioskRegistry
from src.api.routes.kiosks import build_router
from src.security.base.principal import Principal, Scope
from src.security.dependencies import get_principal


def _make_app(registry: KioskRegistry, scopes: list[Scope]) -> FastAPI:
    app = FastAPI()
    app.include_router(build_router(registry))

    async def _mock_principal() -> Principal:
        return Principal(id="test", auth_method="api_key", scopes=scopes)

    app.dependency_overrides[get_principal] = _mock_principal
    return app


def _make_fake_kiosk(url: str = "https://example.com", running: bool = True) -> MagicMock:
    kiosk = MagicMock()
    kiosk.is_running = running
    kiosk.current_url = url
    kiosk.engine = MagicMock()
    kiosk.engine.engine_type = "chromium"
    return kiosk


@pytest.fixture
def registry_with_kiosk() -> tuple[KioskRegistry, str, MagicMock]:
    registry = KioskRegistry()
    kiosk = _make_fake_kiosk()
    registry.register("test-uuid", kiosk)
    return registry, "test-uuid", kiosk


def test_list_kiosks_returns_200(registry_with_kiosk):
    registry, _, _ = registry_with_kiosk
    response = TestClient(_make_app(registry, [Scope.READ])).get("/kiosks")
    assert response.status_code == 200


def test_list_kiosks_returns_summaries(registry_with_kiosk):
    registry, uuid, _ = registry_with_kiosk
    data = TestClient(_make_app(registry, [Scope.READ])).get("/kiosks").json()
    assert len(data) == 1
    assert data[0]["uuid"] == uuid
    assert data[0]["is_running"] is True


def test_list_kiosks_requires_auth():
    registry = KioskRegistry()
    app = FastAPI()
    app.include_router(build_router(registry))

    async def _no_auth():
        raise HTTPException(status_code=401, detail="Unauthorized")

    app.dependency_overrides[get_principal] = _no_auth
    response = TestClient(app, raise_server_exceptions=False).get("/kiosks")
    assert response.status_code == 401


def test_get_kiosk_returns_status(registry_with_kiosk):
    registry, uuid, _ = registry_with_kiosk
    data = TestClient(_make_app(registry, [Scope.READ])).get(f"/kiosks/{uuid}").json()
    assert data["uuid"] == uuid
    assert data["is_running"] is True
    assert data["current_url"] == "https://example.com"
    assert data["error"] is None


def test_get_kiosk_not_found():
    registry = KioskRegistry()
    response = TestClient(_make_app(registry, [Scope.READ])).get("/kiosks/nonexistent")
    assert response.status_code == 404


# --- History endpoint tests
def test_get_history_requires_admin_scope(registry_with_kiosk):
    """GET /kiosks/{uuid}/history requires ADMIN scope."""
    registry, uuid, _ = registry_with_kiosk

    # READ scope → 403
    response = TestClient(_make_app(registry, [Scope.READ])).get(f"/kiosks/{uuid}/history")
    assert response.status_code == 403

    # CONTROL scope → 403
    response = TestClient(_make_app(registry, [Scope.CONTROL])).get(f"/kiosks/{uuid}/history")
    assert response.status_code == 403

    # No credentials → 401
    app = FastAPI()
    app.include_router(build_router(registry))

    async def _no_auth():
        raise HTTPException(status_code=401, detail="Unauthorized")

    app.dependency_overrides[get_principal] = _no_auth
    response = TestClient(app, raise_server_exceptions=False).get(f"/kiosks/{uuid}/history")
    assert response.status_code == 401

    # ADMIN scope → 200
    response = TestClient(_make_app(registry, [Scope.ADMIN])).get(f"/kiosks/{uuid}/history")
    assert response.status_code == 200


def test_get_history_not_found():
    """GET /kiosks/{uuid}/history returns 404 for unknown UUID."""
    registry = KioskRegistry()
    response = TestClient(_make_app(registry, [Scope.ADMIN])).get("/kiosks/nonexistent/history")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"]["code"] == "not_found"


def test_get_history_newest_first(registry_with_kiosk):
    """GET /kiosks/{uuid}/history returns events newest first."""
    registry, uuid, _ = registry_with_kiosk
    log = registry.get_log(uuid)

    # Record three events in chronological order
    log.record("event_1", success=True, detail="first")
    log.record("event_2", success=False, detail="second")
    log.record("event_3", success=True, detail="third")

    # Fetch history
    response = TestClient(_make_app(registry, [Scope.ADMIN])).get(f"/kiosks/{uuid}/history")
    assert response.status_code == 200
    data = response.json()

    # Assert newest first (event_3, event_2, event_1)
    assert len(data) == 3
    assert data[0]["event"] == "event_3"
    assert data[0]["success"] is True
    assert data[0]["context"]["detail"] == "third"

    assert data[1]["event"] == "event_2"
    assert data[1]["success"] is False
    assert data[1]["context"]["detail"] == "second"

    assert data[2]["event"] == "event_1"
    assert data[2]["success"] is True
    assert data[2]["context"]["detail"] == "first"