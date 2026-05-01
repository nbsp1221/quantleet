from __future__ import annotations

import json

from tests.support import ROOT


def test_product_docs_promote_result_report_as_primary_inspection_path() -> None:
    product_spec = (ROOT / "docs" / "product-specs" / "research-ergonomics.md").read_text(
        encoding="utf-8"
    )

    assert "result.report" in product_spec
    assert "BacktestEngine.run(..., label=...)" in product_spec
    assert "Strategy.display_name" in product_spec
    assert "Strategy.parameters()" in product_spec
    assert "next_bar" in product_spec
    assert "conservative_ohlcv" in product_spec
    assert "mark_to_market" in product_spec


def test_quickstart_docs_show_result_report_plot_and_preserve_legacy_surfaces() -> None:
    quickstart = (ROOT / "docs" / "references" / "research-ergonomics-quickstart.md").read_text(
        encoding="utf-8"
    )

    assert "result.report" in quickstart
    assert "label=\"sma-cross\"" in quickstart
    assert "result.trade_log" in quickstart
    assert "result.equity_curve" in quickstart
    assert "result.drawdown_curve" in quickstart
    assert "result.summary" in quickstart
    assert "For visual inspection, `result.plot()`" in quickstart
    assert "For structured inspection, `result.report`" in quickstart


def test_quickstart_notebook_mentions_result_report() -> None:
    notebook_path = ROOT / "notebooks" / "research-ergonomics-quickstart.ipynb"
    notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
    notebook_source = "\n".join("".join(cell.get("source", [])) for cell in notebook["cells"])

    assert "sma_result.report" in notebook_source
    assert "rsi_result.report" in notebook_source
