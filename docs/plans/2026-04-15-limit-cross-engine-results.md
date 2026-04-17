# Limit Cross-Engine Experiment Results

## Status

- Status: `draft evidence note`
- Class: `experiment result`
- Scope: compare `quantcraft` limit-order backtest outputs against external libraries before freezing new canonical limit regressions

Related documents:

- [2026-04-15-limit-cross-engine-experiment.md](2026-04-15-limit-cross-engine-experiment.md)
- [2026-04-14-limit-strategy-regression-design.md](2026-04-14-limit-strategy-regression-design.md)

## Purpose

The point of this experiment was to avoid freezing new limit-order golden
results from `quantcraft` without an external comparison baseline.

The working question was:

- if the same dataset and the same high-level strategy rules are run in several
  well-known backtesting libraries, do the resulting trade counts, fill prices,
  and ending equity agree closely enough that `quantcraft` can be trusted as a
  source of canonical limit-order regression values?

## Dataset And Shared Experiment Rules

- dataset: checked-in BTC USD-M 1h 2025 CSV fixture under
  `tests/fixtures/backtest/binance_usdm_btcusdtusdt_1h_2025.csv`
- initial cash: `1_000_000`
- updated cost assumptions for the follow-up run:
  - fee rate: `0.04%`
  - slippage: `1 tick`
- engines:
  - `quantcraft`
  - `backtrader`
  - `pyalgotrade`
  - `nautilus_trader`
- rejected comparator:
  - `PyBroker` was installed and inspected, but its default limit-order path
    schedules an order for a specific future bar and removes it after that
    execution attempt, which makes it a poor comparator for persistent resting
    limit orders
- partially explored comparator:
  - `backtesting.py` was useful in the zero-cost baseline, but was not kept in
    the final cost run because its public cost surface does not provide a clean
    fixed one-tick market-only slippage model comparable to the other engines

To reduce indicator-implementation noise, the experiment used common pandas
precomputed EMA, RSI, and Bollinger values and then fed the same strategy rules
into each engine.

For the cost run, still-open long positions were explicitly closed with a
market exit on the last bar so ending-equity comparison would not depend on
engine-specific open-position accounting behavior.

## Strategy Set Used

### 1. EMA Pullback Buy-Limit With Market Exit

- buy limit when the completed bar is above a rising EMA by more than 1%
- limit price is the EMA value
- market exit when close falls back below EMA

### 2. Market Entry With Take-Profit Sell-Limit Exit

- market buy when RSI 14 on the completed bar is below 30
- once filled, place a sell limit at `entry_price * 1.02`

### 3. Bollinger Lower-Band Buy-Limit With Middle-Band Sell-Limit

- buy limit when the completed bar closes below the lower Bollinger band
- limit price is the lower band value
- once filled, place a sell limit at the Bollinger middle band

## Result Summary

### Zero-Cost Baseline

The first baseline run used zero fees and zero slippage and already showed
`quantcraft` diverging from the conservative external-engine cluster. That run
remains useful as exploratory context only.

### Cost Run: EMA Pullback Buy-Limit With Market Exit

| Engine | Closed Trades | Fill Count | Final Equity |
| --- | --- | --- | --- |
| `quantcraft` | 29 | 58 | `1_010_378.0082` |
| `backtrader` | 29 | 58 | `1_000_226.3763` |
| `pyalgotrade` | 28 | 56 | `1_000_302.1064` |
| `nautilus_trader` | 29 | 58 | `1_010_371.2110` |

Interpretation:

- `quantcraft` and `nautilus_trader` were extremely close
- `backtrader` and `pyalgotrade` formed a tighter conservative cluster below
  the `quantcraft` / `nautilus_trader` pair
- this supports the idea that `quantcraft` may be philosophically closer to an
  execution-engine style optimistic fill model than to a conservative
  bar-backtester model

### Cost Run: Market Entry With Take-Profit Sell-Limit Exit

| Engine | Closed Trades | Fill Count | Final Equity |
| --- | --- | --- | --- |
| `quantcraft` | 14 | 29 | `1_003_881.3978` |
| `backtrader` | 14 | 29 | `998_389.9213` |
| `pyalgotrade` | 14 | 29 | `998_389.9213` |
| `nautilus_trader` | 1 | 2 | `993_388.0978` |

Interpretation:

- `backtrader` and `pyalgotrade` still matched exactly
- `quantcraft` remained materially more favorable than the conservative pair
- the current Nautilus port for this strategy did not produce a comparable
  sequence of repeated take-profit fills, so it is not yet a reliable
  apples-to-apples comparator for this strategy family

### Cost Run: Bollinger Lower-Band Buy-Limit With Middle-Band Sell-Limit

| Engine | Closed Trades | Fill Count | Final Equity |
| --- | --- | --- | --- |
| `quantcraft` | 27 | 55 | `1_006_367.1218` |
| `backtrader` | 27 | 55 | `994_482.0805` |
| `pyalgotrade` | 27 | 55 | `994_484.8816` |
| `nautilus_trader` | 1 | 2 | `991_259.5468` |

Interpretation:

- `backtrader` and `pyalgotrade` again formed a tight conservative cluster
- `quantcraft` remained materially more optimistic
- the current Nautilus port again failed to generate repeated comparable
  passive-limit exits, so it cannot yet be treated as a finalized comparator
  for this strategy family

## Main Finding

The cost-adjusted experiment still does **not** support immediately freezing
`quantcraft` limit strategy outputs as canonical real-data regression values.

Instead, it supports the narrower conclusion:

- `quantcraft` currently uses a materially different limit-order fill semantic
  from the `backtrader` / `pyalgotrade` cluster
- `nautilus_trader` appears philosophically closer to `quantcraft` for the EMA
  pullback strategy under a custom market-only one-tick slippage fill model

The most likely reason is that `quantcraft` treats limit orders as filling at
the best actually executable synthetic tick price once the limit condition is
met, while the conservative bar-based engines used here mostly behave as if a
triggered limit fills at the limit price itself.

That difference especially matters for:

- favorable price improvement on sell limits
- favorable price improvement on buy limits
- ending equity when many fills occur

## What This Means For Canonical Limit Tests

Do **not** freeze real-data canonical limit-order golden results yet.

Before doing that, the repository needs an explicit decision on which semantic
contract it wants:

1. `quantcraft` semantics are intentional
   - keep them
   - document them clearly
   - add synthetic tests that defend the chosen behavior
   - only then freeze real-data golden results

2. external-engine consensus semantics are preferred
   - change `quantcraft`
   - re-run the comparison
   - only then freeze real-data golden results

## Recommendation

Current recommendation:

- block new canonical limit-order golden fixtures for now
- first make an explicit product and engine decision about limit fill semantics
- decide whether the intended comparator philosophy is:
  - conservative bar-backtester semantics (`backtrader` / `pyalgotrade`)
  - optimistic execution-engine semantics closer to `nautilus_trader`
- finish a cleaner apples-to-apples Nautilus port for the take-profit-limit and
  Bollinger both-side strategies before using Nautilus as decisive external
  validation for the whole limit strategy set
- then run this same cross-engine experiment again after any engine changes
