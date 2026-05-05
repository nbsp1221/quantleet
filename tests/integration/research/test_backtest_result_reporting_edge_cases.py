from __future__ import annotations

from quantleet.backtest import BacktestEngine
from quantleet.data import BarSeries, TimeBar
from quantleet.research import Strategy
from quantleet.trading.domain.costs import CostConfig
from quantleet.trading.domain.events import BarEvent


def _bars() -> BarSeries:
    return BarSeries(
        symbol="BTC/USDT",
        timeframe="1m",
        bar_type="time",
        rows=(
            TimeBar(timestamp=60, open=100.0, high=100.0, low=100.0, close=100.0, volume=1.0),
            TimeBar(timestamp=120, open=100.0, high=100.0, low=100.0, close=100.0, volume=1.0),
            TimeBar(timestamp=180, open=105.0, high=105.0, low=105.0, close=105.0, volume=1.0),
        ),
    )


class BuyThenExitStrategy(Strategy):
    def on_bar(self, bar: BarEvent) -> None:
        if len(self.data.close) == 1:
            self.buy(quantity=1.0, tag="entry")
        elif self.position.is_open:
            self.sell(quantity=1.0, tag="exit")


class UnaffordableBuyStrategy(Strategy):
    def on_bar(self, bar: BarEvent) -> None:
        if len(self.data.close) == 1:
            self.buy(quantity=100.0, tag="too-large")


def test_report_exposure_counts_intrabar_position_even_when_flat_at_close() -> None:
    result = BacktestEngine(
        initial_cash=1_000.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
    ).run(
        bars=_bars(),
        strategy=BuyThenExitStrategy(),
    )

    assert result.final_state.position_quantity == 0.0
    assert result.report.exposure.ending_state == "flat"
    assert result.report.exposure.final_position_quantity == 0.0
    assert result.report.exposure.final_average_entry_price is None
    assert result.report.exposure.bars_in_position == 2
    assert result.report.exposure.total_bars == 3
    assert result.report.exposure.exposure_ratio == 2 / 3


def test_report_exposes_order_rejections_separately_from_fills() -> None:
    result = BacktestEngine(
        initial_cash=1_000.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
    ).run(
        bars=_bars(),
        strategy=UnaffordableBuyStrategy(),
    )

    assert result.trade_log == ()
    assert result.report.fills == ()
    assert len(result.report.order_rejections) == 1
    rejection = result.report.order_rejections[0]
    assert rejection.symbol == "BTC/USDT"
    assert rejection.side == "buy"
    assert rejection.order_type == "market"
    assert rejection.reason in {"insufficient_cash", "execution_affordability"}
    assert rejection.tag == "too-large"
    assert result.report.execution.order_rejection_count == 1
