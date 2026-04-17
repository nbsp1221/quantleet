from __future__ import annotations

import inspect
import math

import pytest

from quantcraft.backtest.strategy_runtime import _StrategyDriver
from quantcraft.data import BarSeries, TimeBar
from quantcraft.research import qc, ta
from quantcraft.research.series import SeriesView
from quantcraft.research.strategy import Strategy
from quantcraft.trading.domain.events import BarEvent

_LEGACY_BB_NAME = "bollinger" + "_bands"


def test_qc_helpers_support_crossovers_and_na_checks() -> None:
    fast = SeriesView((1.0, 2.0, 4.0))
    slow = SeriesView((2.0, 2.0, 3.0))

    assert qc.is_na(math.nan) is True
    assert qc.is_na(1.0) is False
    assert qc.crossover(fast, slow) is True
    assert qc.crossunder(slow, fast) is True
    assert qc.crossover(fast, 3.5) is True
    assert qc.crossunder(3.5, fast) is True


def test_indicator_signatures_match_the_approved_contract() -> None:
    assert tuple(inspect.signature(ta.sma).parameters) == ("series", "length")
    assert tuple(inspect.signature(ta.ema).parameters) == ("series", "length")
    assert tuple(inspect.signature(ta.rsi).parameters) == ("series", "length")
    assert tuple(inspect.signature(ta.atr).parameters) == ("high", "low", "close", "length")
    assert tuple(inspect.signature(ta.cci).parameters) == ("high", "low", "close", "length")
    assert tuple(inspect.signature(ta.bb).parameters) == ("series", "length", "stddev")
    assert tuple(inspect.signature(ta.macd).parameters) == ("series", "fast", "slow", "signal")
    assert not hasattr(ta, _LEGACY_BB_NAME)


def test_sma_and_ema_are_live_causal_views_with_talib_warmup() -> None:
    closes = SeriesView((1.0, 2.0, 3.0, 4.0, 5.0))

    sma = ta.sma(closes, length=3)
    ema = ta.ema(closes, length=3)

    assert sma[0] == 4.0
    assert sma[1] == 3.0
    assert qc.is_na(sma[3])
    assert ema[0] == pytest.approx(4.0)
    assert ema[1] == pytest.approx(3.0)
    assert ema[2] == pytest.approx(2.0)
    assert qc.is_na(ema[3])


def test_rsi_atr_and_cci_follow_talib_fixture_behavior() -> None:
    closes = SeriesView((1.0, 2.0, 3.0, 4.0, 5.0))
    highs = SeriesView((2.0, 3.0, 4.0, 5.0, 6.0))
    lows = SeriesView((0.5, 1.0, 2.0, 3.0, 4.0))

    rsi = ta.rsi(closes, length=3)
    atr = ta.atr(highs, lows, closes, length=3)
    cci = ta.cci(highs, lows, closes, length=3)

    assert rsi[0] == pytest.approx(100.0)
    assert rsi[1] == pytest.approx(100.0)
    assert qc.is_na(rsi[2])
    assert atr[0] == pytest.approx(2.0)
    assert atr[1] == pytest.approx(2.0)
    assert qc.is_na(atr[2])
    assert cci[0] == pytest.approx(100.0)
    assert cci[1] == pytest.approx(100.0)
    assert cci[2] == pytest.approx(100.0)


def test_multi_output_indicators_return_named_result_objects_with_bb_contract() -> None:
    closes = SeriesView((1.0, 2.0, 3.0, 4.0, 5.0))

    bands = ta.bb(closes, length=3, stddev=2)
    macd = ta.macd(closes, fast=2, slow=3, signal=2)

    assert hasattr(bands, "middle")
    assert hasattr(bands, "upper")
    assert hasattr(bands, "lower")
    assert hasattr(macd, "macd")
    assert hasattr(macd, "signal")
    assert hasattr(macd, "histogram")

    assert bands.middle[0] == pytest.approx(4.0)
    assert bands.upper[0] == pytest.approx(5.632993161855453)
    assert bands.lower[0] == pytest.approx(2.3670068381445466)
    assert macd.macd[0] == pytest.approx(0.5)
    assert macd.signal[0] == pytest.approx(0.5)
    assert macd.histogram[0] == pytest.approx(0.0)
    assert qc.is_na(macd.macd[2])


class CountingSeries:
    def __init__(self, values: tuple[float, ...]) -> None:
        self._values = values
        self.read_count = 0

    def __getitem__(self, index: int) -> float:
        self.read_count += 1
        if index < 0:
            raise ValueError("negative indices are not supported")
        if index >= len(self._values):
            return math.nan
        return self._values[-(index + 1)]

    def __len__(self) -> int:
        return len(self._values)

    @property
    def latest(self) -> float:
        return self[0]

    @property
    def is_empty(self) -> bool:
        return not self._values


def test_indicator_reads_are_memoized_for_a_stable_series_length() -> None:
    series = CountingSeries((1.0, 2.0, 3.0, 4.0, 5.0))

    sma = ta.sma(series, length=3)
    bands = ta.bb(series, length=3, stddev=2)

    assert sma[0] == 4.0
    first_read_count = series.read_count
    assert sma[0] == 4.0
    assert series.read_count == first_read_count

    _ = bands.upper[0]
    band_read_count = series.read_count
    _ = bands.middle[0]
    _ = bands.lower[0]
    assert series.read_count == band_read_count


class RecordsIndicatorBindingsStrategy(Strategy):
    def __init__(self) -> None:
        super().__init__()
        self.bound_close = None
        self.fast = None
        self.slow = None
        self.crossed = None

    def init(self) -> None:
        self.bound_close = self.data.close
        self.fast = ta.sma(self.data.close, length=2)
        self.slow = ta.sma(self.data.close, length=3)

    def on_bar(self, bar: BarEvent) -> None:
        self.crossed = qc.crossover(self.fast, self.slow)


def test_indicator_bindings_from_init_stay_live_as_bars_arrive() -> None:
    strategy = RecordsIndicatorBindingsStrategy()
    runtime = _StrategyDriver(strategy)
    runtime.initialize()

    bars = (
        BarEvent(
            bar_type="time",
            bar_spec="1m",
            symbol="BTC/USDT",
            timestamp=60,
            open=5.0,
            high=5.0,
            low=5.0,
            close=5.0,
            volume=1.0,
            is_closed=True,
        ),
        BarEvent(
            bar_type="time",
            bar_spec="1m",
            symbol="BTC/USDT",
            timestamp=120,
            open=4.0,
            high=4.0,
            low=4.0,
            close=4.0,
            volume=1.0,
            is_closed=True,
        ),
        BarEvent(
            bar_type="time",
            bar_spec="1m",
            symbol="BTC/USDT",
            timestamp=180,
            open=1.0,
            high=1.0,
            low=1.0,
            close=1.0,
            volume=1.0,
            is_closed=True,
        ),
        BarEvent(
            bar_type="time",
            bar_spec="1m",
            symbol="BTC/USDT",
            timestamp=240,
            open=10.0,
            high=10.0,
            low=10.0,
            close=10.0,
            volume=1.0,
            is_closed=True,
        ),
    )

    runtime.handle_bar(bars[0])
    runtime.handle_bar(bars[1])
    assert strategy.bound_close is strategy.data.close
    assert qc.is_na(strategy.slow[0])

    runtime.handle_bar(bars[2])
    assert strategy.fast[0] == pytest.approx(2.5)
    assert strategy.slow[0] == pytest.approx((5.0 + 4.0 + 1.0) / 3.0)
    assert strategy.crossed is False

    runtime.handle_bar(bars[3])
    assert strategy.bound_close is strategy.data.close
    assert strategy.fast[0] == pytest.approx(5.5)
    assert strategy.slow[0] == pytest.approx(5.0)
    assert strategy.crossed is True


def test_indicator_bindings_work_when_backtest_history_is_preloaded_before_init() -> None:
    strategy = RecordsIndicatorBindingsStrategy()
    runtime = _StrategyDriver(strategy)
    bars = BarSeries(
        symbol="BTC/USDT",
        timeframe="1m",
        bar_type="time",
        rows=(
            TimeBar(
                timestamp=60,
                open=5.0,
                high=5.0,
                low=5.0,
                close=5.0,
                volume=1.0,
            ),
            TimeBar(
                timestamp=120,
                open=4.0,
                high=4.0,
                low=4.0,
                close=4.0,
                volume=1.0,
            ),
            TimeBar(
                timestamp=180,
                open=1.0,
                high=1.0,
                low=1.0,
                close=1.0,
                volume=1.0,
            ),
        ),
    )

    runtime.initialize(bars=bars)

    assert strategy.bound_close is strategy.data.close
    assert strategy.bound_close.is_empty is True
    assert qc.is_na(strategy.fast[0])
    assert qc.is_na(strategy.slow[0])

    runtime.handle_bar(
        BarEvent(
            bar_type="time",
            bar_spec="1m",
            symbol="BTC/USDT",
            timestamp=60,
            open=5.0,
            high=5.0,
            low=5.0,
            close=5.0,
            volume=1.0,
            is_closed=True,
        )
    )
    assert qc.is_na(strategy.fast[0])
    assert qc.is_na(strategy.slow[0])

    runtime.handle_bar(
        BarEvent(
            bar_type="time",
            bar_spec="1m",
            symbol="BTC/USDT",
            timestamp=120,
            open=4.0,
            high=4.0,
            low=4.0,
            close=4.0,
            volume=1.0,
            is_closed=True,
        )
    )
    assert strategy.fast[0] == pytest.approx(4.5)
    assert qc.is_na(strategy.slow[0])

    runtime.handle_bar(
        BarEvent(
            bar_type="time",
            bar_spec="1m",
            symbol="BTC/USDT",
            timestamp=180,
            open=1.0,
            high=1.0,
            low=1.0,
            close=1.0,
            volume=1.0,
            is_closed=True,
        )
    )
    assert strategy.fast[0] == pytest.approx(2.5)
    assert strategy.slow[0] == pytest.approx((5.0 + 4.0 + 1.0) / 3.0)
