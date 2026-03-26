# Research Ergonomics Quickstart

This quickstart is the canonical first-run path for the current implemented `Research Ergonomics` surface.

## Canonical Import Path

```python
from quantcraft.research import Strategy, ta, qc, run_backtest
```

The public research API for this slice is the `quantcraft.research` import above. The lower-layer imports below are current supporting setup types used to construct backtest inputs; they are not part of the research public surface.

## Minimal Setup

```python
from quantcraft.research import Strategy, ta, qc, run_backtest
from quantcraft.data import DataFrameDataSource
from quantcraft.trading.domain.costs import CostConfig

rows = DataFrameDataSource(
    frame=[
        {"timestamp": "1970-01-01T00:01:00+00:00", "open": 5.0, "high": 5.0, "low": 5.0, "close": 5.0, "volume": 1.0},
        {"timestamp": "1970-01-01T00:02:00+00:00", "open": 4.0, "high": 4.0, "low": 4.0, "close": 4.0, "volume": 1.0},
        {"timestamp": "1970-01-01T00:03:00+00:00", "open": 1.0, "high": 1.0, "low": 1.0, "close": 1.0, "volume": 1.0},
        {"timestamp": "1970-01-01T00:04:00+00:00", "open": 10.0, "high": 10.0, "low": 10.0, "close": 10.0, "volume": 1.0},
        {"timestamp": "1970-01-01T00:05:00+00:00", "open": 11.0, "high": 11.0, "low": 11.0, "close": 11.0, "volume": 1.0},
    ],
    symbol="BTC/USDT",
    timeframe="1m",
).load()

costs = CostConfig(tick_size=1.0, slippage_ticks=1.0, fee_rate=0.001)
```

## Primary Example: SMA crossover

```python
class SmaCrossStrategy(Strategy):
    def init(self) -> None:
        self.fast = ta.sma(self.data.close, length=2)
        self.slow = ta.sma(self.data.close, length=3)

    def on_bar(self, bar) -> None:
        if qc.crossover(self.fast, self.slow):
            self.buy(symbol=bar.symbol, quantity=1)
        elif qc.crossunder(self.fast, self.slow):
            self.sell(symbol=bar.symbol, quantity=1)


result = run_backtest(
    symbol="BTC/USDT",
    bar_type="time",
    bar_spec="1m",
    rows=rows,
    strategy=SmaCrossStrategy(),
    initial_cash=1_000.0,
    costs=costs,
)
```

Inspect:

- `result.trade_log`
- `result.equity_curve`
- `result.summary`

## Secondary Example: RSI 30/70 mean reversion

```python
class Rsi3070Strategy(Strategy):
    def init(self) -> None:
        self.rsi = ta.rsi(self.data.close, length=2)

    def on_bar(self, bar) -> None:
        if not qc.is_na(self.rsi[0]) and self.rsi[0] < 30:
            self.buy(symbol=bar.symbol, quantity=1)
        elif not qc.is_na(self.rsi[0]) and self.rsi[0] > 70:
            self.sell(symbol=bar.symbol, quantity=1)
```

The supporting notebook demonstrates the same flow in executable form:

- subclass `Strategy`
- bind indicators in `init()`
- evaluate signals and place orders in `on_bar()`
- call `run_backtest(...)`
- inspect summary and equity curve

See:

- [`../../notebooks/research-ergonomics-quickstart.ipynb`](../../notebooks/research-ergonomics-quickstart.ipynb)
