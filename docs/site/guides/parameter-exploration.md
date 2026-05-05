# Parameter Exploration

`ParameterStudy` runs a finite grid of strategy parameters against a
materialized series.

```python
from collections.abc import Mapping

from quantleet.research import ParameterStudy, Strategy, qc, ta


class ParameterizedSmaStrategy(Strategy):
    def __init__(self, *, fast: int, slow: int) -> None:
        super().__init__()
        self._fast_length = fast
        self._slow_length = slow

    def parameters(self) -> dict[str, object]:
        return {"fast": self._fast_length, "slow": self._slow_length}

    def init(self) -> None:
        self.fast = ta.sma(self.data.close, length=self._fast_length)
        self.slow = ta.sma(self.data.close, length=self._slow_length)

    def on_bar(self, bar) -> None:
        if qc.is_na(self.fast[0]) or qc.is_na(self.slow[0]):
            return
        if qc.crossover(self.fast, self.slow):
            self.buy(quantity=1.0)
        elif self.position.is_open and qc.crossunder(self.fast, self.slow):
            self.sell(quantity=1.0)


def factory(parameters: Mapping[str, object]) -> Strategy:
    return ParameterizedSmaStrategy(
        fast=int(parameters["fast"]),
        slow=int(parameters["slow"]),
    )


grid = ParameterStudy(
    engine=engine,
    bars=bars,
    strategy_factory=factory,
).grid_search(
    parameters={"fast": [2, 3], "slow": [3, 4]},
    constraint=lambda parameters: parameters["fast"] < parameters["slow"],
    objective=("returns.total_return", "max"),
)

records = grid.to_records()
best = grid.best()
selected_report = best.backtest.report if best.backtest is not None else None
```

Grid search is a research diagnostic. It is not an optimizer guarantee or a
trading recommendation.
