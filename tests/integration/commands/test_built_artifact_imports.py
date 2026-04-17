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

        module_path = quantcraft.__file__ or ""
        assert "site-packages" in module_path, module_path
        assert module_path.endswith("__init__.py"), module_path
        for name in ("Exchange", "MarketType", "TimeBar", "BacktestEngine"):
            try:
                getattr(quantcraft, name)
            except AttributeError:
                pass
            else:
                raise AssertionError(f"quantcraft should not export {name}")

        data_module = importlib.import_module("quantcraft.data")
        assert getattr(data_module, "TimeBar", None) is not None
        assert getattr(data_module, "BarSeries", None) is not None
        assert getattr(data_module, "CCXTDataSource", None) is not None
        assert getattr(data_module, "CSVDataSource", None) is not None
        assert getattr(data_module, "DataFrameDataSource", None) is not None

        research_module = importlib.import_module("quantcraft.research")
        backtest_module = importlib.import_module("quantcraft.backtest")
        execution_module = importlib.import_module("quantcraft.execution")
        integrations_module = importlib.import_module("quantcraft.integrations")
        ccxt_module = importlib.import_module("quantcraft.integrations.venues.ccxt")
        assert getattr(research_module, "Strategy", None) is not None
        assert getattr(research_module, "ta", None) is not None
        assert getattr(research_module, "qc", None) is not None
        assert not hasattr(research_module, "BacktestEngine")
        assert not hasattr(research_module, "run_backtest")
        assert getattr(backtest_module, "BacktestEngine", None) is not None
        assert getattr(backtest_module, "BacktestResult", None) is not None
        assert getattr(backtest_module, "BacktestSummary", None) is not None
        assert getattr(backtest_module, "ExposureSummary", None) is not None
        assert getattr(ccxt_module, "Exchange", None) is not None
        assert getattr(ccxt_module, "MarketType", None) is not None
        for name in (
            "CCXTBackend",
            "TimeBar",
            "_DEFAULT_PAGINATION_LIMIT",
            "_fetch_ohlcv_range",
            "_make_ccxt_exchange",
            "_validate_symbol_contract",
            "ccxt",
        ):
            assert not hasattr(ccxt_module, name), name
        assert getattr(execution_module, "__all__", None) == []
        assert getattr(integrations_module, "__all__", None) == []

        for module_name in (
            "quantcraft.exchange",
            "quantcraft.data.adapters.exchange_backend",
            "quantcraft.data.domain",
            "quantcraft.data.domain.bars",
            "quantcraft.data.domain.sources",
            "quantcraft.research.domain",
            "quantcraft.research.domain.series",
            "quantcraft.research.application",
            "quantcraft.research.application.backtest",
            "quantcraft.research.application.engine",
            "quantcraft.research.application.order_activation",
            "quantcraft.research.application.strategy",
            "quantcraft.research.application._runtime",
            "quantcraft.research.adapters",
            "quantcraft.research.adapters.execution_model",
            "quantcraft.data.application",
            "quantcraft.trading.application",
            "quantcraft.trading.adapters",
        ):
            try:
                importlib.import_module(module_name)
            except ModuleNotFoundError:
                pass
            else:
                raise AssertionError(f"{module_name} should not be importable")
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
