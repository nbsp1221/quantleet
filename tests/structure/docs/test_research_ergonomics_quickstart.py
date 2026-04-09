from __future__ import annotations

import json

from tests.support import ROOT


def test_research_ergonomics_quickstart_doc_and_notebook_exist() -> None:
    quickstart_doc = ROOT / "docs" / "references" / "research-ergonomics-quickstart.md"
    quickstart_notebook = ROOT / "notebooks" / "research-ergonomics-quickstart.ipynb"

    assert quickstart_doc.exists()
    assert quickstart_notebook.exists()


def test_research_ergonomics_quickstart_doc_covers_canonical_usage_path() -> None:
    quickstart_doc = (ROOT / "docs" / "references" / "research-ergonomics-quickstart.md").read_text(
        encoding="utf-8"
    )

    canonical_import = "from quantcraft.research import BacktestEngine, Strategy, ta, qc"
    assert canonical_import in quickstart_doc
    assert "from quantcraft.data import BarSeries, DataFrameDataSource, TimeBar" in quickstart_doc
    assert "quantity=1" in quickstart_doc
    assert "SMA crossover" in quickstart_doc
    assert "RSI 30/70 mean reversion" in quickstart_doc
    assert "Canonical User Journeys" in quickstart_doc
    for journey_marker in [
        "Clean Install To Public Imports",
        "DataFrame-Like Quickstart To First Backtest",
        "Materialized `BarSeries`",
        "Exchange-Backed Historical Research Flow",
    ]:
        assert journey_marker in quickstart_doc
    for required_field in [
        "starting state:",
        "user intent:",
        "success artifact:",
        "superficially passing but still bad:",
    ]:
        assert required_field in quickstart_doc
    assert "strict merge gates" in quickstart_doc
    assert "self.position.is_open" in quickstart_doc
    assert "not self.position.is_open" in quickstart_doc
    assert "source.load() returns `BarSeries`" in quickstart_doc
    assert "source = DataFrameDataSource(" in quickstart_doc
    assert "bars = BarSeries(" in quickstart_doc
    assert "engine.run(" in quickstart_doc
    assert "source=source" in quickstart_doc
    assert "bars=bars" in quickstart_doc
    assert "run_backtest" not in quickstart_doc


def test_research_ergonomics_quickstart_notebook_uses_canonical_import_path() -> None:
    notebook_path = ROOT / "notebooks" / "research-ergonomics-quickstart.ipynb"
    notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
    notebook_source = "\n".join("".join(cell.get("source", [])) for cell in notebook["cells"])

    assert "from quantcraft.research import " in notebook_source
    assert "from quantcraft.data import BarSeries, DataFrameDataSource, TimeBar" in notebook_source
    assert "BacktestEngine" in notebook_source
    assert "Strategy" in notebook_source
    assert "ta" in notebook_source
    assert "qc" in notebook_source
    assert "source = DataFrameDataSource(" in notebook_source
    assert "bars = source.load()" in notebook_source
    assert "BarSeries(" in notebook_source
    assert "TimeBar(" in notebook_source
    assert "engine.run(" in notebook_source
    assert "source=source" in notebook_source
    assert "bars=bars" in notebook_source
    assert "quantity=1" in notebook_source
    assert "SmaCrossStrategy" in notebook_source
    assert "Rsi3070Strategy" in notebook_source
    assert "self.position.is_open" in notebook_source
    assert "not self.position.is_open" in notebook_source
    assert "trade_log" in notebook_source
    assert "run_backtest" not in notebook_source
