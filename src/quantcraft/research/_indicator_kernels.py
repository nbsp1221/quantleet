from __future__ import annotations

import math
from collections import deque
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Callable, TypeVar

_State = TypeVar("_State")


def _replay_rows(
    state: _State,
    rows: Iterable[tuple[float, ...]],
    append: Callable[[_State, tuple[float, ...]], None],
) -> _State:
    for values in rows:
        append(state, values)
    return state


@dataclass(slots=True)
class _SmaState:
    outputs: tuple[list[float], ...] = field(default_factory=lambda: ([],))
    window: deque[float] = field(default_factory=deque)
    total: float = 0.0


class _SmaKernel:
    def __init__(self, length: int) -> None:
        self._length = length

    def build(self, sources: tuple[tuple[float, ...], ...]) -> _SmaState:
        return _replay_rows(_SmaState(), ((value,) for value in sources[0]), self.append)

    def append(self, state: _SmaState, values: tuple[float, ...]) -> None:
        value = values[0]
        if len(state.window) == self._length:
            state.total -= state.window.popleft()
        state.window.append(value)
        state.total += value
        if len(state.window) < self._length:
            state.outputs[0].append(math.nan)
            return
        state.outputs[0].append(state.total / self._length)

@dataclass(slots=True)
class _EmaState:
    outputs: tuple[list[float], ...] = field(default_factory=lambda: ([],))
    ema_value: float | None = None


class _EmaKernel:
    def __init__(self, length: int) -> None:
        self._alpha = 2.0 / (length + 1.0)

    def build(self, sources: tuple[tuple[float, ...], ...]) -> _EmaState:
        return _replay_rows(_EmaState(), ((value,) for value in sources[0]), self.append)

    def append(self, state: _EmaState, values: tuple[float, ...]) -> None:
        value = values[0]
        if state.ema_value is None:
            state.ema_value = value
        else:
            state.ema_value = (value * self._alpha) + (state.ema_value * (1.0 - self._alpha))
        state.outputs[0].append(state.ema_value)

@dataclass(slots=True)
class _RsiState:
    outputs: tuple[list[float], ...] = field(default_factory=lambda: ([],))
    previous_value: float | None = None
    gains: deque[float] = field(default_factory=deque)
    losses: deque[float] = field(default_factory=deque)
    gain_total: float = 0.0
    loss_total: float = 0.0


class _RsiKernel:
    def __init__(self, length: int) -> None:
        self._length = length

    def build(self, sources: tuple[tuple[float, ...], ...]) -> _RsiState:
        return _replay_rows(_RsiState(), ((value,) for value in sources[0]), self.append)

    def append(self, state: _RsiState, values: tuple[float, ...]) -> None:
        value = values[0]
        if state.previous_value is None:
            gain = 0.0
            loss = 0.0
        else:
            delta = value - state.previous_value
            gain = max(delta, 0.0)
            loss = max(-delta, 0.0)
        if len(state.gains) == self._length:
            state.gain_total -= state.gains.popleft()
            state.loss_total -= state.losses.popleft()
        state.gains.append(gain)
        state.losses.append(loss)
        state.gain_total += gain
        state.loss_total += loss
        index = len(state.outputs[0])
        if index < self._length:
            state.outputs[0].append(math.nan)
        elif state.loss_total == 0.0:
            state.outputs[0].append(100.0)
        else:
            rs = (state.gain_total / self._length) / (state.loss_total / self._length)
            state.outputs[0].append(100.0 - (100.0 / (1.0 + rs)))
        state.previous_value = value

@dataclass(slots=True)
class _AtrState:
    outputs: tuple[list[float], ...] = field(default_factory=lambda: ([],))
    previous_close: float | None = None
    true_ranges: deque[float] = field(default_factory=deque)
    total_true_range: float = 0.0


class _AtrKernel:
    def __init__(self, length: int) -> None:
        self._length = length

    def build(self, sources: tuple[tuple[float, ...], ...]) -> _AtrState:
        return _replay_rows(_AtrState(), zip(*sources), self.append)

    def append(self, state: _AtrState, values: tuple[float, ...]) -> None:
        high, low, close = values
        if state.previous_close is None:
            true_range = high - low
        else:
            true_range = max(
                high - low,
                abs(high - state.previous_close),
                abs(low - state.previous_close),
            )
        if len(state.true_ranges) == self._length:
            state.total_true_range -= state.true_ranges.popleft()
        state.true_ranges.append(true_range)
        state.total_true_range += true_range
        if len(state.true_ranges) < self._length:
            state.outputs[0].append(math.nan)
        else:
            state.outputs[0].append(state.total_true_range / self._length)
        state.previous_close = close

@dataclass(slots=True)
class _CciState:
    outputs: tuple[list[float], ...] = field(default_factory=lambda: ([],))
    typical_prices: deque[float] = field(default_factory=deque)


class _CciKernel:
    def __init__(self, length: int) -> None:
        self._length = length

    def build(self, sources: tuple[tuple[float, ...], ...]) -> _CciState:
        return _replay_rows(_CciState(), zip(*sources), self.append)

    def append(self, state: _CciState, values: tuple[float, ...]) -> None:
        high, low, close = values
        typical_price = (high + low + close) / 3.0
        if len(state.typical_prices) == self._length:
            state.typical_prices.popleft()
        state.typical_prices.append(typical_price)
        if len(state.typical_prices) < self._length:
            state.outputs[0].append(math.nan)
            return
        window = tuple(state.typical_prices)
        sma_value = sum(window) / self._length
        mean_deviation = sum(abs(value - sma_value) for value in window) / self._length
        if mean_deviation == 0.0:
            state.outputs[0].append(0.0)
            return
        state.outputs[0].append((typical_price - sma_value) / (0.015 * mean_deviation))

@dataclass(slots=True)
class _BollingerState:
    outputs: tuple[list[float], ...] = field(default_factory=lambda: ([], [], []))
    window: deque[float] = field(default_factory=deque)
    total: float = 0.0
    total_squares: float = 0.0


class _BollingerKernel:
    def __init__(self, length: int, stddev: float) -> None:
        self._length = length
        self._stddev = stddev

    def build(self, sources: tuple[tuple[float, ...], ...]) -> _BollingerState:
        return _replay_rows(
            _BollingerState(),
            ((value,) for value in sources[0]),
            self.append,
        )

    def append(self, state: _BollingerState, values: tuple[float, ...]) -> None:
        value = values[0]
        if len(state.window) == self._length:
            removed = state.window.popleft()
            state.total -= removed
            state.total_squares -= removed * removed
        state.window.append(value)
        state.total += value
        state.total_squares += value * value
        if len(state.window) < self._length:
            state.outputs[0].append(math.nan)
            state.outputs[1].append(math.nan)
            state.outputs[2].append(math.nan)
            return
        mean = state.total / self._length
        variance = max((state.total_squares / self._length) - (mean * mean), 0.0)
        deviation = math.sqrt(variance)
        state.outputs[0].append(mean + (self._stddev * deviation))
        state.outputs[1].append(mean)
        state.outputs[2].append(mean - (self._stddev * deviation))

@dataclass(slots=True)
class _MacdState:
    outputs: tuple[list[float], ...] = field(default_factory=lambda: ([], [], []))
    fast_ema: float | None = None
    slow_ema: float | None = None
    signal_ema: float | None = None


class _MacdKernel:
    def __init__(self, fast: int, slow: int, signal: int) -> None:
        self._fast_alpha = 2.0 / (fast + 1.0)
        self._slow_alpha = 2.0 / (slow + 1.0)
        self._signal_alpha = 2.0 / (signal + 1.0)

    def build(self, sources: tuple[tuple[float, ...], ...]) -> _MacdState:
        return _replay_rows(_MacdState(), ((value,) for value in sources[0]), self.append)

    def append(self, state: _MacdState, values: tuple[float, ...]) -> None:
        value = values[0]
        if state.fast_ema is None:
            state.fast_ema = value
        else:
            state.fast_ema = (value * self._fast_alpha) + (
                state.fast_ema * (1.0 - self._fast_alpha)
            )
        if state.slow_ema is None:
            state.slow_ema = value
        else:
            state.slow_ema = (value * self._slow_alpha) + (
                state.slow_ema * (1.0 - self._slow_alpha)
            )
        macd_value = state.fast_ema - state.slow_ema
        if state.signal_ema is None:
            state.signal_ema = macd_value
        else:
            state.signal_ema = (macd_value * self._signal_alpha) + (
                state.signal_ema * (1.0 - self._signal_alpha)
            )
        histogram_value = macd_value - state.signal_ema
        state.outputs[0].append(macd_value)
        state.outputs[1].append(state.signal_ema)
        state.outputs[2].append(histogram_value)
