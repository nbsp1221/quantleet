import importlib

import pytest

from quantcraft import Exchange, MarketType, TimeBar


def test_public_import_smoke() -> None:
    assert MarketType.SPOT == "spot"
    assert TimeBar is not None
    assert Exchange is not None


def test_public_import_surface_rejects_unknown_root_exports() -> None:
    import quantcraft

    with pytest.raises(AttributeError, match="has no attribute"):
        getattr(quantcraft, "UnknownExport")


def test_data_public_import_surface_exposes_time_bar_and_bar_series() -> None:
    data_module = importlib.import_module("quantcraft.data")

    assert getattr(data_module, "TimeBar", None) is not None
    assert getattr(data_module, "BarSeries", None) is not None
    assert getattr(data_module, "CCXTDataSource", None) is not None
    assert getattr(data_module, "CSVDataSource", None) is not None
    assert getattr(data_module, "DataFrameDataSource", None) is not None


def test_root_time_bar_resolves_to_the_canonical_data_time_bar() -> None:
    data_module = importlib.import_module("quantcraft.data")

    assert TimeBar is getattr(data_module, "TimeBar")


def test_research_public_import_surface_exposes_backtest_engine_and_hides_run_backtest() -> None:
    research_module = importlib.import_module("quantcraft.research")
    application_module = importlib.import_module("quantcraft.research.application")

    assert getattr(research_module, "BacktestEngine", None) is not None
    assert getattr(research_module, "Strategy", None) is not None
    assert getattr(research_module, "ta", None) is not None
    assert getattr(research_module, "qc", None) is not None
    assert not hasattr(research_module, "run_backtest")
    assert not hasattr(application_module, "run_backtest")
