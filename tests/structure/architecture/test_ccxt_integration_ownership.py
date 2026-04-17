from __future__ import annotations

import ast
from pathlib import Path

from tests.support import ROOT


def _parse_module(relative_path: str) -> ast.AST:
    return ast.parse((ROOT / relative_path).read_text(encoding="utf-8"))


def test_ccxt_integration_owner_files_exist() -> None:
    expected_paths = (
        Path("src/quantcraft/integrations/venues/__init__.py"),
        Path("src/quantcraft/integrations/venues/ccxt/__init__.py"),
        Path("src/quantcraft/integrations/venues/ccxt/market_data.py"),
    )

    for relative_path in expected_paths:
        assert (ROOT / relative_path).exists(), (
            f"missing ccxt integration owner path: {relative_path}"
        )


def test_ccxt_market_data_owner_contains_exchange_behavior() -> None:
    tree = _parse_module("src/quantcraft/integrations/venues/ccxt/market_data.py")

    defined_names = {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef)
    }

    assert {
        "_suppress_import_stderr",
        "MarketType",
        "Exchange",
        "CCXTBackend",
        "_fetch_ohlcv_range",
        "_make_ccxt_exchange",
        "_validate_symbol_contract",
    } <= defined_names


def test_removed_exchange_compatibility_shims_stay_absent() -> None:
    assert not (ROOT / "src/quantcraft/data/adapters/exchange_backend.py").exists()
    assert not (ROOT / "src/quantcraft/exchange.py").exists()


def test_ccxt_data_source_imports_canonical_integrations_owner() -> None:
    tree = _parse_module("src/quantcraft/data/adapters/ccxt_source.py")

    imported_modules = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
        and node.module != "__future__"
    }

    assert "quantcraft.integrations.venues.ccxt.market_data" in imported_modules
    assert "quantcraft.data.adapters.exchange_backend" not in imported_modules
