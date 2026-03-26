from __future__ import annotations

import json

from tests.support import ROOT


def test_research_ergonomics_quickstart_doc_and_notebook_exist() -> None:
    quickstart_doc = ROOT / "docs" / "references" / "research-ergonomics-quickstart.md"
    quickstart_notebook = ROOT / "notebooks" / "research-ergonomics-quickstart.ipynb"

    assert quickstart_doc.exists()
    assert quickstart_notebook.exists()


def test_research_ergonomics_quickstart_doc_covers_canonical_usage_path() -> None:
    quickstart_doc = (
        ROOT / "docs" / "references" / "research-ergonomics-quickstart.md"
    ).read_text(encoding="utf-8")

    assert "from quantcraft.research import Strategy, ta, qc, run_backtest" in quickstart_doc
    assert "from quantcraft.data import DataFrameDataSource" in quickstart_doc
    assert "quantity=1" in quickstart_doc
    assert "SMA crossover" in quickstart_doc
    assert "RSI 30/70 mean reversion" in quickstart_doc


def test_research_ergonomics_quickstart_notebook_uses_canonical_import_path() -> None:
    notebook_path = ROOT / "notebooks" / "research-ergonomics-quickstart.ipynb"
    notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
    notebook_source = "\n".join("".join(cell.get("source", [])) for cell in notebook["cells"])

    assert "from quantcraft.research import " in notebook_source
    assert "from quantcraft.data import DataFrameDataSource" in notebook_source
    assert "Strategy" in notebook_source
    assert "ta" in notebook_source
    assert "qc" in notebook_source
    assert "run_backtest" in notebook_source
    assert "quantity=1" in notebook_source
    assert "SmaCrossStrategy" in notebook_source
    assert "Rsi3070Strategy" in notebook_source
    assert "trade_log" in notebook_source
