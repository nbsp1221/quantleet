from __future__ import annotations

import os
import subprocess
import sys
import textwrap
from pathlib import Path
from tempfile import TemporaryDirectory

from tests.support import ROOT


def test_built_wheel_exposes_documented_public_imports() -> None:
    artifact_dir = ROOT / "dist"
    subprocess.run(
        ["uv", "build", "--out-dir", str(artifact_dir)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    wheels = sorted(artifact_dir.glob("quantcraft-*.whl"))
    assert wheels, "expected uv build to produce a quantcraft wheel"

    wheel_path = wheels[-1]
    script = textwrap.dedent(
        """
        import importlib

        import quantcraft
        from quantcraft import Exchange, MarketType, TimeBar

        module_path = quantcraft.__file__ or ""
        assert "site-packages" in module_path, module_path
        assert module_path.endswith("__init__.py"), module_path
        assert MarketType.SPOT == "spot"
        assert TimeBar is not None
        assert Exchange is not None

        data_module = importlib.import_module("quantcraft.data")
        assert getattr(data_module, "TimeBar", None) is not None
        assert getattr(data_module, "BarSeries", None) is not None
        assert getattr(data_module, "CCXTDataSource", None) is not None
        assert getattr(data_module, "CSVDataSource", None) is not None
        assert getattr(data_module, "DataFrameDataSource", None) is not None
        assert TimeBar is getattr(data_module, "TimeBar")

        research_module = importlib.import_module("quantcraft.research")
        application_module = importlib.import_module("quantcraft.research.application")
        assert getattr(research_module, "BacktestEngine", None) is not None
        assert getattr(research_module, "Strategy", None) is not None
        assert getattr(research_module, "ta", None) is not None
        assert getattr(research_module, "qc", None) is not None
        assert not hasattr(research_module, "run_backtest")
        assert not hasattr(application_module, "run_backtest")
        """
    )

    with TemporaryDirectory() as temp_dir:
        site_packages_dir = Path(temp_dir) / "site-packages"
        site_packages_dir.mkdir()
        subprocess.run(
            [
                "uv",
                "pip",
                "install",
                "--python",
                sys.executable,
                "--no-deps",
                "--reinstall",
                "--target",
                str(site_packages_dir),
                str(wheel_path),
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

        env = os.environ.copy()
        env["PYTHONPATH"] = str(site_packages_dir)
        env["PYTHONNOUSERSITE"] = "1"

        subprocess.run(
            [sys.executable, "-c", script],
            cwd=Path(temp_dir),
            env=env,
            check=True,
            capture_output=True,
            text=True,
        )
