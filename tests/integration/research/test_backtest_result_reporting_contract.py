from __future__ import annotations

from quantleet.backtest import BacktestEngine
from quantleet.strategy import Strategy, StrategyConfig
from quantleet.trading.domain.costs import CostConfig
from quantleet.trading.domain.events import BarEvent
from tests.integration.research.support_backtest_runner import (
    DeterministicEntryExitStrategy,
    fixture_bar_series,
    run_engine_backtest,
)


class MetadataConfig(StrategyConfig):
    fast: int = 20
    slow: int = 50
    zero_count: int = 0
    disabled: bool = False
    empty_name: str = ""
    zero_ratio: float = 0.0
    optional_level: int | None = None


class MetadataStrategy(Strategy[MetadataConfig]):
    def __init__(self, config: MetadataConfig | None = None) -> None:
        super().__init__(config)
        self.public_cache = "must not be introspected"

    @property
    def display_name(self) -> str | None:
        return "SMA 20/50"

    def on_bar(self, bar: BarEvent) -> None:
        return None


class ConflictingParametersStrategy(MetadataStrategy):
    parameters_call_count = 0

    def parameters(self) -> dict[str, object]:
        type(self).parameters_call_count += 1
        return {"fast": 999, "slow": 999}


class RaisingParametersStrategy(MetadataStrategy):
    def parameters(self) -> dict[str, object]:
        raise AssertionError("reporting must not call Strategy.parameters()")


def test_report_is_directly_reachable_from_engine_result() -> None:
    result = run_engine_backtest(
        bars=fixture_bar_series(),
        strategy=DeterministicEntryExitStrategy,
    )

    assert result.report.run.symbol == "BTC/USDT"
    assert result.report.run.timeframe == "1m"
    assert result.report.run.start_timestamp == 60
    assert result.report.run.end_timestamp == 180
    assert result.report.run.bar_count == 3
    assert result.report.run.initial_cash == 1_000.0
    assert result.report.run.execution_model_name == "conservative_ohlcv"
    assert result.report.returns.final_equity == result.summary.final_equity
    assert result.report.equity[-1].equity == result.summary.final_equity


def test_report_captures_strategy_identity_and_config_snapshot() -> None:
    result = _engine().run(
        bars=fixture_bar_series(),
        strategy=MetadataStrategy,
        label="sma-20-50",
    )

    assert result.report.run.strategy_class_name == "MetadataStrategy"
    assert result.report.run.strategy_display_name == "SMA 20/50"
    assert result.report.run.strategy_config == {
        "fast": 20,
        "slow": 50,
        "zero_count": 0,
        "disabled": False,
        "empty_name": "",
        "zero_ratio": 0.0,
        "optional_level": None,
    }
    assert not hasattr(result.report.run, "strategy_parameters")
    assert result.report.run.run_label == "sma-20-50"
    assert "public_cache" not in result.report.run.strategy_config


def test_report_uses_strategy_config_even_when_parameters_method_conflicts() -> None:
    ConflictingParametersStrategy.parameters_call_count = 0
    result = _engine().run(
        bars=fixture_bar_series(),
        strategy=ConflictingParametersStrategy,
    )

    assert result.report.run.strategy_config["fast"] == 20
    assert result.report.run.strategy_config["slow"] == 50
    assert ConflictingParametersStrategy.parameters_call_count == 0


def test_report_does_not_call_raising_parameters_method() -> None:
    result = _engine().run(
        bars=fixture_bar_series(),
        strategy=RaisingParametersStrategy,
    )

    assert result.report.run.strategy_config["fast"] == 20
    assert result.report.run.strategy_config["slow"] == 50


def test_config_less_strategy_reports_empty_config() -> None:
    result = _engine().run(
        bars=fixture_bar_series(),
        strategy=DeterministicEntryExitStrategy,
    )

    assert result.report.run.strategy_config == {}
    assert type(result.report.run.strategy_config) is dict


def test_report_exposes_structured_execution_assumptions() -> None:
    costs = CostConfig(tick_size=0.5, slippage_ticks=2.0, fee_rate=0.002)
    result = run_engine_backtest(
        bars=fixture_bar_series(),
        strategy=DeterministicEntryExitStrategy,
        costs=costs,
    )

    execution = result.report.execution

    assert execution.execution_model_name == "conservative_ohlcv"
    assert execution.order_activation_timing == "next_bar"
    assert execution.fill_price_basis == "conservative_ohlcv"
    assert execution.open_position_finalization == "mark_to_market"
    assert execution.tick_size == 0.5
    assert execution.slippage_ticks == 2.0
    assert execution.fee_rate == 0.002
    assert execution.annual_risk_free_rate == 0.0
    assert execution.periods_per_year is not None


def test_human_readable_report_is_grouped_and_scan_friendly() -> None:
    result = run_engine_backtest(
        bars=fixture_bar_series(),
        strategy=DeterministicEntryExitStrategy,
    )

    text = result.report.to_text()

    for section in (
        "Return",
        "Risk",
        "Trade Quality",
        "Costs",
        "Exposure And Ending State",
        "Execution Assumptions",
    ):
        assert section in text
    assert "BacktestReport(" not in text


def _engine() -> BacktestEngine:
    return BacktestEngine(
        initial_cash=1_000.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
    )
