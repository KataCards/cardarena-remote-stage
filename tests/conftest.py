from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _patch_configure_logging(monkeypatch: pytest.MonkeyPatch) -> None:
    """Patch configure_logging to prevent global logging handler mutations in tests.

    Patches both the original module and all re-exported paths to ensure
    modules that imported via 'from src.utils import configure_logging' are covered.
    """
    def noop(*args, **kwargs) -> None:
        return None

    # Patch original module
    monkeypatch.setattr("src.utils.monitoring.logging.configure_logging", noop)

    # Patch re-exported paths used by production code
    monkeypatch.setattr("src.utils.configure_logging", noop)
    monkeypatch.setattr("src.startup.configure_logging", noop)
    monkeypatch.setattr("src.main.configure_logging", noop)