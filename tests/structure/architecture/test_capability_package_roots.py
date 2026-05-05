from pathlib import Path

from tests.support import ROOT


def test_capability_package_roots_exist() -> None:
    expected_paths = (
        Path("src/quantleet/backtest/__init__.py"),
        Path("src/quantleet/execution/__init__.py"),
        Path("src/quantleet/integrations/__init__.py"),
    )

    for relative_path in expected_paths:
        assert (ROOT / relative_path).exists(), f"missing capability package root: {relative_path}"
