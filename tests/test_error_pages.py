from __future__ import annotations

import logging

import pytest

from src.utils.error_pages import build_error_map


def test_build_error_map_warns_when_folder_missing(
    tmp_path, caplog: pytest.LogCaptureFixture
) -> None:
    missing = tmp_path / "does-not-exist"

    with caplog.at_level(logging.WARNING):
        resources, error_map = build_error_map(str(missing))

    assert resources == {}
    assert error_map == {}
    assert "Error pages directory is missing or not a directory" in caplog.text
