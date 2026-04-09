from __future__ import annotations

from typing import Protocol

from .indicators.pure import (
    atr as pure_atr,
)
from .indicators.pure import (
    bb as pure_bb,
)
from .indicators.pure import (
    cci as pure_cci,
)
from .indicators.pure import (
    ema as pure_ema,
)
from .indicators.pure import (
    macd as pure_macd,
)
from .indicators.pure import (
    rsi as pure_rsi,
)
from .indicators.pure import (
    sma as pure_sma,
)
from .indicators.pure.bb import PureBollingerBandsResult as BollingerBandsResult
from .indicators.pure.macd import PureMACDResult as MACDResult
from .indicators.runtime import (
    SeriesLike,
    bind_indicator_from_pure,
    bind_multi_output_indicator_from_pure,
)


class _IndicatorView(Protocol):
    def __getitem__(self, index: int) -> float: ...

    def __len__(self) -> int: ...

    @property
    def latest(self) -> float: ...

    @property
    def is_empty(self) -> bool: ...


def sma(series: SeriesLike, length: int = 20) -> _IndicatorView:
    _validate_length(length)
    return bind_indicator_from_pure(
        sources=(series,),
        compute=lambda values: pure_sma(values, length=length),
    )


def ema(series: SeriesLike, length: int = 20) -> _IndicatorView:
    _validate_length(length)
    return bind_indicator_from_pure(
        sources=(series,),
        compute=lambda values: pure_ema(values, length=length),
    )


def rsi(series: SeriesLike, length: int = 14) -> _IndicatorView:
    _validate_length(length)
    return bind_indicator_from_pure(
        sources=(series,),
        compute=lambda values: pure_rsi(values, length=length),
    )


def atr(
    high: SeriesLike,
    low: SeriesLike,
    close: SeriesLike,
    length: int = 14,
) -> _IndicatorView:
    _validate_length(length)
    return bind_indicator_from_pure(
        sources=(high, low, close),
        compute=lambda source_high, source_low, source_close: pure_atr(
            source_high,
            source_low,
            source_close,
            length=length,
        ),
    )


def cci(
    high: SeriesLike,
    low: SeriesLike,
    close: SeriesLike,
    length: int = 20,
) -> _IndicatorView:
    _validate_length(length)
    return bind_indicator_from_pure(
        sources=(high, low, close),
        compute=lambda source_high, source_low, source_close: pure_cci(
            source_high,
            source_low,
            source_close,
            length=length,
        ),
    )


def bb(
    series: SeriesLike,
    length: int = 20,
    stddev: int | float = 2,
) -> BollingerBandsResult[_IndicatorView]:
    _validate_length(length)
    return bind_multi_output_indicator_from_pure(
        sources=(series,),
        compute=lambda values: pure_bb(values, length=length, stddev=stddev),
        result_type=BollingerBandsResult,
        field_names=("upper", "middle", "lower"),
    )


def macd(
    series: SeriesLike,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> MACDResult[_IndicatorView]:
    _validate_length(fast)
    _validate_length(slow)
    _validate_length(signal)
    return bind_multi_output_indicator_from_pure(
        sources=(series,),
        compute=lambda values: pure_macd(values, fast=fast, slow=slow, signal=signal),
        result_type=MACDResult,
        field_names=("macd", "signal", "histogram"),
    )


def _validate_length(length: int) -> None:
    if length <= 0:
        raise ValueError("length must be positive")


__all__ = [
    "BollingerBandsResult",
    "MACDResult",
    "atr",
    "bb",
    "cci",
    "ema",
    "macd",
    "rsi",
    "sma",
]
