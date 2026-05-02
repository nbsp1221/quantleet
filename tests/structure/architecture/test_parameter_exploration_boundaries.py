from __future__ import annotations

import ast
import inspect
from pathlib import Path

from quantcraft.backtest import BacktestEngine
from quantcraft.research import ParameterStudy
from tests.support import ROOT

DEFERRED_CONTROLS = {"source", "n_jobs", "workers", "parallel", "executor"}


def _imports_parameter_exploration(path: Path) -> bool:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if any(
                alias.name == "quantcraft.research.parameter_exploration"
                for alias in node.names
            ):
                return True
        elif isinstance(node, ast.ImportFrom):
            if node.module == "quantcraft.research.parameter_exploration":
                return True
    return False


def test_parameter_exploration_lives_under_research_boundary() -> None:
    assert (ROOT / "src" / "quantcraft" / "research" / "parameter_exploration.py").exists()


def test_backtest_trading_and_execution_do_not_import_parameter_exploration() -> None:
    for package_name in ("backtest", "trading", "execution"):
        package_root = ROOT / "src" / "quantcraft" / package_name
        offenders = [
            path
            for path in package_root.rglob("*.py")
            if _imports_parameter_exploration(path)
        ]
        assert offenders == []


def test_backtest_surface_does_not_gain_optimizer_or_study_exports() -> None:
    import quantcraft.backtest as backtest

    assert not hasattr(BacktestEngine, "optimize")
    for name in ("ParameterStudy", "GridSearchResult", "GridSearchRow"):
        assert not hasattr(backtest, name)


def test_parameter_study_public_signatures_omit_deferred_controls() -> None:
    study_signature = inspect.signature(ParameterStudy)
    search_signature = inspect.signature(ParameterStudy.grid_search)

    assert DEFERRED_CONTROLS.isdisjoint(study_signature.parameters)
    assert DEFERRED_CONTROLS.isdisjoint(search_signature.parameters)


def test_no_heavy_optimizer_dependency_is_added_for_beta() -> None:
    pyproject_text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")

    for dependency_name in ("optuna", "ray", "scikit-optimize", "skopt"):
        assert dependency_name not in pyproject_text
