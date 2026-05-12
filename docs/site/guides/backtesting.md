# Backtesting

`BacktestEngine` is the first-beta backtest entry point.

```python
from quantleet.backtest import BacktestEngine, CostConfig

engine = BacktestEngine(
    initial_cash=1_000.0,
    costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
)
```

Run from a data source:

```python
result = engine.run(source=source, strategy=StrategyClass, label="research-run")
```

Run from a materialized series:

```python
result = engine.run(bars=bars, strategy=StrategyClass, config=StrategyConfigInstance)
```

Each run returns a `BacktestResult` with `summary`, `trade_log`,
`equity_curve`, `drawdown_curve`, `report`, and `plot()`.

Provide exactly one of `source` or `bars`.
