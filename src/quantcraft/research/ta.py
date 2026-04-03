from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from ._indicator_kernels import (
    _AtrKernel,
    _BollingerKernel,
    _CciKernel,
    _EmaKernel,
    _MacdKernel,
    _RsiKernel,
    _SmaKernel,
)
from ._indicator_runtime import _IndicatorRuntime, _SeriesLike


class _IndicatorView(Protocol):
    def __getitem__(self, index: int) -> float: ...

    def __len__(self) -> int: ...

    @property
    def latest(self) -> float: ...

    @property
    def is_empty(self) -> bool: ...


@dataclass(frozen=True, slots=True)
class BollingerBandsResult:
    upper: _IndicatorView
    middle: _IndicatorView
    lower: _IndicatorView


@dataclass(frozen=True, slots=True)
class MACDResult:
    macd: _IndicatorView
    signal: _IndicatorView
    histogram: _IndicatorView


def sma(series: _SeriesLike, length: int = 20) -> _IndicatorView:
    _validate_length(length)
    return _IndicatorRuntime(sources=(series,), kernel=_SmaKernel(length)).view()


def ema(series: _SeriesLike, length: int = 20) -> _IndicatorView:
    _validate_length(length)
    return _IndicatorRuntime(sources=(series,), kernel=_EmaKernel(length)).view()


def rsi(series: _SeriesLike, length: int = 14) -> _IndicatorView:
    _validate_length(length)
    return _IndicatorRuntime(sources=(series,), kernel=_RsiKernel(length)).view()


def atr(
    high: _SeriesLike,
    low: _SeriesLike,
    close: _SeriesLike,
    length: int = 14,
) -> _IndicatorView:
    _validate_length(length)
    return _IndicatorRuntime(
        sources=(high, low, close),
        kernel=_AtrKernel(length),
    ).view()


def cci(
    high: _SeriesLike,
    low: _SeriesLike,
    close: _SeriesLike,
    length: int = 20,
) -> _IndicatorView:
    _validate_length(length)
    return _IndicatorRuntime(
        sources=(high, low, close),
        kernel=_CciKernel(length),
    ).view()


def bollinger_bands(
    series: _SeriesLike,
    length: int = 20,
    stddev: int | float = 2,
) -> BollingerBandsResult:
    _validate_length(length)
    runtime = _IndicatorRuntime(
        sources=(series,),
        kernel=_BollingerKernel(length=length, stddev=float(stddev)),
    )

    return BollingerBandsResult(
        upper=runtime.view(0),
        middle=runtime.view(1),
        lower=runtime.view(2),
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
    runtime = _IndicatorRuntime(
        sources=(series,),
        kernel=_MacdKernel(fast=fast, slow=slow, signal=signal),
    )
    return MACDResult(
        macd=runtime.view(0),
        signal=runtime.view(1),
        histogram=runtime.view(2),
    )


def _validate_length(length: int) -> None:
    if length <= 0:
        raise ValueError("length must be positive")


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
