from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import ClassVar

from quantleet.backtest import BacktestEngine, BacktestResult
from quantleet.data import BarSeries, TimeBar
from quantleet.research import Strategy
from quantleet.strategy import StrategyConfig
from quantleet.trading.domain.costs import CostConfig


class DeterministicEntryExitStrategy(Strategy):
    def init(self) -> None:
        self._seen_bars = 0

    def on_bar(self, bar) -> None:
        self._seen_bars += 1
        if self._seen_bars == 1:
            self.buy(quantity=1.0, tag="entry")
        elif self._seen_bars == 2:
            self.sell(
                quantity=1.0,
                order_type="limit",
                limit_price=114.0,
                tag="exit",
            )


class BuyAndHoldStrategy(Strategy):
    def init(self) -> None:
        self._entered = False

    def on_bar(self, bar) -> None:
        if not self._entered:
            self._entered = True
            self.buy(quantity=1.0, tag="entry")


class BuyThenImplicitSellStrategy(Strategy):
    def init(self) -> None:
        self._entered = False
        self._exited = False

    def on_bar(self, bar) -> None:
        if not self._entered:
            self._entered = True
            self.buy(quantity=1.0, tag="entry")
        elif self.position.is_open and not self._exited:
            self._exited = True
            self.sell(quantity=1.0, tag="exit")


class NeverFilledLimitStrategy(Strategy):
    placed_history: ClassVar[list[bool]] = []

    def init(self) -> None:
        self._placed = False

    def on_bar(self, bar) -> None:
        if not self._placed:
            self._placed = True
            self.buy(
                quantity=1.0,
                order_type="limit",
                limit_price=96.0,
                tag="never-fill",
            )
        type(self).placed_history.append(self._placed)


class GapCrossedBuyLimitStrategy(Strategy):
    def init(self) -> None:
        self._placed = False

    def on_bar(self, bar) -> None:
        if not self._placed:
            self._placed = True
            self.buy(
                quantity=1.0,
                order_type="limit",
                limit_price=100.0,
                tag="gap-crossed-entry",
            )


class MarketableBuyLimitStrategy(Strategy):
    def init(self) -> None:
        self._placed = False

    def on_bar(self, bar) -> None:
        if not self._placed:
            self._placed = True
            self.buy(
                quantity=1.0,
                order_type="limit",
                limit_price=130.0,
                tag="marketable-limit-entry",
            )


class IntrabarTouchedBuyLimitStrategy(Strategy):
    def init(self) -> None:
        self._placed = False

    def on_bar(self, bar) -> None:
        if not self._placed:
            self._placed = True
            self.buy(
                quantity=1.0,
                order_type="limit",
                limit_price=109.0,
                tag="intrabar-touch-entry",
            )


class StopMarketGapAboveBuyStrategy(Strategy):
    def init(self) -> None:
        self._placed = False

    def on_bar(self, bar) -> None:
        if not self._placed:
            self._placed = True
            self.buy(
                quantity=1.0,
                order_type="stop_market",
                stop_price=110.0,
                tag="gap-above-stop-entry",
            )


class StopMarketGapBelowBuyStrategy(Strategy):
    def init(self) -> None:
        self._placed = False

    def on_bar(self, bar) -> None:
        if not self._placed:
            self._placed = True
            self.buy(
                quantity=1.0,
                order_type="stop_market",
                stop_price=90.0,
                tag="gap-below-stop-entry",
            )


class StopMarketIntrabarAboveBuyStrategy(Strategy):
    def init(self) -> None:
        self._placed = False

    def on_bar(self, bar) -> None:
        if not self._placed:
            self._placed = True
            self.buy(
                quantity=1.0,
                order_type="stop_market",
                stop_price=110.0,
                tag="intrabar-above-stop-entry",
            )


class StopMarketIntrabarBelowBuyStrategy(Strategy):
    def init(self) -> None:
        self._placed = False

    def on_bar(self, bar) -> None:
        if not self._placed:
            self._placed = True
            self.buy(
                quantity=1.0,
                order_type="stop_market",
                stop_price=90.0,
                tag="intrabar-below-stop-entry",
            )


class StopMarketGapAboveSellStrategy(Strategy):
    def init(self) -> None:
        self._seen_bars = 0

    def on_bar(self, bar) -> None:
        self._seen_bars += 1
        if self._seen_bars == 1:
            self.buy(quantity=1.0, tag="entry")
        elif self._seen_bars == 2 and self.position.is_open:
            self.sell(
                quantity=1.0,
                order_type="stop_market",
                stop_price=115.0,
                tag="gap-above-stop-exit",
            )


class StopMarketGapBelowSellStrategy(Strategy):
    def init(self) -> None:
        self._seen_bars = 0

    def on_bar(self, bar) -> None:
        self._seen_bars += 1
        if self._seen_bars == 1:
            self.buy(quantity=1.0, tag="entry")
        elif self._seen_bars == 2 and self.position.is_open:
            self.sell(
                quantity=1.0,
                order_type="stop_market",
                stop_price=95.0,
                tag="gap-below-stop-exit",
            )


class StopMarketIntrabarAboveSellStrategy(Strategy):
    def init(self) -> None:
        self._seen_bars = 0

    def on_bar(self, bar) -> None:
        self._seen_bars += 1
        if self._seen_bars == 1:
            self.buy(quantity=1.0, tag="entry")
        elif self._seen_bars == 2 and self.position.is_open:
            self.sell(
                quantity=1.0,
                order_type="stop_market",
                stop_price=115.0,
                tag="intrabar-above-stop-exit",
            )


class StopMarketIntrabarBelowSellStrategy(Strategy):
    def init(self) -> None:
        self._seen_bars = 0

    def on_bar(self, bar) -> None:
        self._seen_bars += 1
        if self._seen_bars == 1:
            self.buy(quantity=1.0, tag="entry")
        elif self._seen_bars == 2 and self.position.is_open:
            self.sell(
                quantity=1.0,
                order_type="stop_market",
                stop_price=95.0,
                tag="intrabar-below-stop-exit",
            )


class StopMarketSellWhileFlatStrategy(Strategy):
    def on_bar(self, bar) -> None:
        self.sell(
            quantity=1.0,
            order_type="stop_market",
            stop_price=95.0,
            tag="flat-stop-exit-ignored",
        )


class StopLimitConfig(StrategyConfig):
    stop_price: float = 105.0
    limit_price: float = 106.0


class BuyStopLimitStrategy(Strategy[StopLimitConfig]):
    def init(self) -> None:
        self._placed = False

    def on_bar(self, bar) -> None:
        if not self._placed:
            self._placed = True
            self.buy(
                quantity=1.0,
                order_type="stop_limit",
                stop_price=self.config.stop_price,
                limit_price=self.config.limit_price,
                tag="stop-limit-entry",
            )


class SellStopLimitStrategy(Strategy[StopLimitConfig]):
    def init(self) -> None:
        self._seen_bars = 0

    def on_bar(self, bar) -> None:
        self._seen_bars += 1
        if self._seen_bars == 1:
            self.buy(quantity=1.0, tag="entry")
        elif self._seen_bars == 2 and self.position.is_open:
            self.sell(
                quantity=1.0,
                order_type="stop_limit",
                stop_price=self.config.stop_price,
                limit_price=self.config.limit_price,
                tag="stop-limit-exit",
            )


class MultipleStopMarketEntriesStrategy(Strategy):
    def init(self) -> None:
        self._placed = False

    def on_bar(self, bar) -> None:
        if not self._placed:
            self._placed = True
            self.buy(
                quantity=1.0,
                order_type="stop_market",
                stop_price=105.0,
                tag="older-stop-entry",
            )
            self.buy(
                quantity=1.0,
                order_type="stop_market",
                stop_price=110.0,
                tag="newer-stop-entry",
            )


class OlderLimitThenTriggeredStopExitStrategy(Strategy):
    def init(self) -> None:
        self._seen_bars = 0

    def on_bar(self, bar) -> None:
        self._seen_bars += 1
        if self._seen_bars == 1:
            self.buy(quantity=2.0, tag="entry")
        elif self._seen_bars == 2:
            self.sell(
                quantity=1.0,
                order_type="limit",
                limit_price=115.0,
                tag="older-limit-exit",
            )
        elif self._seen_bars == 3 and self.position.is_open:
            self.sell(
                quantity=1.0,
                order_type="stop_market",
                stop_price=115.0,
                tag="newer-stop-exit",
            )


class OlderLimitThenNewerMarketExitStrategy(Strategy):
    def init(self) -> None:
        self._seen_bars = 0

    def on_bar(self, bar) -> None:
        self._seen_bars += 1
        if self._seen_bars == 1:
            self.buy(quantity=2.0, tag="entry")
        elif self._seen_bars == 2:
            self.sell(
                quantity=1.0,
                order_type="limit",
                limit_price=115.0,
                tag="older-limit-exit",
            )
        elif self._seen_bars == 3:
            self.sell(quantity=1.0, tag="newer-market-exit")


class RepeatedExitSignalsStrategy(Strategy):
    def init(self) -> None:
        self._seen_bars = 0

    def on_bar(self, bar) -> None:
        self._seen_bars += 1
        if self._seen_bars == 1:
            self.sell(quantity=1.0, tag="flat-exit-ignored")
        elif self._seen_bars == 2:
            self.buy(quantity=1.0, tag="entry")
        elif self._seen_bars in (3, 4):
            self.sell(quantity=1.0, tag="exit")


class SellWhileFlatStrategy(Strategy):
    def on_bar(self, bar) -> None:
        self.sell(quantity=1.0, tag="flat-exit-ignored")


class PositionViewProbeStrategy(Strategy):
    position_snapshots: ClassVar[list[tuple[bool, float, float]]] = []

    def init(self) -> None:
        self._seen_bars = 0
        type(self).position_snapshots.clear()

    def on_bar(self, bar) -> None:
        self._seen_bars += 1
        type(self).position_snapshots.append(
            (
                self.position.is_open,
                self.position.quantity,
                self.position.average_entry_price,
            )
        )
        if self._seen_bars == 1:
            self.buy(quantity=2.0, tag="entry")
        elif self._seen_bars == 2:
            self.buy(quantity=1.0, tag="increase")
        elif self._seen_bars == 3:
            self.sell(quantity=1.0, tag="partial-exit")
        elif self._seen_bars == 4:
            self.sell(quantity=2.0, tag="full-exit")


class ReusedStrategyInstanceProbe(Strategy):
    def on_bar(self, bar) -> None:
        observed_bars = len(self.data.close)
        if observed_bars == 1:
            self.buy(quantity=1.0, tag="entry")
        elif observed_bars == 2 and self.position.is_open:
            self.sell(quantity=1.0, tag="exit")


class FakeExchangeClient:
    def __init__(self, *, pages: list[list[list[float]]]) -> None:
        self.pages = pages[:]

    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        since: int | None = None,
        limit: int | None = None,
        params: dict[str, object] | None = None,
    ) -> list[list[float]]:
        del symbol, timeframe, since, limit, params
        if self.pages:
            return self.pages.pop(0)
        return []


class InMemoryBarSeriesSource:
    def load(self) -> BarSeries:
        return fixture_bar_series()


class InMemoryDuckTypedSource:
    def load(self) -> object:
        return type(
            "DuckBars",
            (),
            {
                "symbol": "BTC/USDT",
                "timeframe": "1m",
                "bar_type": "time",
                "rows": fixture_rows(),
            },
        )()


def fixture_rows() -> tuple[TimeBar, ...]:
    fixture_path = Path(__file__).with_name("fixtures") / "backtest_ohlcv_fixture.json"
    payload = json.loads(fixture_path.read_text())
    return tuple(TimeBar(**row) for row in payload)


def make_bar_series(
    rows: tuple[TimeBar, ...],
    *,
    symbol: str = "BTC/USDT",
    timeframe: str = "1m",
) -> BarSeries:
    return BarSeries(
        symbol=symbol,
        timeframe=timeframe,
        bar_type="time",
        rows=rows,
    )


def stop_market_gap_below_sell_rows() -> tuple[TimeBar, ...]:
    return (
        TimeBar(timestamp=60, open=100.0, high=104.0, low=96.0, close=104.0, volume=10.0),
        TimeBar(timestamp=120, open=105.0, high=108.0, low=103.0, close=106.0, volume=12.0),
        TimeBar(timestamp=180, open=90.0, high=92.0, low=88.0, close=91.0, volume=14.0),
    )


def fixture_bar_series() -> BarSeries:
    return make_bar_series(fixture_rows())


def fixture_dataframe_records() -> list[dict[str, object]]:
    return [
        {
            "timestamp": datetime.fromtimestamp(row.timestamp / 1000, tz=UTC).isoformat(),
            "open": row.open,
            "high": row.high,
            "low": row.low,
            "close": row.close,
            "volume": row.volume,
        }
        for row in fixture_rows()
    ]


def run_engine_backtest(
    *,
    bars: BarSeries,
    strategy: type[Strategy[StrategyConfig]],
    config: StrategyConfig | None = None,
    initial_cash: float = 1_000.0,
    costs: CostConfig | None = None,
) -> BacktestResult:
    used_costs = costs or CostConfig(tick_size=1.0, slippage_ticks=1.0, fee_rate=0.001)
    return BacktestEngine(initial_cash=initial_cash, costs=used_costs).run(
        bars=bars,
        strategy=strategy,
        config=config,
    )


def run_engine_backtest_from_source(
    *,
    source: object,
    strategy: type[Strategy[StrategyConfig]],
    config: StrategyConfig | None = None,
    initial_cash: float = 1_000.0,
    costs: CostConfig | None = None,
) -> BacktestResult:
    used_costs = costs or CostConfig(tick_size=1.0, slippage_ticks=1.0, fee_rate=0.001)
    return BacktestEngine(initial_cash=initial_cash, costs=used_costs).run(
        source=source,
        strategy=strategy,
        config=config,
    )
