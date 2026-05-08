# Strategy Authoring

Strategies subclass `quantleet.strategy.Strategy`.

```python
from quantleet.research import qc, ta
from quantleet.strategy import Strategy


class SmaCrossStrategy(Strategy):
    def init(self) -> None:
        self.fast = ta.sma(self.data.close, length=2)
        self.slow = ta.sma(self.data.close, length=3)

    def on_bar(self, bar) -> None:
        if qc.is_na(self.fast[0]) or qc.is_na(self.slow[0]):
            return
        if qc.crossover(self.fast, self.slow):
            self.buy(quantity=1.0)
        elif self.position.is_open and qc.crossunder(self.fast, self.slow):
            self.sell(quantity=1.0)
```

Use `init()` to bind indicators. Use `on_bar()` to inspect visible historical
state and submit orders.

Useful strategy state:

- `self.data.open`
- `self.data.high`
- `self.data.low`
- `self.data.close`
- `self.data.volume`
- `self.position.is_open`
- `self.position.quantity`
- `self.position.average_entry_price`

Indicator warmup can produce missing values on early history. Use `qc.is_na`
before using fresh indicator values.

In the current single-symbol workflow, `buy()` and `sell()` may omit `symbol`.
If supplied, it must match the active series symbol.
