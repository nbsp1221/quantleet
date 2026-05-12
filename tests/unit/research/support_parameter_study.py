from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from quantleet.backtest import BacktestEngine, BacktestResult
from quantleet.data import BarSeries, TimeBar
from quantleet.strategy import Strategy, StrategyConfig
from quantleet.trading.domain.costs import CostConfig
from quantleet.trading.domain.events import BarEvent


def make_bars(*, closes: tuple[float, ...] = (100.0, 102.0, 101.0, 104.0)) -> BarSeries:
    return BarSeries(
        symbol="TEST",
        timeframe="1m",
        bar_type="time",
        rows=tuple(
            TimeBar(
                timestamp=(index + 1) * 60,
                open=close,
                high=close + 1.0,
                low=close - 1.0,
                close=close,
                volume=1.0,
            )
            for index, close in enumerate(closes)
        ),
    )


def make_engine() -> BacktestEngine:
    return BacktestEngine(
        initial_cash=1_000.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
    )


class NoTradeConfig(StrategyConfig):
    x: int = 1
    fast: int = 5
    slow: int = 20
    name: str = "alpha"
    count: int = 3
    ratio: float = 0.5
    enabled: bool = True
    maybe: int | None = None
    status: str = "reserved-looking"


class NoTradeStrategy(Strategy[NoTradeConfig]):
    def on_bar(self, bar: BarEvent) -> None:
        return None


class BuyOnceStrategy(NoTradeStrategy):
    def init(self) -> None:
        self._entered = False

    def on_bar(self, bar: BarEvent) -> None:
        if not self._entered:
            self._entered = True
            self.buy(quantity=1.0, tag="entry")


class RoundTripStrategy(NoTradeStrategy):
    def init(self) -> None:
        self._seen = 0

    def on_bar(self, bar: BarEvent) -> None:
        self._seen += 1
        if self._seen == 1:
            self.buy(quantity=1.0, tag="entry")
        elif self._seen == 2 and self.position.is_open:
            self.sell(quantity=1.0, tag="exit")


@dataclass
class CountingEngine:
    calls: list[dict[str, Any]]

    def __init__(self) -> None:
        self.calls = []
        self._engine = make_engine()

    def run(
        self,
        *,
        strategy: type[Strategy[StrategyConfig]],
        config: StrategyConfig | None = None,
        bars: BarSeries | None = None,
        source: object | None = None,
        label: str | None = None,
    ) -> BacktestResult:
        self.calls.append(
            {"strategy": strategy, "config": config, "bars": bars, "source": source, "label": label}
        )
        return self._engine.run(strategy=strategy, config=config, bars=bars, label=label)
