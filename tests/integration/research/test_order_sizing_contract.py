from __future__ import annotations

import pytest

from quantleet.backtest import BacktestEngine, BacktestSummary, ExposureSummary
from quantleet.data import TimeBar
from quantleet.research import Strategy, qc, ta
from quantleet.trading.domain.costs import CostConfig
from tests.integration.research.support_backtest_runner import make_bar_series, run_engine_backtest
from tests.support_backtest import (
    canonical_trade_log_digest,
    canonical_trade_log_samples,
    load_canonical_bars,
)


class BuyHalfBudgetStrategy(Strategy):
    def on_bar(self, bar) -> None:
        if len(self.data.close) == 1:
            self.buy(qty_percent=50.0, tag="half-budget")


class BuyAllAffordableBudgetStrategy(Strategy):
    def on_bar(self, bar) -> None:
        if len(self.data.close) == 1:
            self.buy(qty_percent=100.0, tag="max-budget")


class BuyThenScaleOutStrategy(Strategy):
    def on_bar(self, bar) -> None:
        visible = len(self.data.close)
        if visible == 1:
            self.buy(qty_percent=100.0, tag="entry")
        elif visible == 2 and self.position.is_open:
            self.sell(qty_percent=30.0, tag="scale-out")


class SequentialPercentEntriesStrategy(Strategy):
    def on_bar(self, bar) -> None:
        if len(self.data.close) == 1:
            self.buy(qty_percent=50.0, tag="first-half")
            self.buy(qty_percent=50.0, tag="second-half")


class LimitPercentBudgetStrategy(Strategy):
    def on_bar(self, bar) -> None:
        if len(self.data.close) == 1:
            self.buy(
                qty_percent=100.0,
                order_type="limit",
                limit_price=20.0,
                tag="limit-budget",
            )


class CanonicalPercentMarketStrategy(Strategy):
    def init(self) -> None:
        self.rsi = ta.rsi(self.data.close, length=14)

    def on_bar(self, bar) -> None:
        if qc.is_na(self.rsi[0]):
            return
        if (not self.position.is_open) and self.rsi[0] < 30:
            self.buy(qty_percent=50.0)
        elif self.position.is_open and self.rsi[0] > 70:
            self.sell(qty_percent=100.0)


class CanonicalPercentLimitEntryStrategy(Strategy):
    def init(self) -> None:
        self.ema = ta.ema(self.data.close, length=20)
        self._entry_pending = False

    def on_bar(self, bar) -> None:
        if qc.is_na(self.ema[0]) or qc.is_na(self.ema[1]):
            return
        if self.position.is_open:
            self._entry_pending = False
            if self.data.close[0] < self.ema[0]:
                self.sell(qty_percent=100.0)
            return
        if self._entry_pending:
            return
        if self.ema[0] > self.ema[1] and self.data.close[0] > self.ema[0] * 1.01:
            self.buy(
                qty_percent=50.0,
                order_type="limit",
                limit_price=float(self.ema[0]),
            )
            self._entry_pending = True


class CanonicalPercentLimitExitStrategy(Strategy):
    def init(self) -> None:
        self.rsi = ta.rsi(self.data.close, length=14)
        self._exit_pending = False

    def on_bar(self, bar) -> None:
        if qc.is_na(self.rsi[0]):
            return
        if self.position.is_open:
            if not self._exit_pending:
                self.sell(
                    qty_percent=100.0,
                    order_type="limit",
                    limit_price=float(self.position.average_entry_price * 1.02),
                )
                self._exit_pending = True
            return
        self._exit_pending = False
        if self.rsi[0] < 30:
            self.buy(qty_percent=50.0)


def _run_canonical_percent_backtest(strategy: Strategy):
    engine = BacktestEngine(
        initial_cash=1_000_000.0,
        costs=CostConfig(tick_size=0.1, slippage_ticks=1.0, fee_rate=0.0004),
    )
    return engine.run(bars=load_canonical_bars(), strategy=strategy)


def test_backtest_buy_qty_percent_preserves_requested_budget_when_affordable() -> None:
    rows = (
        TimeBar(timestamp=60, open=8.0, high=9.0, low=7.0, close=8.5, volume=10.0),
        TimeBar(timestamp=120, open=10.0, high=11.0, low=9.0, close=10.5, volume=10.0),
    )

    result = run_engine_backtest(
        bars=make_bar_series(rows),
        strategy=BuyHalfBudgetStrategy(),
        initial_cash=80.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.01),
    )

    assert len(result.trade_log) == 1
    assert result.trade_log[0].quantity == 4.0
    assert result.trade_log[0].price == 10.0


def test_backtest_buy_qty_percent_clamps_when_full_budget_plus_fees_is_unaffordable() -> None:
    rows = (
        TimeBar(timestamp=60, open=8.0, high=9.0, low=7.0, close=8.5, volume=10.0),
        TimeBar(timestamp=120, open=10.0, high=11.0, low=9.0, close=10.5, volume=10.0),
    )

    result = run_engine_backtest(
        bars=make_bar_series(rows),
        strategy=BuyAllAffordableBudgetStrategy(),
        initial_cash=80.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.01),
    )

    assert len(result.trade_log) == 1
    assert result.trade_log[0].quantity == pytest.approx(80.0 / 10.1)


def test_backtest_sell_qty_percent_scales_out_of_current_position() -> None:
    rows = (
        TimeBar(timestamp=60, open=8.0, high=9.0, low=7.0, close=8.5, volume=10.0),
        TimeBar(timestamp=120, open=10.0, high=11.0, low=9.0, close=10.5, volume=10.0),
        TimeBar(timestamp=180, open=12.0, high=13.0, low=11.0, close=12.5, volume=10.0),
    )

    result = run_engine_backtest(
        bars=make_bar_series(rows),
        strategy=BuyThenScaleOutStrategy(),
        initial_cash=100.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
    )

    assert tuple((fill.side, fill.quantity) for fill in result.trade_log) == (
        ("buy", 10.0),
        ("sell", 3.0),
    )
    assert result.final_state.position_quantity == 7.0


def test_backtest_same_cycle_percent_entries_resolve_sequentially() -> None:
    rows = (
        TimeBar(timestamp=60, open=8.0, high=9.0, low=7.0, close=8.5, volume=10.0),
        TimeBar(timestamp=120, open=10.0, high=11.0, low=9.0, close=10.5, volume=10.0),
    )

    result = run_engine_backtest(
        bars=make_bar_series(rows),
        strategy=SequentialPercentEntriesStrategy(),
        initial_cash=100.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
    )

    assert tuple(
        (fill.tag if hasattr(fill, "tag") else None, fill.quantity) for fill in result.trade_log
    ) == (
        (None, 5.0),
        (None, 2.5),
    )
    assert result.final_state.position_quantity == 7.5


def test_limit_buy_qty_percent_uses_limit_price_as_affordability_anchor() -> None:
    rows = (
        TimeBar(timestamp=60, open=8.0, high=9.0, low=7.0, close=8.5, volume=10.0),
        TimeBar(timestamp=120, open=10.0, high=11.0, low=9.0, close=10.5, volume=10.0),
    )

    result = run_engine_backtest(
        bars=make_bar_series(rows),
        strategy=LimitPercentBudgetStrategy(),
        initial_cash=100.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
    )

    assert len(result.trade_log) == 1
    assert result.trade_log[0].quantity == 5.0
    assert result.trade_log[0].price == 10.0


def test_canonical_percent_market_backtest_matches_btc_fixture_result_contract() -> None:
    result = _run_canonical_percent_backtest(CanonicalPercentMarketStrategy())

    assert result.summary == BacktestSummary(
        total_trades=34,
        total_fills=68,
        total_fees=pytest.approx(15016.378191945156),
        final_balance=pytest.approx(1_071_114.3412848383),
        final_equity=pytest.approx(1_071_114.3412848383),
        total_return=pytest.approx(0.071114341285),
        max_drawdown=pytest.approx(0.179663475086),
        realized_pnl=pytest.approx(86_130.71947678244),
        unrealized_pnl=0.0,
        win_rate=pytest.approx(0.647058823529),
        average_win=pytest.approx(14365.481255762985),
        average_loss=pytest.approx(20410.520528495697),
        profit_factor=pytest.approx(1.290350023107),
        exposure=ExposureSummary(
            bars_in_position=4504,
            total_bars=8760,
            exposure_ratio=pytest.approx(0.5141552511415525),
        ),
    )

    first_fills, last_fills = canonical_trade_log_samples(result.trade_log)
    assert first_fills == (
        {
            "timestamp": 1736265600000,
            "side": "buy",
            "quantity": 5.106443821458,
            "price": 97915.5,
            "fee": 199.999999999988,
        },
        {
            "timestamp": 1736848800000,
            "side": "sell",
            "quantity": 5.106443821458,
            "price": 97129.79999999999,
            "fee": 198.39514683578,
        },
        {
            "timestamp": 1737334800000,
            "side": "buy",
            "quantity": 4.989443036469,
            "price": 99769.6,
            "fee": 199.117894388519,
        },
        {
            "timestamp": 1738184400000,
            "side": "sell",
            "quantity": 4.989443036469,
            "price": 104155.29999999999,
            "fee": 207.870774518536,
        },
        {
            "timestamp": 1738357200000,
            "side": "buy",
            "quantity": 5.002895708303,
            "price": 101647.6,
            "fee": 203.41293671972,
        },
    )
    assert last_fills == (
        {
            "timestamp": 1765490400000,
            "side": "sell",
            "quantity": 5.806361419145,
            "price": 92823.5,
            "fee": 215.586715676002,
        },
        {
            "timestamp": 1765713600000,
            "side": "buy",
            "quantity": 5.941853960699,
            "price": 89308.40000000001,
            "fee": 212.262988105476,
        },
        {
            "timestamp": 1765983600000,
            "side": "sell",
            "quantity": 5.941853960699,
            "price": 89633.90000000001,
            "fee": 213.036617491159,
        },
        {
            "timestamp": 1766502000000,
            "side": "buy",
            "quantity": 6.119626671868,
            "price": 86837.3,
            "fee": 212.564742877201,
        },
        {
            "timestamp": 1766970000000,
            "side": "sell",
            "quantity": 6.119626671868,
            "price": 88262.09999999999,
            "fee": 216.052440510032,
        },
    )
    assert canonical_trade_log_digest(result.trade_log) == (
        "b5ef0c390ec2168696bac49ae5fb1fb7f7b20306ea6fce5cf9c4cc297fe1781f"
    )


def test_canonical_percent_limit_entry_backtest_matches_btc_fixture_result_contract() -> None:
    result = _run_canonical_percent_backtest(CanonicalPercentLimitEntryStrategy())

    assert result.summary == BacktestSummary(
        total_trades=29,
        total_fills=58,
        total_fees=pytest.approx(11632.217051315038),
        final_balance=pytest.approx(1_001_510.1769165891),
        final_equity=pytest.approx(1_001_510.1769165891),
        total_return=pytest.approx(0.001510176917),
        max_drawdown=pytest.approx(0.012844629121),
        realized_pnl=pytest.approx(13142.393967904727),
        unrealized_pnl=0.0,
        win_rate=pytest.approx(0.448275862069),
        average_win=pytest.approx(2685.230927916542),
        average_loss=pytest.approx(2087.364071645335),
        profit_factor=pytest.approx(1.045217822118),
        exposure=ExposureSummary(
            bars_in_position=45,
            total_bars=8760,
            exposure_ratio=pytest.approx(0.005136986301369863),
        ),
    )

    first_fills, last_fills = canonical_trade_log_samples(result.trade_log)
    assert first_fills == (
        {
            "timestamp": 1736334000000,
            "side": "buy",
            "quantity": 5.286790662828,
            "price": 94575.3353760541,
            "fee": 199.99999999998,
        },
        {
            "timestamp": 1736337600000,
            "side": "sell",
            "quantity": 5.286790662828,
            "price": 95093.7,
            "fee": 201.096194101507,
        },
        {
            "timestamp": 1736514000000,
            "side": "buy",
            "quantity": 5.36174995167,
            "price": 93471.29184450864,
            "fee": 200.467877811931,
        },
        {
            "timestamp": 1736517600000,
            "side": "sell",
            "quantity": 5.36174995167,
            "price": 93522.0,
            "fee": 200.576631592033,
        },
        {
            "timestamp": 1736564400000,
            "side": "buy",
            "quantity": 5.324499895928,
            "price": 94113.08560330409,
            "fee": 200.442045800102,
        },
    )
    assert last_fills == (
        {
            "timestamp": 1744045200000,
            "side": "sell",
            "quantity": 6.445282237129,
            "price": 77394.7,
            "fee": 199.532274063171,
        },
        {
            "timestamp": 1744052400000,
            "side": "buy",
            "quantity": 6.410380081874,
            "price": 78106.8499729574,
            "fee": 200.277838129827,
        },
        {
            "timestamp": 1744056000000,
            "side": "sell",
            "quantity": 6.410380081874,
            "price": 78093.59999999999,
            "fee": 200.243863184734,
        },
        {
            "timestamp": 1744124400000,
            "side": "buy",
            "quantity": 6.39128669077,
            "price": 78302.20893005375,
            "fee": 200.180746317018,
        },
        {
            "timestamp": 1744128000000,
            "side": "sell",
            "quantity": 6.39128669077,
            "price": 78459.79999999999,
            "fee": 200.58363020019,
        },
    )
    assert canonical_trade_log_digest(result.trade_log) == (
        "61f854df38edab1cda9b75445b7ef9accd3bafe58e275cd5ac0f8576ad1627a6"
    )


def test_canonical_percent_limit_exit_backtest_matches_btc_fixture_result_contract() -> None:
    result = _run_canonical_percent_backtest(CanonicalPercentLimitExitStrategy())

    assert result.summary == BacktestSummary(
        total_trades=13,
        total_fills=27,
        total_fees=pytest.approx(5791.726401979646),
        final_balance=pytest.approx(565868.251108661),
        final_equity=pytest.approx(985626.9879311735),
        total_return=pytest.approx(-0.014373012069),
        max_drawdown=pytest.approx(0.152385228789),
        realized_pnl=pytest.approx(137754.66649470356),
        unrealized_pnl=pytest.approx(-146335.95216154994),
        win_rate=pytest.approx(1.0),
        average_win=pytest.approx(10168.413689870582),
        average_loss=0.0,
        profit_factor=float("inf"),
        exposure=ExposureSummary(
            bars_in_position=7013,
            total_bars=8760,
            exposure_ratio=pytest.approx(0.8005707762557077),
        ),
    )

    first_fills, last_fills = canonical_trade_log_samples(result.trade_log)
    assert first_fills == (
        {
            "timestamp": 1736265600000,
            "side": "buy",
            "quantity": 5.106443821458,
            "price": 97915.5,
            "fee": 199.999999999988,
        },
        {
            "timestamp": 1736967600000,
            "side": "sell",
            "quantity": 5.106443821458,
            "price": 99873.81,
            "fee": 203.999999999988,
        },
        {
            "timestamp": 1737334800000,
            "side": "buy",
            "quantity": 5.05963740458,
            "price": 99769.6,
            "fee": 201.919199999994,
        },
        {
            "timestamp": 1737338400000,
            "side": "sell",
            "quantity": 5.05963740458,
            "price": 101764.99200000001,
            "fee": 205.957583999994,
        },
        {
            "timestamp": 1737936000000,
            "side": "buy",
            "quantity": 4.969203828857,
            "price": 102560.1,
            "fee": 203.856816643183,
        },
    )
    assert last_fills == (
        {
            "timestamp": 1755176400000,
            "side": "buy",
            "quantity": 4.674077223086,
            "price": 118822.30000000002,
            "fee": 222.153842409877,
        },
        {
            "timestamp": 1759503600000,
            "side": "sell",
            "quantity": 4.674077223086,
            "price": 121198.746,
            "fee": 226.596919258074,
        },
        {
            "timestamp": 1759856400000,
            "side": "buy",
            "quantity": 4.610312770698,
            "price": 121621.7,
            "fee": 224.2856306816,
        },
        {
            "timestamp": 1759942800000,
            "side": "sell",
            "quantity": 4.610312770698,
            "price": 124054.134,
            "fee": 228.771343295232,
        },
        {
            "timestamp": 1760115600000,
            "side": "buy",
            "quantity": 4.791317899723,
            "price": 118150.1,
            "fee": 226.437875593625,
        },
    )
    assert canonical_trade_log_digest(result.trade_log) == (
        "6819316d5fda53a5a3aa076da11e90002d63079412a220d4fb608c6f084e6cd8"
    )
