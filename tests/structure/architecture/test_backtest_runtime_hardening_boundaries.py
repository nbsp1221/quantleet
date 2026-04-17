from __future__ import annotations

import ast

from tests.support import ROOT


def _parse_module(relative_path: str) -> ast.AST:
    return ast.parse((ROOT / relative_path).read_text(encoding="utf-8"))


def test_backtest_loop_imports_execution_model_directly() -> None:
    tree = _parse_module("src/quantcraft/backtest/runtime.py")

    execution_model_imports = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        and node.module == "quantcraft.backtest.execution_model"
    ]

    imported_names = {
        alias.name for node in execution_model_imports for alias in node.names
    }

    assert "ConservativeOHLCVExecutionModel" in imported_names


def test_backtest_loop_uses_backtest_owned_strategy_driver() -> None:
    tree = _parse_module("src/quantcraft/backtest/runtime.py")

    runtime_imports = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        and node.module == "quantcraft.backtest.strategy_runtime"
    ]

    imported_names = {alias.name for node in runtime_imports for alias in node.names}

    assert "_StrategyDriver" in imported_names


def test_backtest_loop_does_not_revert_to_unnamed_synthetic_event_helper() -> None:
    tree = _parse_module("src/quantcraft/backtest/runtime.py")

    synthetic_helper_imports = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        and node.module == "quantcraft.research.adapters.synthetic_events"
    ]

    imported_names = {
        alias.name for node in synthetic_helper_imports for alias in node.names
    }

    assert "convert_bar_series_to_backtest_events" not in imported_names


def test_execution_model_wrapper_module_is_not_reintroduced() -> None:
    wrapper_path = ROOT / "src" / "quantcraft" / "research" / "adapters" / "synthetic_events.py"

    assert not wrapper_path.exists()


def test_research_backtest_routes_fill_state_transitions_through_trading_kernel() -> None:
    tree = _parse_module("src/quantcraft/backtest/runtime.py")

    state_imports = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        and node.module == "quantcraft.trading.domain.state"
    ]
    imported_names = {alias.name for node in state_imports for alias in node.names}
    local_function_names = {
        node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
    }
    called_names = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }

    assert {"TradingState", "apply_fill"} <= imported_names
    assert "apply_fill" not in local_function_names
    assert "apply_fill" in called_names


def test_removed_research_backtest_compatibility_modules() -> None:
    removed_paths = (
        ROOT / "src/quantcraft/research/application",
        ROOT / "src/quantcraft/research/adapters",
        ROOT / "src/quantcraft/research/adapters/execution_model.py",
    )

    for path in removed_paths:
        assert not path.exists(), f"legacy path should be removed: {path}"


def test_execution_package_does_not_define_a_second_position_engine() -> None:
    execution_root = ROOT / "src" / "quantcraft" / "execution"
    if not execution_root.exists():
        return

    for path in execution_root.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        defined_names = {
            node.name
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef)
        }
        state_imports = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
            and node.module == "quantcraft.trading.domain.state"
        ]
        imported_names = {alias.name for node in state_imports for alias in node.names}
        noncanonical_state_imports = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
            and node.module is not None
            and node.module.endswith(".state")
            and node.module != "quantcraft.trading.domain.state"
        ]

        assert "TradingState" not in defined_names, path
        assert "apply_fill" not in defined_names, path
        assert not noncanonical_state_imports, path
        assert imported_names <= {"TradingState", "apply_fill"}, path
