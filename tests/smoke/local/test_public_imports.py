import importlib

import pytest

import quantleet


def test_data_public_import_surface_exposes_time_bar_and_bar_series() -> None:
    data_module = importlib.import_module("quantleet.data")

    assert getattr(data_module, "TimeBar", None) is not None
    assert getattr(data_module, "BarSeries", None) is not None
    assert getattr(data_module, "CCXTDataSource", None) is not None
    assert getattr(data_module, "CSVDataSource", None) is not None
    assert getattr(data_module, "DataFrameDataSource", None) is not None


def test_root_package_exports_no_legacy_public_symbols() -> None:
    for name in ("Exchange", "MarketType", "TimeBar", "BacktestEngine"):
        with pytest.raises(AttributeError, match="has no attribute"):
            getattr(quantleet, name)


def test_research_public_import_surface_exposes_strategy_and_parameter_study() -> None:
    research_module = importlib.import_module("quantleet.research")

    assert getattr(research_module, "Strategy", None) is not None
    assert getattr(research_module, "ParameterStudy", None) is not None
    assert getattr(research_module, "GridSearchResult", None) is not None
    assert getattr(research_module, "GridSearchRow", None) is not None
    assert getattr(research_module, "ta", None) is not None
    assert getattr(research_module, "qc", None) is not None
    assert not hasattr(research_module, "run_backtest")
    assert not hasattr(research_module, "BacktestEngine")


def test_strategy_public_import_surface_exposes_strategy_config_contract() -> None:
    strategy_module = importlib.import_module("quantleet.strategy")
    research_module = importlib.import_module("quantleet.research")

    assert getattr(strategy_module, "Strategy", None) is not None
    assert getattr(strategy_module, "StrategyConfig", None) is not None
    assert getattr(strategy_module, "StrategyConfigError", None) is not None
    assert getattr(strategy_module, "StrategyConfigDeclarationError", None) is not None
    assert getattr(strategy_module, "StrategyConfigValidationError", None) is not None
    assert getattr(strategy_module, "StrategyConfigMutationError", None) is not None
    assert getattr(research_module, "Strategy") is getattr(strategy_module, "Strategy")


def test_capability_public_surfaces_import_cleanly() -> None:
    research_module = importlib.import_module("quantleet.research")
    strategy_module = importlib.import_module("quantleet.strategy")
    backtest_module = importlib.import_module("quantleet.backtest")
    execution_module = importlib.import_module("quantleet.execution")
    integrations_module = importlib.import_module("quantleet.integrations")
    ccxt_module = importlib.import_module("quantleet.integrations.venues.ccxt")

    assert getattr(backtest_module, "BacktestEngine", None) is not None
    assert getattr(backtest_module, "CostConfig", None) is not None
    assert getattr(backtest_module, "BacktestReport", None) is not None
    assert getattr(backtest_module, "RunManifest", None) is not None
    assert getattr(backtest_module, "ExecutionAssumptions", None) is not None
    assert getattr(backtest_module, "ReturnMetrics", None) is not None
    assert getattr(backtest_module, "RiskMetrics", None) is not None
    assert getattr(backtest_module, "TradeMetrics", None) is not None
    assert getattr(backtest_module, "CostMetrics", None) is not None
    assert getattr(backtest_module, "ExposureMetrics", None) is not None
    assert getattr(backtest_module, "EquityPoint", None) is not None
    assert getattr(backtest_module, "ReportingFill", None) is not None
    assert getattr(backtest_module, "ClosedTrade", None) is not None
    assert getattr(backtest_module, "BacktestResult", None) is not None
    assert getattr(backtest_module, "BacktestSummary", None) is not None
    assert getattr(backtest_module, "ExposureSummary", None) is not None
    assert getattr(strategy_module, "Strategy", None) is not None
    assert getattr(strategy_module, "StrategyConfig", None) is not None
    assert getattr(research_module, "Strategy", None) is not None
    assert getattr(research_module, "ParameterStudy", None) is not None
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
        assert not hasattr(ccxt_module, name)
    assert getattr(execution_module, "__all__", None) == []
    assert getattr(integrations_module, "__all__", None) == []


def test_removed_legacy_paths_no_longer_import() -> None:
    for module_name in (
        "quantleet.exchange",
        "quantleet.data.adapters.exchange_backend",
        "quantleet.data.domain",
        "quantleet.data.domain.bars",
        "quantleet.data.domain.sources",
        "quantleet.research.domain",
        "quantleet.research.domain.series",
        "quantleet.research.application",
        "quantleet.research.application.backtest",
        "quantleet.research.application.engine",
        "quantleet.research.application.order_activation",
        "quantleet.research.application.strategy",
        "quantleet.research.application._runtime",
        "quantleet.research.adapters",
        "quantleet.research.adapters.execution_model",
        "quantleet.data.application",
        "quantleet.trading.application",
        "quantleet.trading.adapters",
    ):
        with pytest.raises(ModuleNotFoundError):
            importlib.import_module(module_name)
