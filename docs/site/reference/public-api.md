# Public API Reference

This curated reference lists the first-beta imports users should prefer.

## Data

- `quantcraft.data.TimeBar`
- `quantcraft.data.BarSeries`
- `quantcraft.data.DataFrameDataSource`
- `quantcraft.data.CSVDataSource`
- `quantcraft.data.CCXTDataSource`

## Backtesting

- `quantcraft.backtest.BacktestEngine`
- `quantcraft.backtest.CostConfig`
- `quantcraft.backtest.BacktestResult`
- `BacktestResult.report`
- `BacktestResult.plot()`

## Research

- `quantcraft.research.Strategy`
- `Strategy.buy(...)`
- `Strategy.sell(...)`
- `quantcraft.research.ParameterStudy`
- `ParameterStudy.grid_search(...)`
- `quantcraft.research.ta`
- `quantcraft.research.qc`

Lower-level trading-domain objects are supporting implementation contracts, not
the primary first-beta import surface for user documentation.
