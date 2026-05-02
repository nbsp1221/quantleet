# Parameter Study External Comparison Experiment Plan

## Repo Workflow Planner Contract

- Date: `2026-05-02`
- Task: Validate the implemented `ParameterStudy(...).grid_search(...)` workflow
  against comparable third-party backtesting libraries from a fresh `/tmp`
  user environment.
- Status: `complete`
- Risk class: `Tier B`, experimental verification only
- Requestor: `User`
- Owner: `Codex`

### Scope

- Use `/tmp` as an isolated user-style project.
- Install the local Quantcraft project and selected comparison libraries with
  `uv`.
- Use the checked-in CSV fixture
  `tests/fixtures/backtest/binance_usdm_btcusdtusdt_1h_2025.csv` as the shared
  dataset.
- Run two to three simple single-symbol strategies through Quantcraft and
  comparable libraries that support parameter search or strategy optimization.
- Compare output shape, selected parameters, and headline metrics.
- Classify metric differences as engine-definition differences, setup
  differences, external-library limitations, or Quantcraft bug candidates.

### Approval Record

- Requestor: `User`
- Human approver: `User`
- Granted scope: task-driven `/tmp` project creation and network-backed package
  installation/documentation lookup for this comparison experiment.
- Verification marker: final report must include commands run, observed
  results, and difference classification.
- Expiration: end of this conversation turn.
- Audit reference: this plan file.

### Governing Docs

- `AGENTS.md`
- `README.md`
- `ARCHITECTURE.md`
- `docs/product-specs/parameter-exploration.md`
- `docs/product-specs/parameter-exploration-test-scenarios.md`
- `docs/plans/2026-05-02-parameter-exploration-implementation-plan.md`

### Success Criteria

- A fresh `/tmp` uv project can import and run local Quantcraft's public
  `ParameterStudy` workflow.
- The experiment uses the same CSV data across all compared libraries.
- The experiment includes at least two simple strategies and three comparison
  libraries when installation/runtime compatibility permits.
- For every material difference, the report separates symptom, likely cause,
  and whether it points to a Quantcraft bug.
- The final report identifies any remaining risks or follow-up work.

### Verification Commands

- `/tmp` uv setup and dependency installation command.
- Experiment script command.
- Any focused diagnostics required to classify failures or output differences.

## Evaluator Acceptance Contract

- Evaluator owner: `Codex`
- Acceptance artifact: final user report plus this plan updated with
  verification evidence.
- Auto-fail conditions:
  - using a different dataset per library
  - modifying Tier A `trading` or `execution` code
  - treating different metric definitions as bugs without evidence
  - reporting completion without fresh experiment output

## Verification Evidence

- `/tmp` setup:
  - `uv init --bare --python 3.13`
  - `uv add --editable /home/retn0/repositories/nbsp1221/quantcraft`
  - `uv add pandas backtesting backtrader vectorbt`
- Experiment command:
  - `uv run python -X faulthandler compare_parameter_study.py --output comparison-results.json`
- Result artifact:
  - `/tmp/quantcraft-external-comparison/comparison-results.json`
- Dataset:
  - `/home/retn0/repositories/nbsp1221/quantcraft/tests/fixtures/backtest/binance_usdm_btcusdtusdt_1h_2025.csv`
  - rows: `8760`
  - start: `2025-01-01T00:00:00+00:00`
  - end: `2025-12-31T23:00:00+00:00`
- Installed comparison versions:
  - `backtesting.py==0.6.5`
  - `backtrader==1.9.78.123`
  - `vectorbt==0.28.2`
  - `pandas==3.0.2`
  - `numpy==2.4.4`

## Experiment Summary

All Quantcraft runs completed through
`ParameterStudy(...).grid_search(...)`; every Quantcraft scenario produced
strict-JSON-safe `to_records()` output.

| Scenario | Raw candidates | Quantcraft best | Vectorbt best | backtesting.py best | Backtrader best |
| --- | ---: | --- | --- | --- | --- |
| `sma_cross` | 6 | `fast=32, slow=64` | same | same | same |
| `rsi_mean_reversion` | 12 | `length=21, lower=30, upper=70` | same | same | same |
| `donchian_breakout` | 6 | `entry=80, exit=20` | same | same | same |

Notable diagnostics:

- `vectorbt` matched Quantcraft final equity to floating-point noise on
  `rsi_mean_reversion` and `donchian_breakout`.
- `vectorbt` selected the same `sma_cross` parameters but reported one more
  trade and a `0.0995%` return delta, consistent with signal/closed-vs-open
  trade accounting differences rather than a Quantcraft failure.
- `backtesting.py` and `backtrader` selected the same parameters in all
  scenarios but differed in returns and drawdown because their regular
  execution paths use integer/unit sizing or different drawdown accounting for
  this BTC-priced dataset.
- `backtesting.py Backtest.optimize(...)` segfaulted on the default
  fork/shared-memory path under this Python 3.13 stack. Setting multiprocessing
  start method to `spawn` forced its documented thread fallback and made
  optimization complete.
- A trial with `backtesting.lib.FractionalBacktest` removed the sizing mismatch
  for the RSI scenario, but `SMA` and `Donchian` hit a `ValueError: output
  array is read-only` in this dependency stack. The recorded comparison
  therefore uses regular `Backtest` and classifies residual differences as
  external sizing/metric semantics.

## Evaluator Disposition

- Quantcraft bug candidates found: none.
- Confidence:
  - high that `ParameterStudy.grid_search(...)` performs the intended user
    workflow over real fixture data
  - high that selected best rows are stable across independent libraries for
    these strategy families
  - medium for exact metric parity with integer-sizing libraries because their
    execution semantics differ from Quantcraft's fractional `qty_percent`
    workflow
- Remaining follow-up:
  - Add a first-party example or notebook that reproduces this style of
    parameter study on the checked-in BTC fixture.
  - If exact cross-library parity becomes a release goal, use a low-priced or
    normalized dataset that avoids integer-share/fractional-unit mismatches.
