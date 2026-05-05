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

- `quantleet.research.Strategy`
- `Strategy.buy(...)`
- `Strategy.sell(...)`
- `quantleet.research.ParameterStudy`
- `ParameterStudy.grid_search(...)`
- `quantleet.research.ta`
- `quantleet.research.qc`

Lower-level trading-domain objects are supporting implementation contracts, not
the primary first-beta import surface for user documentation.
