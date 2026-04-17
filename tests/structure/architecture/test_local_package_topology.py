from __future__ import annotations

from pathlib import Path

from tests.support import ROOT


def test_local_owner_files_exist() -> None:
    expected_paths = (
        Path("src/quantcraft/data/bars.py"),
        Path("src/quantcraft/data/sources.py"),
        Path("src/quantcraft/research/series.py"),
    )

    for relative_path in expected_paths:
        assert (ROOT / relative_path).exists(), f"missing owner path: {relative_path}"


def test_removed_domain_shims_stay_absent() -> None:
    removed_paths = (
        ROOT / "src/quantcraft/data/domain",
        ROOT / "src/quantcraft/research/domain",
    )

    for path in removed_paths:
        assert not path.exists(), f"legacy path should be removed: {path}"


def test_removed_placeholder_directories_stay_absent() -> None:
    removed_paths = (
        ROOT / "src/quantcraft/data/application",
        ROOT / "src/quantcraft/trading/application",
        ROOT / "src/quantcraft/trading/adapters",
    )

    for path in removed_paths:
        assert not path.exists(), f"placeholder path should be removed: {path}"
