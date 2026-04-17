from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from quantcraft.backtest import BacktestEngine, BacktestResult
from quantcraft.data import BarSeries, TimeBar
from quantcraft.research import Strategy
from quantcraft.trading.domain.costs import CostConfig


class DeterministicEntryExitStrategy(Strategy):
    def init(self) -> None:
        self._seen_bars = 0

    def on_bar(self, bar) -> None:
        self._seen_bars += 1
        if self._seen_bars == 1:
            self.buy(symbol=bar.symbol, quantity=1.0, tag="entry")
        elif self._seen_bars == 2:
            self.sell(
                symbol=bar.symbol,
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
            self.buy(symbol=bar.symbol, quantity=1.0, tag="entry")


class NeverFilledLimitStrategy(Strategy):
    def __init__(self) -> None:
        super().__init__()
        self._placed = False

    def init(self) -> None:
        self._placed = False

    def on_bar(self, bar) -> None:
        if not self._placed:
            self._placed = True
            self.buy(
                symbol=bar.symbol,
                quantity=1.0,
                order_type="limit",
                limit_price=96.0,
                tag="never-fill",
            )


class OlderLimitThenNewerMarketExitStrategy(Strategy):
    def init(self) -> None:
        self._seen_bars = 0

    def on_bar(self, bar) -> None:
        self._seen_bars += 1
        if self._seen_bars == 1:
            self.buy(symbol=bar.symbol, quantity=2.0, tag="entry")
        elif self._seen_bars == 2:
            self.sell(
                symbol=bar.symbol,
                quantity=1.0,
                order_type="limit",
                limit_price=115.0,
                tag="older-limit-exit",
            )
        elif self._seen_bars == 3:
            self.sell(symbol=bar.symbol, quantity=1.0, tag="newer-market-exit")


class RepeatedExitSignalsStrategy(Strategy):
    def init(self) -> None:
        self._seen_bars = 0

    def on_bar(self, bar) -> None:
        self._seen_bars += 1
        if self._seen_bars == 1:
            self.sell(symbol=bar.symbol, quantity=1.0, tag="flat-exit-ignored")
        elif self._seen_bars == 2:
            self.buy(symbol=bar.symbol, quantity=1.0, tag="entry")
        elif self._seen_bars in (3, 4):
            self.sell(symbol=bar.symbol, quantity=1.0, tag="exit")


class SellWhileFlatStrategy(Strategy):
    def on_bar(self, bar) -> None:
        self.sell(symbol=bar.symbol, quantity=1.0, tag="flat-exit-ignored")


class PositionViewProbeStrategy(Strategy):
    def __init__(self) -> None:
        super().__init__()
        self.position_snapshots: list[tuple[bool, float, float]] = []

    def init(self) -> None:
        self._seen_bars = 0
        self.position_snapshots.clear()

    def on_bar(self, bar) -> None:
        self._seen_bars += 1
        self.position_snapshots.append(
            (
                self.position.is_open,
                self.position.quantity,
                self.position.average_entry_price,
            )
        )
        if self._seen_bars == 1:
            self.buy(symbol=bar.symbol, quantity=2.0, tag="entry")
        elif self._seen_bars == 2:
            self.buy(symbol=bar.symbol, quantity=1.0, tag="increase")
        elif self._seen_bars == 3:
            self.sell(symbol=bar.symbol, quantity=1.0, tag="partial-exit")
        elif self._seen_bars == 4:
            self.sell(symbol=bar.symbol, quantity=2.0, tag="full-exit")


class ReusedStrategyInstanceProbe(Strategy):
    def on_bar(self, bar) -> None:
        observed_bars = len(self.data.close)
        if observed_bars == 1:
            self.buy(symbol=bar.symbol, quantity=1.0, tag="entry")
        elif observed_bars == 2 and self.position.is_open:
            self.sell(symbol=bar.symbol, quantity=1.0, tag="exit")


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
    strategy: Strategy,
    initial_cash: float = 1_000.0,
    costs: CostConfig | None = None,
) -> BacktestResult:
    used_costs = costs or CostConfig(tick_size=1.0, slippage_ticks=1.0, fee_rate=0.001)
    return BacktestEngine(initial_cash=initial_cash, costs=used_costs).run(
        bars=bars,
        strategy=strategy,
    )


def run_engine_backtest_from_source(
    *,
    source: object,
    strategy: Strategy,
    initial_cash: float = 1_000.0,
    costs: CostConfig | None = None,
) -> BacktestResult:
    used_costs = costs or CostConfig(tick_size=1.0, slippage_ticks=1.0, fee_rate=0.001)
    return BacktestEngine(initial_cash=initial_cash, costs=used_costs).run(
        source=source,
        strategy=strategy,
    )
