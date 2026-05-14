# Walk-Forward Analysis

`WalkForwardStudy` checks whether settings selected on one training window also
survive the next unseen test window.

Use it after a small `ParameterStudy`-style search space is already worth
checking. It is validation evidence, not an optimizer guarantee, trading
recommendation, paper-trading loop, live-trading loop, or continuous account
simulation.

```python
from quantleet.research import WalkForwardStudy


study = WalkForwardStudy(
    engine=engine,
    bars=bars,
    strategy=ParameterizedSmaStrategy,
)

result = study.run(
    parameters={"fast": [2, 3], "slow": [3, 4]},
    constraint=lambda config: config["fast"] < config["slow"],
    objective=("returns.total_return", "max"),
    train_size=120,
    test_size=30,
)

fold_records = result.to_records()
candidate_records = result.to_candidate_records()
summary = result.oos_summary
diagnostics = result.diagnostics
```

The first beta workflow is intentionally narrow:

- input is one materialized `BarSeries`
- folds use bar-count windows
- mode is rolling only
- the objective uses the same tuple shape as `ParameterStudy`
- successful folds retain the selected out-of-sample `BacktestResult`
- `oos_summary` summarizes independent test folds

Do not read `oos_summary` as a stitched portfolio, live-equivalent account, or
future-performance claim.
