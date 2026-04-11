"""Tests for GET /health."""
from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api.registry import KioskRegistry
from src.api.routes.health import build_router


@pytest.fixture
def client() -> TestClient:
    registry = KioskRegistry()
    app = FastAPI()
    app.include_router(build_router(registry))
    return TestClient(app)


def test_health_returns_200(client: TestClient) -> None:
    assert client.get("/health").status_code == 200


def test_health_status_ok(client: TestClient) -> None:
    assert client.get("/health").json()["status"] == "ok"


def test_health_kiosk_count_empty(client: TestClient) -> None:
    assert client.get("/health").json()["kiosk_count"] == 0


def test_health_kiosk_count_with_kiosks() -> None:
    class _FakeKiosk:
        pass

    registry = KioskRegistry()
    registry.register("a", _FakeKiosk())
    registry.register("b", _FakeKiosk())
    app = FastAPI()
    app.include_router(build_router(registry))
    response = TestClient(app).get("/health")
    assert response.json()["kiosk_count"] == 2
