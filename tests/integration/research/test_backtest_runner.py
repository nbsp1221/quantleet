from __future__ import annotations

import json
from pathlib import Path

from quantcraft.data import OHLCVBar
from quantcraft.research.application.backtest import (
    BacktestResult,
    BacktestSummary,
    ExposureSummary,
    run_backtest,
)
from quantcraft.research.application.strategy import Strategy
from quantcraft.trading.domain.costs import CostConfig
from quantcraft.trading.domain.events import FillEvent
from quantcraft.trading.domain.state import TradingState


class DeterministicEntryExitStrategy(Strategy):
    def __init__(self) -> None:
        super().__init__()
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
    def __init__(self) -> None:
        super().__init__()
        self._entered = False

    def on_bar(self, bar) -> None:
        if not self._entered:
            self._entered = True
            self.buy(symbol=bar.symbol, quantity=1.0, tag="entry")


class NeverFilledLimitStrategy(Strategy):
    def __init__(self) -> None:
        super().__init__()
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
    def __init__(self) -> None:
        super().__init__()
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


def test_backtest_runner_produces_deterministic_trade_log_and_summary() -> None:
    fixture_path = Path(__file__).with_name("fixtures") / "backtest_ohlcv_fixture.json"
    payload = json.loads(fixture_path.read_text())
    rows = tuple(OHLCVBar(**row) for row in payload)

    result = run_backtest(
        symbol="BTC/USDT",
        bar_type="time",
        bar_spec="1m",
        rows=rows,
        strategy=DeterministicEntryExitStrategy(),
        initial_cash=1_000.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=1.0, fee_rate=0.001),
    )

    assert result == BacktestResult(
        trade_log=(
            FillEvent(
                symbol="BTC/USDT",
                side="buy",
                quantity=1.0,
                price=111.0,
                timestamp=120,
                fee=0.111,
            ),
            FillEvent(
                symbol="BTC/USDT",
                side="sell",
                quantity=1.0,
                price=115.0,
                timestamp=180,
                fee=0.115,
            ),
        ),
        equity_curve=(1000.0, 997.889, 1003.774),
        final_state=TradingState(
            cash=1003.774,
            position_quantity=0.0,
            average_entry_price=0.0,
            realized_pnl=4.0,
            unrealized_pnl=0.0,
            equity=1003.774,
        ),
        summary=BacktestSummary(
            total_trades=2,
            total_fees=0.226,
            final_balance=1003.774,
            final_equity=1003.774,
            total_return=0.003774,
            max_drawdown=0.002111,
            realized_pnl=4.0,
            unrealized_pnl=0.0,
            win_rate=1.0,
            average_win=4.0,
            average_loss=0.0,
            profit_factor=float("inf"),
            exposure=ExposureSummary(
                bars_in_position=1,
                total_bars=3,
                exposure_ratio=1 / 3,
            ),
        ),
    )
    assert result.trade_log
    assert result.final_state.position_quantity == 0.0
    assert result.summary.trade_count == 2
    assert result.summary.ending_equity == 1003.774


def test_backtest_runner_exposes_expanded_research_result_surface() -> None:
    fixture_path = Path(__file__).with_name("fixtures") / "backtest_ohlcv_fixture.json"
    payload = json.loads(fixture_path.read_text())
    rows = tuple(OHLCVBar(**row) for row in payload)

    result = run_backtest(
        symbol="BTC/USDT",
        bar_type="time",
        bar_spec="1m",
        rows=rows,
        strategy=DeterministicEntryExitStrategy(),
        initial_cash=1_000.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=1.0, fee_rate=0.001),
    )

    assert result.equity_curve == (1000.0, 997.889, 1003.774)
    assert result.summary.final_balance == 1003.774
    assert result.summary.final_equity == 1003.774
    assert result.summary.total_return == 0.003774
    assert result.summary.max_drawdown == 0.002111
    assert result.summary.total_trades == 2
    assert result.summary.win_rate == 1.0
    assert result.summary.average_win == 4.0
    assert result.summary.average_loss == 0.0
    assert result.summary.profit_factor == float("inf")
    assert result.summary.exposure.bars_in_position == 1
    assert result.summary.exposure.total_bars == 3
    assert result.summary.exposure.exposure_ratio == 1 / 3


def test_backtest_runner_uses_tick_path_not_bar_only_fills() -> None:
    fixture_path = Path(__file__).with_name("fixtures") / "backtest_ohlcv_fixture.json"
    payload = json.loads(fixture_path.read_text())
    rows = tuple(OHLCVBar(**row) for row in payload)

    result = run_backtest(
        symbol="BTC/USDT",
        bar_type="time",
        bar_spec="1m",
        rows=rows,
        strategy=DeterministicEntryExitStrategy(),
        initial_cash=1_000.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=1.0, fee_rate=0.001),
    )

    assert tuple(fill.timestamp for fill in result.trade_log) == (120, 180)
    assert tuple(fill.price for fill in result.trade_log) == (111.0, 115.0)


def test_backtest_runner_activates_bar_orders_on_the_next_bar() -> None:
    fixture_path = Path(__file__).with_name("fixtures") / "backtest_ohlcv_fixture.json"
    payload = json.loads(fixture_path.read_text())
    rows = tuple(OHLCVBar(**row) for row in payload)

    strategy = BuyAndHoldStrategy()

    result = run_backtest(
        symbol="BTC/USDT",
        bar_type="time",
        bar_spec="1m",
        rows=rows,
        strategy=strategy,
        initial_cash=1_000.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=1.0, fee_rate=0.001),
    )

    assert tuple(fill.timestamp for fill in result.trade_log) == (120,)
    assert result.trade_log[0].price == 111.0
    assert result.final_state.position_quantity == 1.0
    assert result.summary.trade_count == 1
    assert result.summary.ending_equity == 1002.889
    assert result.summary.unrealized_pnl == 3.0
    assert result.equity_curve == (1000.0, 997.889, 1002.889)


def test_backtest_runner_marks_open_positions_to_latest_market_state() -> None:
    fixture_path = Path(__file__).with_name("fixtures") / "backtest_ohlcv_fixture.json"
    payload = json.loads(fixture_path.read_text())
    rows = tuple(OHLCVBar(**row) for row in payload)

    result = run_backtest(
        symbol="BTC/USDT",
        bar_type="time",
        bar_spec="1m",
        rows=rows,
        strategy=BuyAndHoldStrategy(),
        initial_cash=1_000.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=1.0, fee_rate=0.001),
    )

    assert result.final_state == TradingState(
        cash=888.889,
        position_quantity=1.0,
        average_entry_price=111.0,
        realized_pnl=0.0,
        unrealized_pnl=3.0,
        equity=1002.889,
    )
    assert result.summary == BacktestSummary(
        total_trades=1,
        total_fees=0.111,
        final_balance=888.889,
        final_equity=1002.889,
        total_return=0.002889,
        max_drawdown=0.002111,
        realized_pnl=0.0,
        unrealized_pnl=3.0,
        win_rate=0.0,
        average_win=0.0,
        average_loss=0.0,
        profit_factor=0.0,
        exposure=ExposureSummary(
            bars_in_position=2,
            total_bars=3,
            exposure_ratio=2 / 3,
        ),
    )


def test_unfilled_limit_order_carries_without_creating_trade_log_entries() -> None:
    fixture_path = Path(__file__).with_name("fixtures") / "backtest_ohlcv_fixture.json"
    payload = json.loads(fixture_path.read_text())
    rows = tuple(OHLCVBar(**row) for row in payload)

    strategy = NeverFilledLimitStrategy()

    result = run_backtest(
        symbol="BTC/USDT",
        bar_type="time",
        bar_spec="1m",
        rows=rows,
        strategy=strategy,
        initial_cash=1_000.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=1.0, fee_rate=0.001),
    )

    assert result.trade_log == ()
    assert result.final_state == TradingState(
        cash=1_000.0,
        position_quantity=0.0,
        average_entry_price=0.0,
        realized_pnl=0.0,
        unrealized_pnl=0.0,
        equity=1_000.0,
    )
    assert strategy._placed is True


def test_backtest_runner_preserves_older_active_intents_ahead_of_newly_activated_ones() -> None:
    rows = (
        OHLCVBar(timestamp=60, open=100.0, high=105.0, low=95.0, close=104.0, volume=10.0),
        OHLCVBar(timestamp=120, open=110.0, high=112.0, low=108.0, close=109.0, volume=12.0),
        OHLCVBar(timestamp=180, open=109.0, high=114.0, low=107.0, close=113.0, volume=14.0),
        OHLCVBar(timestamp=240, open=115.0, high=116.0, low=114.0, close=115.0, volume=15.0),
    )

    result = run_backtest(
        symbol="BTC/USDT",
        bar_type="time",
        bar_spec="1m",
        rows=rows,
        strategy=OlderLimitThenNewerMarketExitStrategy(),
        initial_cash=1_000.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=1.0, fee_rate=0.001),
    )

    assert tuple((fill.side, fill.price, fill.timestamp) for fill in result.trade_log) == (
        ("buy", 111.0, 120),
        ("sell", 115.0, 240),
        ("sell", 114.0, 240),
    )
