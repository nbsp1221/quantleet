# Research Ergonomics Quickstart

This quickstart is the canonical first-run path for the current implemented `Research Ergonomics` surface.

## Canonical Import Path

```python
from quantleet.backtest import BacktestEngine
from quantleet.research import ParameterStudy, ta, qc
from quantleet.strategy import Strategy
```

The public research API for this slice is the `quantleet.research` import above.
The canonical strategy authoring base lives in `quantleet.strategy`. The
lower-layer imports below are current supporting setup types used to construct
backtest inputs; they are not part of the research public surface.

In the current single-symbol `on_bar()` workflow, common `buy()` and `sell()`
calls may omit `symbol`. Explicit `symbol=...` remains supported, but in the
current single-symbol backtest path it should still match the active series
symbol.

## Canonical User Journeys

The current quickstart and examples are anchored to four initial canonical user journeys.
These journeys are reference workflows for docs, reviews, and later automation.
They are not automatically all strict merge gates.

### Journey 1: Clean Install To Public Imports

- starting state: a fresh environment with the package installed
- user intent: verify that the documented public imports actually work
- success artifact: importing `BacktestEngine`, `Strategy`, `ParameterStudy`,
  `ta`, `qc`, `BarSeries`, `TimeBar`, and the documented data sources from their
  documented capability paths works without hidden setup
- superficially passing but still bad: the package installs, but the documented imports or import paths drift

### Journey 2: DataFrame-Like Quickstart To First Backtest

- starting state: the canonical `DataFrameDataSource` path in this quickstart
- user intent: get to a first successful backtest with minimal setup
- success artifact: the quickstart flow runs and produces a `BacktestResult`
- superficially passing but still bad: the example needs undocumented setup or hidden assumptions to work

### Journey 3: Materialized `BarSeries` To `engine.run(bars=...)`

- starting state: user-created `TimeBar` and `BarSeries`
- user intent: run a backtest from explicit materialized historical bars
- success artifact:
  `BacktestEngine.run(bars=..., strategy=StrategyClass, config=...)` works with
  the documented canonical types
- superficially passing but still bad: the path only works because docs or code silently rely on lower-layer internals

### Journey 4: Exchange-Backed Historical Research Flow

- starting state: the documented `CCXTDataSource` historical path
- user intent: load historical bars and run a research workflow through `engine.run(source=...)`
- success artifact: the documented exchange-backed flow remains coherent enough for humans and agents to follow
- superficially passing but still bad: the flow remains "documented" but becomes too hidden, flaky, or environment-dependent to serve as a trustworthy reference workflow

## Minimal Setup

```python
from quantleet.backtest import BacktestEngine
from quantleet.research import ParameterStudy, ta, qc
from quantleet.strategy import Strategy
from quantleet.data import BarSeries, DataFrameDataSource, TimeBar
from quantleet.trading.domain.costs import CostConfig
import matplotlib.pyplot as plt

source = DataFrameDataSource(
    frame=[
        {"timestamp": "1970-01-01T00:01:00+00:00", "open": 5.0, "high": 5.0, "low": 5.0, "close": 5.0, "volume": 1.0},
        {"timestamp": "1970-01-01T00:02:00+00:00", "open": 4.0, "high": 4.0, "low": 4.0, "close": 4.0, "volume": 1.0},
        {"timestamp": "1970-01-01T00:03:00+00:00", "open": 1.0, "high": 1.0, "low": 1.0, "close": 1.0, "volume": 1.0},
        {"timestamp": "1970-01-01T00:04:00+00:00", "open": 10.0, "high": 10.0, "low": 10.0, "close": 10.0, "volume": 1.0},
        {"timestamp": "1970-01-01T00:05:00+00:00", "open": 11.0, "high": 11.0, "low": 11.0, "close": 11.0, "volume": 1.0},
    ],
    symbol="BTC/USDT",
    timeframe="1m",
)

source_bars = source.load()

bars = BarSeries(
    symbol="BTC/USDT",
    timeframe="1m",
    bar_type="time",
    rows=(
        TimeBar(timestamp=60_000, open=5.0, high=5.0, low=5.0, close=5.0, volume=1.0),
        TimeBar(timestamp=120_000, open=4.0, high=4.0, low=4.0, close=4.0, volume=1.0),
    ),
)

costs = CostConfig(tick_size=1.0, slippage_ticks=1.0, fee_rate=0.001)
```

Current ingestion rule:

- source.load() returns `BarSeries`

Indicator semantics note:

- indicator warmup and `NaN` behavior follow `TA-Lib` semantics
- early bars may remain `na` until the indicator has enough visible history
- prefer `qc.is_na(...)` checks before using fresh indicator values in early history

## Primary Example: SMA crossover

```python
class SmaCrossStrategy(Strategy):
    def init(self) -> None:
        self.fast = ta.sma(self.data.close, length=2)
        self.slow = ta.sma(self.data.close, length=3)

    def on_bar(self, bar) -> None:
        if qc.crossover(self.fast, self.slow):
            self.buy(quantity=1)
        elif qc.crossunder(self.fast, self.slow):
            self.sell(quantity=1)


engine = BacktestEngine(
    initial_cash=1_000.0,
    costs=costs,
)

result = engine.run(
    source=source,
    strategy=SmaCrossStrategy,
    label="sma-cross",
)

fig = result.plot()
plt.show()
fig.savefig("sma-cross.png")

materialized_result = engine.run(
    bars=bars,
    strategy=SmaCrossStrategy,
)
```

Inspect:

- `result.report`
- `result.trade_log`
- `result.equity_curve`
- `result.drawdown_curve`
- `result.summary`

For visual inspection, `result.plot()` returns a Matplotlib figure with price,
fills, equity, and drawdown panels. It uses the data captured by the original
backtest run, so users do not pass bars or a source back into plotting.

For structured inspection, `result.report` contains grouped human-readable
output and structured fields for returns, risk, trades, costs, exposure,
execution assumptions, equity rows, fills, closed trades, and order rejections.

Current summary semantics:

- `result.summary.total_trades` = closed trades
- `result.summary.total_fills` = raw fill count
- `result.summary.win_rate` and `result.summary.profit_factor` use net closed-trade PnL after fees

## Secondary Example: RSI 30/70 mean reversion

```python
class Rsi3070Strategy(Strategy):
    def init(self) -> None:
        self.rsi = ta.rsi(self.data.close, length=2)

    def on_bar(self, bar) -> None:
        if (not self.position.is_open) and not qc.is_na(self.rsi[0]) and self.rsi[0] < 30:
            self.buy(quantity=1)
        elif self.position.is_open and not qc.is_na(self.rsi[0]) and self.rsi[0] > 70:
            self.sell(quantity=1)
```

In the current long-only backtest path, repeated `sell()` calls while flat are treated as exit-only no-ops, not short entries.
For one-position strategies like this RSI example, prefer `self.position.is_open` over local booleans when current position state is all you need.

The supporting notebook demonstrates the same flow in executable form:

- subclass `Strategy`
- bind indicators in `init()`
- evaluate signals and place orders in `on_bar()`
- create `BacktestEngine(...)`
- call `engine.run(source=..., strategy=...)` or `engine.run(bars=..., strategy=...)`
- inspect summary, equity curve, drawdown curve, and `result.plot()`

See:

- [`../../notebooks/research-ergonomics-quickstart.ipynb`](../../notebooks/research-ergonomics-quickstart.ipynb)
- [`../../notebooks/backtest-plotting-real-data-example.ipynb`](../../notebooks/backtest-plotting-real-data-example.ipynb)
