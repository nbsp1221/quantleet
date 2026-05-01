# Backtest Result Reporting Beta Spec

- Date: 2026-04-30
- Task: Define the first-beta result reporting requirements for the
  single-symbol backtesting product surface.
- Status: `complete`
- Risk class: `Tier B`
- Requestor: User
- Owner: Codex

## Planner Contract

- Goal: Define what a general Python quant user must be able to learn from one
  completed `BacktestEngine.run(...)` result before `quantcraft` can claim a
  credible first beta for single-symbol backtesting.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `docs/PLANS.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/research-ergonomics.md`
  - `docs/product-specs/backtest-mvp.md`
  - `docs/design-docs/index.md`
  - `docs/design-docs/package-topology-and-naming.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/DESIGN.md`
  - `docs/research/libraries/backtesting-py.md`
- Why these are governing:
  - The README and research ergonomics spec define the first public beta target
    and name `backtesting.py` as the near-term UX comparator.
  - The backtest MVP spec defines the current single-symbol engine boundary.
  - The `backtesting.py` dossier records the main benchmark lessons already
    accepted into repository research.
  - This document is one planning artifact in `docs/plans/`; it does not replace
    durable product specs.
- In-repo scope:
  - Define user-facing reporting requirements for the first beta.
  - Define what result information must be visible, interpretable, and
    machine-readable.
  - Define metric calculation semantics, including formulas and edge cases,
    where those semantics affect user trust.
  - Define benchmark-driven expectations without prescribing implementation
    details.
  - Prepare the ground for separate test-scenario and implementation-plan
    documents.
- Out-of-repo scope:
  - No PyPI publishing.
  - No external service integration.
  - No runtime code changes in this slice.
- Tier A progression requested: `no`
- Approval record, if required: Tier A approval is not required. This is a
  Tier B planning document for backtest/research UX and does not change
  `trading` or `execution` code.
- External research approval record:
  - requestor: User
  - human approver: User
  - verification marker: User explicitly requested web search, library
    investigation, `/tmp` source inspection, and optional `/tmp` git clone for
    this metric-semantics planning work.
  - granted scope: Read-only benchmark research for `backtesting.py`,
    `vectorbt`, `backtrader`, QuantStats, and `empyrical`, plus official
    documentation needed to define reporting metric semantics.
  - expiration: This result-reporting spec slice only.
  - audit reference: Conversation request on 2026-04-30 to investigate metric
    formulas through web search and local or cloned library sources.
- Verification commands:
  - `uv run poe repo-check`
  - `uv run pytest tests/structure/docs tests/structure/repo -q`
- Success criteria:
  - The document explains why result reporting is the first beta slice.
  - The document defines user requirements independently of implementation
    choices.
  - The document closes calculation semantics for the beta reporting metrics.
  - The document identifies which benchmark expectations apply to beta and
    which are explicitly later work.
  - The document is specific enough to drive the next test-scenario document.
- Out of scope:
  - Plotting implementation.
  - Parameter optimization implementation.
  - Multi-symbol, short, leverage, paper trading, or live trading reporting.

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice:
  - Confirm the spec is about what the user needs, not how the code will be
    structured.
  - Confirm the spec does not claim unimplemented features are already shipped.
  - Confirm every beta requirement stays inside single-symbol, long-only
    historical OHLCV backtesting.
  - Confirm the requirements are specific enough to become tests later.
- Acceptance artifact location: This plan's `Evaluator Review` section.
- How the generator and evaluator agreed on done before execution: The planner
  contract fixes scope, verification, and non-goals before any document edit.
- Checks the evaluator will use:
  - Manual review against README and `research-ergonomics.md`.
  - `uv run poe repo-check`.
  - `uv run pytest tests/structure/docs tests/structure/repo -q`.
- Auto-fail conditions:
  - The spec expands first beta into multi-symbol, shorting, leverage, paper, or
    live trading.
  - The spec is mostly implementation detail rather than user-facing
    requirements.
  - The spec duplicates durable product-spec authority instead of defining this
    planned slice.
  - Repository document checks fail.

## Authority Boundary

This file is the planning spec for the result-reporting slice. It is specific
enough to drive the next test-scenario and implementation-plan documents, but it
is not the long-lived product authority by itself.

Before implementation is closed, the durable user-facing reporting contract must
be promoted into the routed product-spec surface, most likely
`docs/product-specs/research-ergonomics.md` or a product-spec document linked
from that file. The implementation plan must include that promotion or explain
why the product-spec routing changed.

## Product Context

The first public beta target is a polished single-symbol Python backtesting
experience for users who want to test a strategy on historical OHLCV data.
Result reporting is the first beta slice because it is the first thing a user
sees after a successful backtest run.

This document defines one beta-enabling feature slice, not the entire beta
release. The broader beta bar remains higher than result reporting alone, but
this slice must be complete enough that it can become the first reliable
building block for that beta.

A backtest that only returns raw fills, a raw equity tuple, and a small dataclass
summary can prove that the engine works, but it does not yet let a user decide
whether the strategy is worth improving. The beta reporting surface must turn
the result object into an understandable research artifact.

The benchmark expectation comes from established single-asset backtesting tools,
especially `backtesting.py`. Its public docs make `Backtest.run()` return a
detailed statistics object, expose equity and trade tables, support optimization
against named statistics, and offer plotting as a natural follow-up. The first
`quantcraft` beta does not need to copy that API, but it must satisfy the same
basic user need: after one run, the user should understand performance, risk,
trading activity, and comparison to holding the asset.

## Target User

The target user for this slice is a general Python quant user who has:

- historical OHLCV data for one tradeable asset
- a Python strategy implemented with `quantcraft.research.Strategy`
- a desire to answer whether the strategy is promising enough to inspect,
  adjust, or parameter-test

The user should not need to understand `quantcraft` internals, the trading
kernel, order reservations, or future paper/live architecture to interpret one
backtest result.

## User Questions The Report Must Answer

The beta result report must answer these questions without requiring the user to
manually reconstruct metrics from fills:

1. Did the strategy make or lose money?
2. How did it compare with simply buying and holding the same asset?
3. How much drawdown did the strategy experience?
4. How volatile was the equity curve?
5. Was the result driven by many trades or only a few trades?
6. Were winning and losing trades balanced, skewed, or fragile?
7. How much did fees affect the outcome?
8. How much time was the strategy exposed to the market?
9. Did the strategy finish flat or with an open position?
10. What execution assumptions shaped the result?

If these questions cannot be answered from the public result surface, the result
reporting slice is not beta-complete.

## Required Result Sections

### Run Identity

The report must identify what period and dataset were tested.

Required information:

- symbol
- timeframe
- start timestamp
- end timestamp
- number of bars
- initial cash
- execution model name

Why: users need enough context to compare runs and avoid mistaking one dataset,
timeframe, or execution policy for another.

### Strategy And Run Configuration

The report must identify the strategy and user-visible run configuration.

Required information:

- strategy class name
- strategy display name, if the user supplied one
- strategy parameter values that are public, deterministic, and explicitly
  exposed by the strategy or run metadata
- run label, if the user supplied one

Why: users compare many runs of the same strategy family. A result that cannot
say which strategy parameters produced it is not ready to become an optimization
or notebook artifact.

Approved beta direction:

- The first reporting slice accepts the current strategy-instance workflow.
- `BacktestEngine.run(...)` must provide a user-facing run label through a
  `label` keyword argument.
- A user-supplied strategy display name must be exposed through
  `Strategy.display_name`.
- Strategy parameters must not be discovered through arbitrary public attribute
  introspection.
- Strategy parameters must be captured through an explicit strategy-owned
  `parameters()` hook.
- The run manifest must leave room for a later
  `engine.run(strategy=StrategyClass, params={...})` workflow, because that is
  the natural path toward optimization and parameter sweeps.

### Return And Equity

The report must show the user's headline outcome.

Required information:

- final equity
- equity peak
- total return
- buy-and-hold return for the same symbol over the same bar range
- strategy return minus buy-and-hold return
- annualized return when annualization is available
- final cash balance
- gross realized PnL before fees
- net realized PnL after allocated fees
- unrealized PnL

Why: a strategy that makes money can still be worse than passive exposure. The
first beta should make that visible by default.

### Risk And Drawdown

The report must make downside behavior visible.

Required information:

- maximum drawdown
- longest drawdown duration or bar count
- volatility over the tested bar sequence
- Sharpe ratio, using a documented risk-free-rate default
- periods-per-year assumption used for annualized metrics

Deferred information:

- average drawdown
- drawdown episode length specifically containing the deepest drawdown

Why: return without risk is not enough for strategy evaluation. `backtesting.py`
sets user expectations by showing drawdown, volatility, and Sharpe-like metrics
in the default run output.

### Trade Quality

The report must summarize closed-trade behavior separately from raw fills.

Required information:

- number of closed trades
- number of raw fills
- win rate
- best trade
- worst trade
- average trade
- average win
- average loss
- profit factor
- expectancy

Deferred information:

- largest win/loss contribution

Why: users reason about strategies in trades, not only fills. The current
`trade_log` is necessary engine evidence, but it is not sufficient as the main
research report.

### Exposure And Ending State

The report must show how much market participation produced the result.

Required information:

- bars in position
- exposure ratio
- final position quantity
- final average entry price when a position remains open
- explicit flat/open ending-state label

Why: a strategy with high return but near-constant exposure means something
different from a strategy with sparse exposure. An open final position also
changes how users interpret closed-trade statistics.

### Cost Impact

The report must make trading costs visible.

Required information:

- total fees
- fees as a share of initial cash

Deferred information:

- fees as a share of gross closed-trade PnL when calculable

Why: the first beta should make fee drag visible because crypto and high-turnover
strategies can look better than they are when costs are hidden.

### Execution Assumptions

The report must show the assumptions that shaped the backtest result.

Required information:

- execution model name
- order activation timing structured identifier:
  `order_activation_timing = "next_bar"`
- fill-price basis structured identifier:
  `fill_price_basis = "conservative_ohlcv"`
- open-position finalization policy structured identifier:
  `open_position_finalization = "mark_to_market"`
- `tick_size`
- `slippage_ticks`
- `fee_rate`
- order rejection count
- annual risk-free rate used for risk metrics
- periods-per-year used for annualized metrics

Why: two backtests with the same trades can imply different product truth if
fees, slippage, fill policy, or open-position treatment differ. These values
must be inspectable without reading engine internals.

### Data For Further Inspection

The report must expose analysis-friendly data, not only formatted text.

Required information:

- an equity curve with timestamps
- a drawdown curve or enough equity data to derive it directly
- a closed-trade table or sequence
- the existing raw fill log
- order rejection events

Why: readable summary output is for first inspection; structured data is for the
next research step. The user should not need private internals to build a
notebook table, chart, or parameter comparison later.

Minimum structured data fields:

- equity curve rows: `timestamp`, `equity`, `drawdown`
- closed-trade rows: `entry_timestamp`, `exit_timestamp`, `quantity`,
  `entry_price`, `exit_price`, `gross_pnl`, `net_pnl`, `fees`,
  `net_return`, `duration_bars`, `entry_tag`, `entry_tags`, and `exit_tag`
- raw reporting fill rows: existing fill facts plus `order_id`, `order_type`,
  and any order `tag`
- order rejection rows: symbol, side, order type, reason, timestamp, quantity,
  order id if available, and tag

The existing raw `trade_log` may continue to expose minimal `FillEvent` values.
Tag provenance for beta reporting belongs in backtest/reporting-owned rows, not
in the trading kernel fill event contract.

## Beta Metric Priority

The first beta reporting slice has two priority levels.

P0 metrics must be implemented before this result-reporting slice is considered
beta-complete:

- run identity
- strategy and run configuration
- execution assumptions
- final equity, equity peak, total return, buy-and-hold return, and active
  return
- gross realized PnL, net realized PnL, unrealized PnL, and total fees
- annualized return, volatility, Sharpe ratio, and the annualization/risk-free
  assumptions used to calculate them
- maximum drawdown and longest drawdown bar count
- closed-trade count, fill count, win rate, best/worst trade, average trade
  return, expectancy return, average win, average loss, and profit factor
- total fees and fees as a share of initial cash
- exposure ratio and flat/open ending state
- timestamped equity/drawdown rows, closed-trade rows, raw fill rows, and order
  rejection rows

P1 metrics are useful but must not block the first beta reporting slice:

- average drawdown
- deepest-drawdown episode length
- largest win/loss contribution
- fees as a share of gross closed-trade PnL
- rolling, walk-forward, or optimizer-specific metrics

## Metric Semantics And Calculation Rules

This section is part of the spec, not an implementation detail. Result reporting
metrics directly affect user trust, so the first beta must not leave their
meaning to implementation accident.

The benchmark survey found broad agreement on the metric families:

- `backtesting.py` exposes start/end, exposure, final and peak equity,
  commissions, total return, buy-and-hold return, annualized return,
  annualized volatility, CAGR, Sharpe, Sortino, Calmar, alpha/beta, drawdown,
  trade statistics, profit factor, expectancy, an equity/drawdown table, and a
  trade table.
- `vectorbt`, `empyrical`, and QuantStats compute return and risk metrics from a
  periodic return series, with maximum drawdown derived from cumulative equity
  or cumulative returns.
- `backtrader` drawdown analyzers track decline from the running peak portfolio
  value and drawdown length.

`quantcraft` should adopt the common semantics, but keep formulas simple,
auditable, and compatible with the current single-symbol long-only engine.

### Unit Conventions

Machine-readable ratio values must use decimal ratios, not display percentages.

Examples:

- `0.125` means `12.5%`.
- `-0.25` means `-25%`.

Human-readable reports may display percentages, but structured result values
must not require parsing text or stripping percent signs.

### Undefined And Infinite Values

Public structured output must use explicit typed sentinels:

- undefined metric: `None`
- positive infinity: `math.inf`
- negative infinity: `-math.inf`

Public structured output must not use string sentinels such as `"n/a"` and must
not expose `NaN` for undefined beta reporting metrics. Human-readable reports
may render `None` as `n/a`.

Why: the next test-scenario document must be able to assert deterministic
values. `NaN` is useful internally, but it is awkward in public structured
output because it is not equal to itself.

### Return Series Basis

All strategy-level risk metrics use the marked-to-market equity curve.

The equity curve for reporting must include unrealized PnL from any open
position at each reported bar. Balance-only curves are not valid for beta risk
reporting because they hide open-position drawdown.

Let:

- `initial_cash` be the engine starting cash.
- `equity[t]` be the marked-to-market equity at reporting point `t`.
- `n` be the number of equity points.

The periodic equity return series is:

- `return[0] = equity[0] / initial_cash - 1`
- `return[t] = equity[t] / equity[t - 1] - 1` for `t > 0`

If `n == 0`, return-based metrics are undefined unless a metric explicitly
states a zero-value default.

### Annualization Basis

Annualized beta metrics must use an explicit `periods_per_year`.

Default rule:

1. If the bar timeframe can be parsed into a duration, use
   `periods_per_year = milliseconds_per_year / timeframe_milliseconds`.
2. Otherwise, infer the median positive timestamp delta from the bar series and
   use `periods_per_year = milliseconds_per_year / median_delta`.
3. If neither is possible, annualized metrics are undefined.

Use a calendar year for the default beta path:

- `milliseconds_per_year = 365.2425 * 24 * 60 * 60 * 1000`

Why: the first beta is not limited to weekday equity data. A crypto-oriented
single-symbol OHLCV workflow should not silently apply a `252` trading-day
assumption unless a later API explicitly lets the user choose that convention.

The report must expose the `periods_per_year` used for annualized metrics.

Accepted fixed-duration timeframe grammar for the first beta:

- integer plus unit, with no whitespace
- units: `ms`, `s`, `m`, `h`, `d`, `w`
- `m` means minutes
- month-like tokens such as `M`, `mo`, or `month` are not fixed-duration and
  must fall back to timestamp-delta inference

Examples:

- `1m`, `5m`, `1h`, `4h`, `1d`, and `1w` are parseable.
- `1M` and `monthly` are not parseable as fixed-duration beta timeframes.

If the timeframe is not parseable and fewer than two bars are available,
annualized metrics are undefined.

When the timeframe is parseable, annualization uses the declared nominal bar
cadence. Missing bars are treated as missing observations, not as a signal to
change the declared cadence. A later elapsed-time annualization mode may be
added only if it is named separately.

### Risk-Free Rate

The beta default risk-free rate is `0.0` annualized.

If a non-zero risk-free rate is supported, it must be converted to the bar
period before Sharpe calculation:

- `period_rf = (1 + annual_risk_free_rate) ** (1 / periods_per_year) - 1`

If `periods_per_year` is unavailable, non-zero risk-free-rate metrics are
undefined rather than guessed.

### Run Identity

Run identity values are derived from the exact backtest input and execution
configuration:

- `symbol = bars.symbol`
- `timeframe = bars.timeframe`
- `start_timestamp = bars.rows[0].timestamp`
- `end_timestamp = bars.rows[-1].timestamp`
- `bar_count = len(bars.rows)`
- `initial_cash = engine.initial_cash`
- `execution_model_name = result.execution_model_name`
- `strategy_name = type(strategy).__name__` unless the user supplied a display
  name
- `strategy_display_name = strategy.display_name` when supplied, otherwise
  `None`
- `strategy_parameters = explicit public deterministic values returned by
  `strategy.parameters()`
- `run_label = user-supplied run label or None`
- `warmup_bar_count = 0` for the current beta unless a later strategy contract
  explicitly declares a warmup period
- `effective_start_timestamp = start_timestamp` for the current beta

The beta report must expose these values through a typed run manifest reachable
from `BacktestResult`. Automatic public-attribute introspection is not allowed
for strategy parameters because it can capture caches, indicator series, or
other unstable runtime state.

For an empty bar series, the implementation should reject the run before
reporting. If a later implementation allows empty results, start/end timestamp
metrics are undefined and `bar_count = 0`.

### Return And Equity Metrics

The required return and equity metrics use these formulas:

- `final_equity = equity[-1]`
- `equity_peak = max(equity)`
- `total_return = final_equity / initial_cash - 1`
- `final_balance = final_state.cash`
- `gross_realized_pnl = gross realized price PnL before fees`
- `net_realized_pnl = realized PnL after allocated entry and exit fees`
- `unrealized_pnl = final_state.unrealized_pnl`

The report must show both fee-excluded and fee-included realized PnL. Human
readable output should make net realized PnL the primary realized outcome while
also showing gross realized PnL and total fees so fee drag is visible.

Buy-and-hold comparison uses the same input bar range:

- `buy_and_hold_return = last_close / first_close - 1`
- `active_return = total_return - buy_and_hold_return`

Use `TimeBar.close` for `first_close` and `last_close`.

Why: `backtesting.py` uses a close-to-close buy-and-hold comparison, and this is
the clearest beta baseline for a user-owned OHLCV range. `quantcraft` uses the
full input range intentionally for the first beta because the current strategy
runtime does not define a strategy-level warmup contract. This differs from
`backtesting.py` when indicator warmup shifts its first trading bar.

A later warmup-aware or execution-price-aware benchmark can be added only if it
is named separately.

If `first_close <= 0`, buy-and-hold metrics are undefined.

### Annual Return And Volatility Metrics

Annualized return for beta reporting is CAGR over the periodic equity return
series:

- `ending_growth = final_equity / initial_cash`
- `years = n / periods_per_year`
- `annualized_return = ending_growth ** (1 / years) - 1`

If `n == 0`, `periods_per_year` is unavailable, or `years <= 0`,
`annualized_return` is undefined. If `ending_growth == 0`, annualized return is
`-1.0`. If `ending_growth < 0`, annualized return is undefined.

Annualized volatility uses sample standard deviation of periodic equity returns:

- `volatility = sample_std(return, ddof=1) * sqrt(periods_per_year)`

If fewer than two periodic returns are available, volatility is undefined.

Why: `vectorbt`, `empyrical`, and QuantStats use this standard return-series
approach. It is simpler to explain and test than the compounded volatility
variant used internally by `backtesting.py`.

### Sharpe Ratio

Sharpe ratio uses periodic excess returns:

- `excess_return[t] = return[t] - period_rf`
- `sharpe = mean(excess_return) / sample_std(excess_return, ddof=1) * sqrt(periods_per_year)`

Edge cases:

- fewer than two periodic returns: undefined
- unavailable `periods_per_year`: undefined
- zero standard deviation and zero mean excess return: undefined
- zero standard deviation and positive mean excess return: `+inf`
- zero standard deviation and negative mean excess return: `-inf`

The report must state the annual risk-free rate used. The beta default is `0.0`.

### Drawdown Metrics

Structured drawdown values in `quantcraft` use non-negative drawdown magnitude
to preserve the current `BacktestSummary.max_drawdown` convention.

For each equity point:

- `running_peak[t] = max(equity[0:t + 1])`
- `drawdown[t] = 0` if `running_peak[t] <= 0`
- otherwise `drawdown[t] = max(1 - equity[t] / running_peak[t], 0)`

Required drawdown metrics:

- `drawdown_curve = tuple(drawdown[t])`
- `max_drawdown = max(drawdown_curve)`
- `longest_drawdown_bar_count = longest contiguous non-zero drawdown episode length`

Deferred drawdown metrics:

- `deepest_drawdown_episode_bar_count = length of the drawdown episode
  containing max_drawdown`
- `average_drawdown = mean(max drawdown of each non-zero drawdown episode)`

A drawdown episode is a contiguous range where `drawdown[t] > 0`. An unrecovered
drawdown at the end of the backtest is still a drawdown episode ending at the
last equity point.

If there are no drawdown episodes:

- `max_drawdown = 0.0`
- `average_drawdown = 0.0`
- `longest_drawdown_bar_count = 0`

Human-readable reports may display drawdown as a negative percentage for
familiarity, but structured values remain non-negative magnitudes.

### Closed-Trade Metrics

The first beta is long-only. A closed trade is created when a sell fill closes
part or all of an existing long position.

For partial closes, each closing fill is a closed-trade record for the closed
quantity. Entry cost and entry fees are allocated pro rata from the open
position.

For each closed trade:

- `gross_pnl = (exit_price - average_entry_price) * closed_quantity`
- `net_pnl = gross_pnl - allocated_entry_fee - exit_fee`
- `entry_notional = average_entry_price * closed_quantity`
- `net_return = net_pnl / (entry_notional + allocated_entry_fee)`
- `fees = allocated_entry_fee + exit_fee`
- `duration_bars = exit_bar_index - entry_bar_index + 1`

If the denominator for `net_return` is `<= 0`, that trade's return is undefined.

The closed-trade record must be persisted in public structured output. It is not
enough to keep only aggregate closed-trade PnL values.

The beta closed-trade provenance policy is weighted-average aggregate
accounting:

- `entry_price` uses the weighted average entry price of the closed quantity.
- Entry fees are allocated pro rata from the open position's fee pool.
- Multi-entry positions are reported as one aggregate position view, not FIFO
  lots.
- `entry_timestamp` is the timestamp where the aggregate open position began.
- `duration_bars = exit_bar_index - aggregate_entry_bar_index + 1`.
- `entry_tag` is the contributing entry tag when the aggregate provenance has a
  single unambiguous non-null entry tag.
- `entry_tag = None` when multiple entry tags contribute to the aggregate
  closed quantity.
- `entry_tags` preserves the contributing non-null entry tags in first
  contribution order. It is empty when no contributing entry had a tag.
- `exit_tag` is the closing order's tag.

A later lot-accounting view may add FIFO or tax-oriented reporting, but it must
be named separately. The first beta aggregate trade view must not pretend to be
a FIFO lot report.

Open positions at the end of the run:

- contribute to final equity, unrealized PnL, return, drawdown, volatility, and
  Sharpe
- do not contribute to closed-trade count, win rate, average win/loss, profit
  factor, or expectancy

### Trade Quality Metrics

Trade quality metrics are based on closed trades only.

Let:

- `closed_trade_count = len(closed_trades)`
- `winning_trades = trades where net_pnl > 0`
- `losing_trades = trades where net_pnl < 0`
- `flat_trades = trades where net_pnl == 0`
- `gross_profit = sum(net_pnl for winning_trades)`
- `gross_loss = abs(sum(net_pnl for losing_trades))`

Required formulas:

- `win_rate = len(winning_trades) / closed_trade_count`
- `average_win = mean(net_pnl of winning_trades)`
- `average_loss = abs(mean(net_pnl of losing_trades))`
- `best_trade = max(net_return of closed trades with defined net_return)`
- `worst_trade = min(net_return of closed trades with defined net_return)`
- `average_trade_return = geometric mean of closed-trade net_return values`
- `expectancy_return = arithmetic mean of closed-trade net_return values`
- `profit_factor = gross_profit / gross_loss`

For `average_trade_return`, compute:

- `growth_product = product(1 + net_return for each defined trade return)`
- `average_trade_return = growth_product ** (1 / trade_return_count) - 1`

If any `1 + net_return < 0`, `average_trade_return` is undefined. If
`growth_product == 0`, `average_trade_return = -1.0`.

Edge cases:

- no closed trades:
  - `closed_trade_count = 0`
  - `win_rate = None`
  - `average_win = None`
  - `average_loss = None`
  - `profit_factor = None`
  - `best_trade`, `worst_trade`, `average_trade_return`, and
    `expectancy_return` are `None`
- no losing trades and positive gross profit: `profit_factor = +inf`
- no losing trades and no gross profit: `profit_factor = None`
- flat trades count toward `closed_trade_count` but not wins or losses

Why: `backtesting.py` reports trade-return expectancy, while the current
`quantcraft` summary already reports net average win/loss and profit factor.
The beta report should make the distinction explicit instead of overloading one
field name.

The existing `BacktestSummary` may keep legacy zero defaults until a migration
plan changes it. The beta reporting surface must not present denominatorless
trade-quality metrics as real zero-valued observations.

### Fill And Fee Metrics

Raw fill count remains separate from closed-trade count:

- `total_fills = len(fill_log)`
- `total_fees = sum(fill.fee for fill in fill_log)`
- `fee_to_initial_cash = total_fees / initial_cash`

Fee drag over closed trades:

- `closed_trade_gross_abs_pnl = sum(abs(gross_pnl) for closed_trades)`
- `fee_to_closed_trade_gross_abs_pnl = closed_trade_fees / closed_trade_gross_abs_pnl`

If the denominator is zero, the ratio is undefined.

`closed_trade_fees` includes allocated entry fees and exit fees for closed
trades. Fees attached to still-open position inventory remain visible in
`total_fees`, but do not enter closed-trade fee ratios until that inventory is
closed.

### Exposure And Ending State

Exposure uses bar count, not wall-clock time:

- `bars_in_position = count of bars where position quantity was positive at any
  point during the bar`
- `total_bars = len(bars.rows)`
- `exposure_ratio = bars_in_position / total_bars`

If `total_bars == 0`, exposure ratio is `0.0`.

Ending state:

- `final_position_quantity = final_state.position_quantity`
- `final_average_entry_price = final_state.average_entry_price`
- `ending_state = "open"` if `final_position_quantity > 0`, otherwise `"flat"`

The first beta does not define short exposure, gross exposure, net exposure, or
leverage exposure.

If an implementation can only observe end-of-bar position state, the
implementation plan must either persist enough intrabar state to satisfy this
definition or explicitly name the narrower metric `end_of_bar_exposure_ratio`.

The implementation plan must treat exposure naming as a public contract. It must
not claim `exposure_ratio` unless the runtime persists enough evidence to count
bars where a positive position existed at any point during the bar.

## Output Experience Requirements

The beta result surface must support two user modes.

### Human-Readable Mode

The user must be able to inspect a compact report immediately after:

```python
result = engine.run(source=source, strategy=MyStrategy(), label="sma-20-50")
report = result.report
```

The canonical beta reporting entry point is the `result.report` property on the
returned `BacktestResult`. A helper-only reporting API is not sufficient for the
first beta because the first-run UX must lead users from `engine.run(...)` to
the report without requiring them to discover a separate reporting entry point.

The summary should group metrics by meaning rather than expose a flat dataclass
dump. A user should be able to scan headline return, risk, trade quality, and
ending state in one pass.

### Machine-Readable Mode

The same result must expose stable structured values for tests, notebooks, and
future optimization.

The structured container must be reachable through `result.report`. Values must
be named, deterministic, and accessible without parsing formatted text.

## Benchmark-Driven Beta Bar

For beta, `quantcraft` does not need feature parity with all of `backtesting.py`.
It does need parity with the default user expectation created by that product:

- a single run produces a rich enough performance summary
- trade statistics are visible without custom reconstruction
- equity and trade data are available for later inspection
- the reported statistics can become optimization targets in a later slice
- the reporting output is good enough to use in the quickstart

The beta reporting slice may stay narrower than `backtesting.py` in these areas:

- no plotting in this slice
- no optimizer in this slice
- no short-trade statistics
- no leverage or margin statistics
- no multi-symbol portfolio statistics
- no walk-forward or rolling-window analytics
- no HTML report generation

## Current Codebase Gap

The current `BacktestResult` already exposes:

- raw fill log as `trade_log`
- equity curve as a tuple of floats
- final trading state
- a medium `BacktestSummary`
- execution model name
- order rejection events

The beta gap is that the current result is still primarily an engine contract.
It does not yet provide run identity, timestamped equity inspection, buy-and-hold
comparison, richer drawdown/risk metrics, closed-trade inspection, or a compact
reporting experience.

The implementation plan must map where the following provenance is persisted:

- input bar metadata and close values needed for run identity and buy-and-hold
  comparison
- timestamped equity and drawdown rows
- execution assumptions from `BacktestEngine` and `CostConfig`
- strategy identity and public parameter values
- closed-trade records derived from fills and open inventory accounting

The implementation plan must implement the reporting surface as an additive
`BacktestResult.report` property, not a replacement result object. Existing
result dataclasses are constructed positionally in tests and should not be
broken accidentally by adding rich reporting fields directly to legacy
positional constructors.

Execution assumption values must use stable structured identifiers:
`order_activation_timing = "next_bar"`,
`fill_price_basis = "conservative_ohlcv"`, and
`open_position_finalization = "mark_to_market"`. Human-readable labels may be
added, but tests should target these structured values rather than prose.

## Acceptance Criteria For This Feature Slice

The later implementation is accepted only when all of the following are true:

1. A quickstart user can run one documented strategy and immediately read a
   grouped report from the returned `BacktestResult` that answers the ten user
   questions above.
2. The public result surface separates raw fills from closed-trade statistics.
3. The public result surface preserves existing summary semantics unless a
   follow-up plan explicitly migrates them.
4. Buy-and-hold comparison is computed over the same tested bar range.
5. Risk metrics document their assumptions, especially annualization and
   risk-free-rate defaults.
6. Undefined public structured metrics use `None`; infinite metrics use
   `math.inf` or `-math.inf`.
7. Reports remain deterministic for existing fixture-backed tests.
8. The reporting surface does not require paper/live, multi-symbol, shorting, or
   leverage support.
9. The reporting surface is structured enough that a later parameter-exploration
   slice can rank runs by named metrics without parsing text.
10. The implementation plan includes a product-spec promotion or synchronization
    task before code implementation is considered closed.
11. The implementation plan includes runtime-sensitive verification gates:
    `uv run poe verify` and `uv run poe verify-runtime`.
12. The beta report exposes gross and net realized PnL rather than a single
    ambiguous realized-PnL value.
13. The beta closed-trade view uses weighted-average aggregate accounting and
    does not claim FIFO lot semantics.
14. Order tags are preserved in reporting-owned fill and closed-trade rows
    without requiring `FillEvent` to grow a `tag` field in this slice.
15. The default `exposure_ratio` counts bars where a positive position existed
    at any point during the bar.

## Follow-Up Documents

This spec intentionally leaves two documents for the next planning steps:

1. Backtest result reporting test scenarios.
2. Backtest result reporting implementation plan.

The test-scenario document should translate each acceptance criterion into
concrete fixture-backed behavior. The implementation-plan document should then
map the approved public API to data structures, migration steps, and exact
files.

## Sources

- `README.md`
- `docs/product-specs/research-ergonomics.md`
- `docs/product-specs/backtest-mvp.md`
- `docs/research/libraries/backtesting-py.md`
- https://kernc.github.io/backtesting.py/doc/backtesting/backtesting.html
- https://github.com/kernc/backtesting.py
- https://www.backtrader.com/docu/order/
- https://www.backtrader.com/blog/posts/2015-10-05-multitrades/multitrades/
- https://www.quantconnect.com/docs/v2/writing-algorithms/trading-and-orders/order-management/order-tickets
- https://www.quantconnect.com/docs/v2/writing-algorithms/trading-and-orders/order-events
- https://www.tradingview.com/pine-script-docs/v5/concepts/strategies/
- https://vectorbt.dev/api/returns/nb/
- https://github.com/polakowo/vectorbt
- https://github.com/ranaroussi/quantstats
- https://github.com/quantopian/empyrical
- https://github.com/mementum/backtrader

## Generator Work Log

- Planned slice order:
  1. Confirm current repository planning format and relevant product specs.
  2. Refresh the `backtesting.py` benchmark expectation from official docs.
  3. Add the first result-reporting spec document under `docs/plans/`.
  4. Research local and cloned library sources for metric formulas:
     `backtesting.py`, `vectorbt`, `backtrader`, QuantStats, and `empyrical`.
  5. Add metric calculation semantics and edge cases to the spec.
  6. Run a four-agent read-only review fan-out across metric semantics,
     testability, document governance, and user value/DX.
  7. Synthesize material review findings and update the spec.
  8. Run repository/document verification.
- Notes:
  - This is the first of three planned documents for the reporting slice.
  - This document intentionally avoids private implementation names except where
    public API choices are now part of the user-facing contract.
  - Formula choices intentionally separate user-facing metric semantics from
    later data-structure and file-ownership decisions.
  - Subagent review found material gaps around authority placement, external
    research approval recording, strategy identity, execution assumptions,
    undefined-value representation, timestamped provenance, closed-trade record
    persistence, timeframe grammar, buy-and-hold warmup wording, drawdown
    duration semantics, exposure semantics, and average-trade versus expectancy
    duplication. The document now addresses those findings directly.
  - A second five-agent review before implementation planning found additional
    issues around runtime verification gates, drawdown naming, exposure
    evidence, realized-PnL fee basis, multi-entry trade provenance, additive
    migration safety, and execution-assumption structured identifiers. The
    auto-fixable items were applied, and the user-approved product/API
    directions are now recorded in this spec.
- Blockers or scope changes:
  - Product-spec promotion is deferred to the implementation-plan slice because
    the user explicitly asked for the first artifact to be a plan/spec document
    under the three-document planning set.
  - No human-intent blockers remain for the reviewed design decisions.
    The implementation plan still needs to choose file ownership and any
    secondary field names not fixed by this spec.

## Evaluator Review

- Findings:
  - No blocking findings for this planning-doc revision after review synthesis.
    The updated spec stays inside single-symbol historical backtesting, records
    the external research approval basis, and makes product-spec promotion an
    implementation-plan acceptance requirement.
  - Formula choices are benchmark-backed but intentionally simple: standard
    return-series formulas for annualization, volatility, and Sharpe; equity
    peak-to-trough drawdown; closed-trade net PnL/return semantics; geometric
    average trade return; and arithmetic expectancy return.
  - The spec now closes test-driving details that were previously ambiguous:
    undefined metric sentinels, timestamped equity provenance, closed-trade row
    fields, fixed-duration timeframe grammar, execution-assumption fields,
    strategy identity, and P0/P1 metric priority.
  - The spec now records the seven approved design directions: direct
    `BacktestResult` report discovery, strict result-reporting slice scope,
    gross/net realized PnL, weighted-average aggregate closed-trade accounting,
    current-slice strategy metadata with future `params` expansion, reporting
    row tag provenance, and any-position-during-bar exposure.
  - A third five-agent review after the approved decisions found no governance
    contradiction with the active plan flow, but identified missing precision in
    aggregate trade provenance and execution-assumption identifiers. The
    auto-fixable provenance details are now closed in this spec.
  - The final API/DX decisions are closed by user approval: the canonical report
    entry point is `result.report`, the current strategy metadata path is
    `BacktestEngine.run(..., label=...)` plus `Strategy.display_name` and
    `Strategy.parameters()`, and execution assumptions use the fixed structured
    identifiers `next_bar`, `conservative_ohlcv`, and `mark_to_market`.
- Fresh verification evidence after final API/DX closure:
  - `uv run poe repo-check` passed with output `repository checks passed`.
  - `uv run pytest tests/structure/docs tests/structure/repo -q` passed with
    output `63 passed`.
- Final disposition:
  - Accepted as the first result-reporting planning artifact after subagent
    review synthesis.
