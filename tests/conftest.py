from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _patch_configure_logging(monkeypatch: pytest.MonkeyPatch) -> None:
    """Patch configure_logging to prevent global logging handler mutations in tests."""
    monkeypatch.setattr("src.utils.monitoring.logging.configure_logging", lambda *args, **kwargs: None)