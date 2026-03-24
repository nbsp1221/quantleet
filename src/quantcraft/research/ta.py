from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, Generic, Protocol, TypeVar


class _SeriesLike(Protocol):
    def __getitem__(self, index: int) -> float: ...

    def __len__(self) -> int: ...

    @property
    def latest(self) -> float: ...

    @property
    def is_empty(self) -> bool: ...


_VersionKey = TypeVar("_VersionKey")
_ComputedValue = TypeVar("_ComputedValue")


class _MemoizedValue(Generic[_VersionKey, _ComputedValue]):
    __slots__ = ("_cached_key", "_cached_value", "_compute", "_version")

    def __init__(
        self,
        *,
        version: Callable[[], _VersionKey],
        compute: Callable[[], _ComputedValue],
    ) -> None:
        self._version = version
        self._compute = compute
        self._cached_key: _VersionKey | None = None
        self._cached_value: _ComputedValue | None = None

    def get(self) -> _ComputedValue:
        key = self._version()
        if self._cached_key != key or self._cached_value is None:
            self._cached_key = key
            self._cached_value = self._compute()
        return self._cached_value


class _ComputedSeriesView:
    __slots__ = ("_values",)

    def __init__(
        self,
        *,
        version: Callable[[], object],
        compute: Callable[[], tuple[float, ...]],
    ) -> None:
        self._values = _MemoizedValue(version=version, compute=compute)

    def __getitem__(self, index: int) -> float:
        if index < 0:
            raise ValueError("computed series does not allow negative indices")
        values = self._values.get()
        if index >= len(values):
            return math.nan
        return values[-(index + 1)]

    def __len__(self) -> int:
        return len(self._values.get())

    @property
    def latest(self) -> float:
        return self[0]

    @property
    def is_empty(self) -> bool:
        return len(self) == 0


@dataclass(frozen=True, slots=True)
class BollingerBandsResult:
    upper: _ComputedSeriesView
    middle: _ComputedSeriesView
    lower: _ComputedSeriesView


@dataclass(frozen=True, slots=True)
class MACDResult:
    macd: _ComputedSeriesView
    signal: _ComputedSeriesView
    histogram: _ComputedSeriesView


def sma(series: _SeriesLike, length: int = 20) -> _ComputedSeriesView:
    _validate_length(length)
    return _ComputedSeriesView(
        version=lambda: len(series),
        compute=lambda: _compute_sma(_series_values(series), length),
    )


def ema(series: _SeriesLike, length: int = 20) -> _ComputedSeriesView:
    _validate_length(length)
    return _ComputedSeriesView(
        version=lambda: len(series),
        compute=lambda: _compute_ema(_series_values(series), length),
    )


def rsi(series: _SeriesLike, length: int = 14) -> _ComputedSeriesView:
    _validate_length(length)
    return _ComputedSeriesView(
        version=lambda: len(series),
        compute=lambda: _compute_rsi(_series_values(series), length),
    )


def atr(
    high: _SeriesLike,
    low: _SeriesLike,
    close: _SeriesLike,
    length: int = 14,
) -> _ComputedSeriesView:
    _validate_length(length)
    return _ComputedSeriesView(
        version=lambda: (len(high), len(low), len(close)),
        compute=lambda: _compute_atr(
            highs=_series_values(high),
            lows=_series_values(low),
            closes=_series_values(close),
            length=length,
        )
    )


def cci(
    high: _SeriesLike,
    low: _SeriesLike,
    close: _SeriesLike,
    length: int = 20,
) -> _ComputedSeriesView:
    _validate_length(length)
    return _ComputedSeriesView(
        version=lambda: (len(high), len(low), len(close)),
        compute=lambda: _compute_cci(
            highs=_series_values(high),
            lows=_series_values(low),
            closes=_series_values(close),
            length=length,
        )
    )


def bollinger_bands(
    series: _SeriesLike,
    length: int = 20,
    stddev: int | float = 2,
) -> BollingerBandsResult:
    _validate_length(length)
    bundle = _MemoizedValue(
        version=lambda: len(series),
        compute=lambda: _compute_bollinger(
            _series_values(series),
            length=length,
            stddev=float(stddev),
        ),
    )

    def compute(index: int) -> tuple[float, ...]:
        return bundle.get()[index]

    return BollingerBandsResult(
        upper=_ComputedSeriesView(version=lambda: len(series), compute=lambda: compute(0)),
        middle=_ComputedSeriesView(version=lambda: len(series), compute=lambda: compute(1)),
        lower=_ComputedSeriesView(version=lambda: len(series), compute=lambda: compute(2)),
    )


def macd(
    series: _SeriesLike,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> MACDResult:
    _validate_length(fast)
    _validate_length(slow)
    _validate_length(signal)
    bundle = _MemoizedValue(
        version=lambda: len(series),
        compute=lambda: _compute_macd(
            _series_values(series),
            fast=fast,
            slow=slow,
            signal=signal,
        ),
    )
    return MACDResult(
        macd=_ComputedSeriesView(
            version=lambda: len(series),
            compute=lambda: bundle.get()[0],
        ),
        signal=_ComputedSeriesView(
            version=lambda: len(series),
            compute=lambda: bundle.get()[1],
        ),
        histogram=_ComputedSeriesView(
            version=lambda: len(series),
            compute=lambda: bundle.get()[2],
        ),
    )


def _validate_length(length: int) -> None:
    if length <= 0:
        raise ValueError("length must be positive")


def _series_values(series: _SeriesLike) -> tuple[float, ...]:
    return tuple(series[index] for index in range(len(series) - 1, -1, -1))


def _compute_sma(values: tuple[float, ...], length: int) -> tuple[float, ...]:
    results: list[float] = []
    for end in range(len(values)):
        if end + 1 < length:
            results.append(math.nan)
            continue
        window = values[end - length + 1 : end + 1]
        results.append(sum(window) / length)
    return tuple(results)


def _compute_ema(values: tuple[float, ...], length: int) -> tuple[float, ...]:
    if not values:
        return ()
    alpha = 2.0 / (length + 1.0)
    results: list[float] = []
    ema_value = values[0]
    for value in values:
        ema_value = (value * alpha) + (ema_value * (1.0 - alpha))
        results.append(ema_value)
    return tuple(results)


def _compute_rsi(values: tuple[float, ...], length: int) -> tuple[float, ...]:
    if not values:
        return ()
    gains = [0.0]
    losses = [0.0]
    for previous, current in zip(values, values[1:]):
        delta = current - previous
        gains.append(max(delta, 0.0))
        losses.append(max(-delta, 0.0))

    results: list[float] = []
    for end in range(len(values)):
        if end < length:
            results.append(math.nan)
            continue
        avg_gain = sum(gains[end - length + 1 : end + 1]) / length
        avg_loss = sum(losses[end - length + 1 : end + 1]) / length
        if avg_loss == 0.0:
            results.append(100.0)
            continue
        rs = avg_gain / avg_loss
        results.append(100.0 - (100.0 / (1.0 + rs)))
    return tuple(results)


def _compute_atr(
    *,
    highs: tuple[float, ...],
    lows: tuple[float, ...],
    closes: tuple[float, ...],
    length: int,
) -> tuple[float, ...]:
    true_ranges: list[float] = []
    for index, (high, low) in enumerate(zip(highs, lows)):
        if index == 0:
            true_ranges.append(high - low)
            continue
        previous_close = closes[index - 1]
        true_ranges.append(max(high - low, abs(high - previous_close), abs(low - previous_close)))
    return _compute_sma(tuple(true_ranges), length)


def _compute_cci(
    *,
    highs: tuple[float, ...],
    lows: tuple[float, ...],
    closes: tuple[float, ...],
    length: int,
) -> tuple[float, ...]:
    typical_prices = tuple(
        (high + low + close) / 3.0 for high, low, close in zip(highs, lows, closes)
    )
    results: list[float] = []
    for end in range(len(typical_prices)):
        if end + 1 < length:
            results.append(math.nan)
            continue
        window = typical_prices[end - length + 1 : end + 1]
        sma_value = sum(window) / length
        mean_deviation = sum(abs(value - sma_value) for value in window) / length
        if mean_deviation == 0.0:
            results.append(0.0)
            continue
        results.append((typical_prices[end] - sma_value) / (0.015 * mean_deviation))
    return tuple(results)


def _compute_bollinger(
    values: tuple[float, ...],
    *,
    length: int,
    stddev: float,
) -> tuple[tuple[float, ...], tuple[float, ...], tuple[float, ...]]:
    upper: list[float] = []
    middle: list[float] = []
    lower: list[float] = []
    for end in range(len(values)):
        if end + 1 < length:
            upper.append(math.nan)
            middle.append(math.nan)
            lower.append(math.nan)
            continue
        window = values[end - length + 1 : end + 1]
        mean = sum(window) / length
        variance = sum((value - mean) ** 2 for value in window) / length
        deviation = math.sqrt(variance)
        middle.append(mean)
        upper.append(mean + (stddev * deviation))
        lower.append(mean - (stddev * deviation))
    return tuple(upper), tuple(middle), tuple(lower)


def _compute_macd(
    values: tuple[float, ...],
    *,
    fast: int,
    slow: int,
    signal: int,
) -> tuple[tuple[float, ...], tuple[float, ...], tuple[float, ...]]:
    fast_values = _compute_ema(values, fast)
    slow_values = _compute_ema(values, slow)
    macd_values = tuple(
        fast_value - slow_value for fast_value, slow_value in zip(fast_values, slow_values)
    )
    signal_values = _compute_ema(macd_values, signal)
    histogram_values = tuple(
        macd_value - signal_value for macd_value, signal_value in zip(macd_values, signal_values)
    )
    return macd_values, signal_values, histogram_values


__all__ = [
    "BollingerBandsResult",
    "MACDResult",
    "atr",
    "bollinger_bands",
    "cci",
    "ema",
    "macd",
    "rsi",
    "sma",
]
