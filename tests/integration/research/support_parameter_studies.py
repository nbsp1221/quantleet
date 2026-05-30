from __future__ import annotations

from typing import ClassVar

from quantleet.backtest import BacktestEngine
from quantleet.data import BarSeries, TimeBar
from quantleet.strategy import Strategy, StrategyConfig, StrategyConfigValidationError
from quantleet.trading.domain.costs import CostConfig
from quantleet.trading.domain.events import BarEvent


def crossing_bars(
    closes: tuple[float, ...] = (100.0, 101.0, 99.0, 104.0, 106.0, 103.0),
) -> BarSeries:
    return BarSeries(
        symbol="TEST",
        timeframe="1m",
        bar_type="time",
        rows=tuple(
            TimeBar(
                timestamp=(index + 1) * 60,
                open=close,
                high=close + 1.0,
                low=close - 1.0,
                close=close,
                volume=1.0,
            )
            for index, close in enumerate(closes)
        ),
    )


def walk_forward_bars(length: int = 12) -> BarSeries:
    closes = tuple(100.0 + ((index % 4) - 1) * 2.0 + index for index in range(length))
    return crossing_bars(closes)


def engine() -> BacktestEngine:
    return BacktestEngine(
        initial_cash=1_000.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
    )


class RoundTripConfig(StrategyConfig):
    fast: int = 5
    slow: int = 20
    enabled: bool = False

    def validate(self) -> None:
        if self.fast >= self.slow:
            raise StrategyConfigValidationError("fast must be less than slow")


class ParameterizedRoundTripStrategy(Strategy[RoundTripConfig]):
    instances: ClassVar[list[ParameterizedRoundTripStrategy]] = []
    constructed_configs: ClassVar[list[dict[str, object]]] = []

    def __init__(self, config: RoundTripConfig | None = None) -> None:
        super().__init__(config)
        type(self).instances.append(self)
        type(self).constructed_configs.append(self.config.to_mapping())

    @property
    def display_name(self) -> str:
        return "Parameterized Round Trip"

    def init(self) -> None:
        self._seen_bars = 0

    def on_bar(self, bar: BarEvent) -> None:
        self._seen_bars += 1
        if self._seen_bars == 1:
            self.buy(quantity=1.0, tag="entry")
        elif self._seen_bars >= 2 and self.position.is_open:
            self.sell(quantity=1.0, tag="exit")


class WfaRoundTripConfig(StrategyConfig):
    fast: int = 2
    slow: int = 4

    def validate(self) -> None:
        if self.fast >= self.slow:
            raise StrategyConfigValidationError("fast must be less than slow")


class WfaRoundTripStrategy(Strategy[WfaRoundTripConfig]):
    constructed_count: ClassVar[int] = 0
    instance_numbers: ClassVar[list[int]] = []
    constructed_configs: ClassVar[list[dict[str, object]]] = []

    def __init__(self, config: WfaRoundTripConfig | None = None) -> None:
        super().__init__(config)
        type(self).constructed_count += 1
        type(self).instance_numbers.append(type(self).constructed_count)
        type(self).constructed_configs.append(self.config.to_mapping())

    def init(self) -> None:
        self._seen = 0

    def on_bar(self, bar: BarEvent) -> None:
        self._seen += 1
        if self._seen == 1:
            self.buy(quantity=1.0, tag="entry")
        elif self._seen >= 2 and self.position.is_open:
            self.sell(quantity=1.0, tag="exit")
