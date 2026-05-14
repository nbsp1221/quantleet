# Public API Reference

This curated reference lists the first-beta imports users should prefer.

## Data

- `quantleet.data.TimeBar`
- `quantleet.data.BarSeries`
- `quantleet.data.DataFrameDataSource`
- `quantleet.data.CSVDataSource`
- `quantleet.data.CCXTDataSource`

## Backtesting

- `quantleet.backtest.BacktestEngine`
- `quantleet.backtest.CostConfig`
- `quantleet.backtest.BacktestResult`
- `BacktestResult.report`
- `BacktestResult.plot()`

## Research

- `quantleet.strategy.Strategy`
- `quantleet.strategy.StrategyConfig`
- `Strategy.buy(...)`
- `Strategy.sell(...)`
- `quantleet.research.ParameterStudy`
- `ParameterStudy.grid_search(...)`
- `quantleet.research.WalkForwardStudy`
- `WalkForwardStudy.run(...)`
- `quantleet.research.WalkForwardResult`
- `quantleet.research.WalkForwardFold`
- `quantleet.research.WalkForwardDiagnostic`
- `quantleet.research.WalkForwardOosSummary`
- `quantleet.research.WalkForwardExecutionScale`
- `quantleet.research.ta`
- `quantleet.research.qc`

`quantleet.research.Strategy` remains available as a migration-compatible
re-export.

`WalkForwardStudy` is a research validation workflow. It uses rolling
train/test folds over one materialized `BarSeries`; it is not a live trading,
paper trading, optimizer-guarantee, or continuous-account reporting surface.

Lower-level trading-domain objects are supporting implementation contracts, not
the primary first-beta import surface for user documentation.
