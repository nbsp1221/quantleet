# Quantleet

Quantleet is a Python backtesting and quant research toolkit focused on a
polished first-beta single-symbol historical backtesting workflow.

The first public beta target is `0.1.0b1`. It is built for users who want to
load OHLCV history, author a compact strategy, run a deterministic backtest,
inspect `result.report`, visualize `result.plot()`, compare a small finite
parameter grid, and run rolling walk-forward validation without learning the
internal repository workflow first.

## Beta Scope

Current first-beta scope:

- single-symbol, single-timeframe historical OHLCV backtesting
- long-or-flat strategy workflows
- `DataFrameDataSource`, `CSVDataSource`, `CCXTDataSource`, `TimeBar`, and
  `BarSeries`
- `Strategy`, `ta`, `qc`, `ParameterStudy`, and `WalkForwardStudy`
- `BacktestEngine.run(source=..., strategy=StrategyClass, config=...)`
- `BacktestEngine.run(bars=..., strategy=StrategyClass, config=...)`
- market, limit, stop-market, and stop-limit orders
- fixed quantity and `qty_percent` sizing
- conservative reservation, fills, positions, reporting, plotting, finite grid
  parameter exploration, and rolling walk-forward validation

Unsupported in the first public beta:

- live trading
- paper trading
- shorting
- leverage or margin
- multi-symbol portfolios
- multi-timeframe strategies
- trading recommendations or optimizer claims

## Installation

Requirements:

- Python 3.13
- `uv` for local contributor setup

Package-user installation for the first beta will use the published package
once `0.1.0b1` is released:

```bash
uv add quantleet==0.1.0b1
```

From a local checkout today:

```bash
uv sync
uv run poe verify
```

Useful targeted checks:

```bash
uv run poe repo-check
uv run pytest tests/smoke/local -q
```

Live tests are excluded from the default verification lane and must be run
explicitly when needed.

## Quickstart

```python
from quantleet.backtest import BacktestEngine, CostConfig
from quantleet.data import DataFrameDataSource
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

result = engine.run(source=source, strategy=SmaCrossStrategy, label="sma-cross")

print(result.report)
figure = result.plot()
```

`result.report` provides structured run, return, risk, trade, cost, exposure,
fill, and closed-trade information. `result.plot()` returns a Matplotlib figure
with price, fills, equity, and drawdown panels.

## Examples

The first public beta has exactly three canonical examples:

- SMA crossover quickstart
- Orders and sizing
- Parameter exploration

See [docs/site/examples.md](docs/site/examples.md).

## Documentation

Public user documentation lives under [docs/site](docs/site/index.md). Start
with:

- [Installation](docs/site/installation.md)
- [Quickstart](docs/site/quickstart.md)
- [Examples](docs/site/examples.md)
- [Walk-forward analysis](docs/site/guides/walk-forward-analysis.md)
- [Beta scope](docs/site/concepts/beta-scope.md)
- [Public API reference](docs/site/reference/public-api.md)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for local setup, verification, docs
expectations, pull request guidance, and AI-assisted contribution ownership
requirements.

## Security

See [SECURITY.md](SECURITY.md) for vulnerability reporting, secrets handling,
and financial safety boundaries.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for release notes.

## Financial Disclaimer

Quantleet is research and software tooling, not financial advice. Backtest
results do not guarantee future performance. You are responsible for data quality,
assumptions, execution risk, and trading decisions.

## License

Quantleet is licensed under the MIT license.
