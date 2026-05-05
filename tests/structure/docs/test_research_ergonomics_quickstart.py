from __future__ import annotations

import json

from tests.support import ROOT


def test_research_ergonomics_quickstart_doc_and_notebook_exist() -> None:
    quickstart_doc = ROOT / "docs" / "references" / "research-ergonomics-quickstart.md"
    quickstart_notebook = ROOT / "notebooks" / "research-ergonomics-quickstart.ipynb"
    real_data_plot_notebook = ROOT / "notebooks" / "backtest-plotting-real-data-example.ipynb"

    assert quickstart_doc.exists()
    assert quickstart_notebook.exists()
    assert real_data_plot_notebook.exists()


def test_research_ergonomics_quickstart_doc_covers_canonical_usage_path() -> None:
    quickstart_doc = (ROOT / "docs" / "references" / "research-ergonomics-quickstart.md").read_text(
        encoding="utf-8"
    )

    assert "from quantleet.backtest import BacktestEngine" in quickstart_doc
    assert "from quantleet.research import ParameterStudy, Strategy, ta, qc" in quickstart_doc
    assert "from quantleet.data import BarSeries, DataFrameDataSource, TimeBar" in quickstart_doc
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
    assert "may omit `symbol`" in quickstart_doc
    assert "Explicit `symbol=...` remains supported" in quickstart_doc
    assert "source.load() returns `BarSeries`" in quickstart_doc
    assert "source = DataFrameDataSource(" in quickstart_doc
    assert "bars = BarSeries(" in quickstart_doc
    assert "engine.run(" in quickstart_doc
    assert "source=source" in quickstart_doc
    assert "bars=bars" in quickstart_doc
    assert "fig = result.plot()" in quickstart_doc
    assert "plt.show()" in quickstart_doc
    assert 'fig.savefig("sma-cross.png")' in quickstart_doc
    assert "result.drawdown_curve" in quickstart_doc
    assert "result.plot(bars=" not in quickstart_doc
    assert "plot_backtest(" not in quickstart_doc
    assert "BacktestEngine.plot(" not in quickstart_doc
    assert "result.report.plot(" not in quickstart_doc
    assert "self.buy(quantity=1)" in quickstart_doc
    assert "self.sell(quantity=1)" in quickstart_doc
    assert "run_backtest" not in quickstart_doc


def test_research_ergonomics_quickstart_notebook_uses_canonical_import_path() -> None:
    notebook_path = ROOT / "notebooks" / "research-ergonomics-quickstart.ipynb"
    notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
    notebook_source = "\n".join("".join(cell.get("source", [])) for cell in notebook["cells"])

    assert "from quantleet.backtest import BacktestEngine" in notebook_source
    assert "from quantleet.research import Strategy, qc, ta" in notebook_source
    assert "from quantleet.data import BarSeries, DataFrameDataSource, TimeBar" in notebook_source
    assert "source = DataFrameDataSource(" in notebook_source
    assert "bars = source.load()" in notebook_source
    assert "BarSeries(" in notebook_source
    assert "TimeBar(" in notebook_source
    assert "engine.run(" in notebook_source
    assert "source=source" in notebook_source
    assert "bars=bars" in notebook_source
    assert "sma_result.plot()" in notebook_source
    assert "rsi_result.drawdown_curve" in notebook_source
    assert "result.plot(bars=" not in notebook_source
    assert "plot_backtest(" not in notebook_source
    assert "BacktestEngine.plot(" not in notebook_source
    assert "result.report.plot(" not in notebook_source
    assert "quantity=1" in notebook_source
    assert "self.buy(quantity=1)" in notebook_source
    assert "self.sell(quantity=1)" in notebook_source
    assert "SmaCrossStrategy" in notebook_source
    assert "Rsi3070Strategy" in notebook_source
    assert "self.position.is_open" in notebook_source
    assert "not self.position.is_open" in notebook_source
    assert "trade_log" in notebook_source
    assert "run_backtest" not in notebook_source


def test_real_data_plotting_example_uses_public_plot_flow() -> None:
    notebook_path = ROOT / "notebooks" / "backtest-plotting-real-data-example.ipynb"
    notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
    notebook_source = "\n".join("".join(cell.get("source", [])) for cell in notebook["cells"])

    assert "from quantleet.backtest import BacktestEngine" in notebook_source
    assert "from quantleet.data import CSVDataSource" in notebook_source
    assert "binance_usdm_btcusdtusdt_1h_2025.csv" in notebook_source
    assert "class Rsi3070Strategy(Strategy):" in notebook_source
    assert "engine.run(" in notebook_source
    assert "source=source" in notebook_source
    assert "result.summary" in notebook_source
    assert "result.report.run.bar_count" in notebook_source
    assert "fig = result.plot()" in notebook_source
    assert "result.plot(bars=" not in notebook_source
    assert "plot_backtest(" not in notebook_source
    assert "BacktestEngine.plot(" not in notebook_source
    assert "tests.support_backtest" not in notebook_source
