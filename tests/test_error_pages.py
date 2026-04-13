from __future__ import annotations

from src.utils.exceptions.error_page_map import build_error_map


def test_build_error_map_warns_when_folder_missing(
    tmp_path,
    capsys,
) -> None:
    missing = tmp_path / "does-not-exist"

    resources, error_map = build_error_map(str(missing))
    captured = capsys.readouterr()

    assert resources == {}
    assert error_map == {}
    assert "Error pages directory is missing or not a directory" in captured.out
