# Examples

The first public beta has exactly three canonical examples.

## Example 1: SMA Crossover Quickstart

Use [Quickstart](quickstart.md) for the canonical first run. It covers strategy
authoring, `BacktestEngine`, `result.report`, and `result.plot()`.

## Example 2: Orders And Sizing

Use [Orders and sizing](guides/orders-and-sizing.md) to compare fixed
`quantity`, `qty_percent`, market, limit, stop-market, and stop-limit behavior
in the current single-symbol historical backtest workflow.

## Example 3: Parameter Exploration

Use [Parameter exploration](guides/parameter-exploration.md) to run
`ParameterStudy(...).grid_search(...)` over a small SMA grid with a `fast <
slow` constraint, inspect records, and open the selected run.
