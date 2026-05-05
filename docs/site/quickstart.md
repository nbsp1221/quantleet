# Quickstart

This quickstart runs a single-symbol SMA crossover backtest from in-memory
OHLCV data.

```python
from quantleet.backtest import BacktestEngine, CostConfig
from quantleet.data import DataFrameDataSource
from quantleet.research import Strategy, qc, ta


class SmaCrossStrategy(Strategy):
    def init(self) -> None:
        self.fast = ta.sma(self.data.close, length=2)
        self.slow = ta.sma(self.data.close, length=3)

    def on_bar(self, bar) -> None:
        if qc.is_na(self.fast[0]) or qc.is_na(self.slow[0]):
            return
        if qc.crossover(self.fast, self.slow):
            self.buy(quantity=1.0, tag="sma-entry")
        elif self.position.is_open and qc.crossunder(self.fast, self.slow):
            self.sell(quantity=1.0, tag="sma-exit")


source = DataFrameDataSource(
    frame=[
        {"timestamp": "1970-01-01T00:01:00+00:00", "open": 10.0, "high": 12.0, "low": 8.0, "close": 10.0, "volume": 1.0},
        {"timestamp": "1970-01-01T00:02:00+00:00", "open": 9.0, "high": 11.0, "low": 7.0, "close": 9.0, "volume": 1.0},
        {"timestamp": "1970-01-01T00:03:00+00:00", "open": 8.0, "high": 10.0, "low": 6.0, "close": 8.0, "volume": 1.0},
        {"timestamp": "1970-01-01T00:04:00+00:00", "open": 11.0, "high": 13.0, "low": 9.0, "close": 11.0, "volume": 1.0},
        {"timestamp": "1970-01-01T00:05:00+00:00", "open": 12.0, "high": 14.0, "low": 10.0, "close": 12.0, "volume": 1.0},
    ],
    symbol="BTC/USDT",
    timeframe="1m",
)

engine = BacktestEngine(
    initial_cash=1_000.0,
    costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
)

result = engine.run(source=source, strategy=SmaCrossStrategy(), label="sma-cross")

print(result.report)
figure = result.plot()
```

`result.report` contains structured run, return, risk, trade, cost, exposure,
fill, and closed-trade sections. `result.plot()` returns a Matplotlib figure
with price, fills, equity, and drawdown panels.

## Financial Disclaimer

Quantleet is research and software tooling, not financial advice. Backtest
results do not guarantee future performance. You are responsible for data quality,
assumptions, execution risk, and trading decisions.
