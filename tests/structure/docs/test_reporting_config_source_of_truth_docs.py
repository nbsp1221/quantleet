from __future__ import annotations

import json

from tests.support import ROOT


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_product_index_routes_reporting_config_source_of_truth_specs() -> None:
    index = _read("docs/product-specs/index.md")

    assert "reporting-config-source-of-truth.md" in index
    assert "reporting-config-source-of-truth-test-scenarios.md" in index
    assert "report.run.strategy_config" in index
    assert "current implemented Stage 4 first-slice WFA contract" in index


def test_public_docs_do_not_teach_strategy_parameters_reporting_hook() -> None:
    public_docs = "\n".join(
        path.read_text(encoding="utf-8") for path in (ROOT / "docs" / "site").rglob("*.md")
    )

    assert "Strategy.parameters()" not in public_docs
    assert "def parameters" not in public_docs
    assert "strategy_parameters" not in public_docs


def test_canonical_report_snapshots_use_strategy_config() -> None:
    snapshots = json.loads(
        (ROOT / "tests" / "fixtures" / "backtest" / "canonical_report_snapshots.json").read_text(
            encoding="utf-8"
        )
    )

    for snapshot in snapshots.values():
        run = snapshot["run"]
        assert "strategy_config" in run
        assert "strategy_parameters" not in run
