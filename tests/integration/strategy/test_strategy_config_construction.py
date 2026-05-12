from __future__ import annotations

import pytest

from quantleet.backtest import BacktestEngine, CostConfig
from quantleet.data import DataFrameDataSource
from quantleet.strategy import Strategy, StrategyConfig, StrategyConfigMutationError
from quantleet.trading.domain.events import BarEvent


class EntryConfig(StrategyConfig):
    threshold: float = 10.0
    tag: str = "configured-entry"


class ConfiguredEntryStrategy(Strategy[EntryConfig]):
    def init(self) -> None:
        self.threshold_seen_in_init = self.config.threshold

    def on_bar(self, bar: BarEvent) -> None:
        if bar.close > self.config.threshold:
            self.buy(quantity=1.0, tag=self.config.tag)


def _source() -> DataFrameDataSource:
    return DataFrameDataSource(
        frame=[
            {
                "timestamp": "1970-01-01T00:01:00+00:00",
                "open": 9.0,
                "high": 9.0,
                "low": 9.0,
                "close": 9.0,
                "volume": 1.0,
            },
            {
                "timestamp": "1970-01-01T00:02:00+00:00",
                "open": 12.0,
                "high": 12.0,
                "low": 12.0,
                "close": 12.0,
                "volume": 1.0,
            },
            {
                "timestamp": "1970-01-01T00:03:00+00:00",
                "open": 12.0,
                "high": 12.0,
                "low": 12.0,
                "close": 12.0,
                "volume": 1.0,
            },
        ],
        symbol="BTC/USDT",
        timeframe="1m",
    )


def test_backtest_runtime_preserves_configured_strategy_construction() -> None:
    result = BacktestEngine(
        initial_cash=1_000.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
    ).run(
        source=_source(),
        strategy=ConfiguredEntryStrategy,
        config=EntryConfig(threshold=11.0, tag="entry"),
    )

    assert result.report.trades.fill_count == 1
    assert result.report.fills[0].tag == "entry"
    assert result.report.run.strategy_config == {"threshold": 11.0, "tag": "entry"}


def test_backtest_runtime_rejects_config_mutation_before_orders_are_emitted() -> None:
    class MutatingStrategy(Strategy[EntryConfig]):
        def on_bar(self, bar: BarEvent) -> None:
            self.config.threshold = 1.0
            self.buy(quantity=1.0)

    with pytest.raises(StrategyConfigMutationError):
        BacktestEngine(
            initial_cash=1_000.0,
            costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
        ).run(source=_source(), strategy=MutatingStrategy)
