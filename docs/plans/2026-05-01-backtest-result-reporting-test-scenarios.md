# Backtest Result Reporting Test Scenario Spec

- Date: 2026-05-01
- Task: Define contract-first test scenarios for the first-beta backtest result
  reporting slice.
- Status: `complete`
- Risk class: `Tier B`
- Requestor: User
- Owner: Codex

## Planner Contract

- Goal: Translate the result-reporting beta spec into concrete test scenarios
  before implementation starts, so tests can guard user-visible behavior instead
  of mirroring implementation details.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/PLANS.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/research-ergonomics.md`
  - `docs/product-specs/backtest-mvp.md`
  - `docs/design-docs/index.md`
  - `docs/design-docs/package-topology-and-naming.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/DESIGN.md`
  - `docs/references/testing.md`
  - `docs/plans/2026-04-30-backtest-result-reporting-spec.md`
- Why these are governing:
  - The product specs define the first-beta single-symbol backtesting target.
  - The result-reporting spec defines the reporting contract and metric
    semantics this document must test.
  - The testing reference defines the repository's test taxonomy, placement,
    naming, smoke policy, and performance policy.
  - The architecture and design docs define package boundaries and public
    surface expectations that tests must not bypass.
- In-repo scope:
  - Define unit, integration, smoke, and structure test scenarios.
  - Define fixture requirements and expected behavior categories.
  - Define edge cases for metric semantics, structured output, and report
    readability.
  - Define scenario IDs that the implementation plan can map to exact tests.
- Out-of-repo scope:
  - No package publishing.
  - No live exchange or network-backed tests.
  - No external service integration.
  - No runtime implementation changes in this slice.
- Tier A progression requested: `no`
- Approval record, if required: Tier A approval is not required. This is a
  Tier B planning document for backtest/research tests and does not change
  `trading` or `execution` code.
- External research approval record:
  - requestor: User
  - human approver: User
  - verification marker: User explicitly requested web search for testing best
    practices before this scenario document.
  - granted scope: Read-only research into testing best practices for pytest,
    unit-test quality, test pyramid balance, and brittle implementation-coupled
    test avoidance.
  - expiration: This test-scenario spec slice only.
  - audit reference: Conversation request on 2026-05-01 to research best
    practices and write the test scenario spec.
- Verification commands:
  - `uv run poe repo-check`
  - `uv run pytest tests/structure/docs tests/structure/repo -q`
- Success criteria:
  - Scenarios test public contracts, not private implementation shape.
  - P0 metric semantics from the result-reporting spec are covered by
    deterministic test scenarios.
  - Unit tests, integration tests, smoke tests, and structure tests each have a
    clear role.
  - Edge cases are explicit enough to prevent accidental metric behavior.
  - Scenarios avoid live services, wall-clock dependence, random data, and broad
    snapshots.
  - The document is specific enough for the next implementation-plan document
    to create failing tests from it.
- Out of scope:
  - Exact source files for the reporting implementation.
  - Plotting, optimization, multi-symbol, shorting, leverage, paper trading, or
    live trading tests.

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice:
  - Confirm every scenario traces to the result-reporting beta spec.
  - Confirm the document emphasizes maintainable contract tests over
    implementation-copy tests.
  - Confirm test placement follows `docs/references/testing.md`.
  - Confirm integration tests cover cross-module behavior, not only pure metric
    math.
  - Confirm no scenario requires live network access or external services.
- Acceptance artifact location: This plan's `Evaluator Review` section.
- How the generator and evaluator agreed on done before execution: The planner
  contract fixes scope, governing docs, verification commands, and non-goals
  before any test scenario is written.
- Checks the evaluator will use:
  - Manual review against the result-reporting spec.
  - Manual review against `docs/references/testing.md`.
  - `uv run poe repo-check`.
  - `uv run pytest tests/structure/docs tests/structure/repo -q`.
- Auto-fail conditions:
  - Scenarios assert internal helper names instead of user-visible behavior.
  - The scenario set covers only happy paths.
  - The scenario set stops at unit tests and omits integration behavior.
  - The document expands the first beta into multi-symbol, shorting, leverage,
    paper trading, or live trading.
  - Repository document checks fail.

## Test Philosophy

Tests for this feature are part of the product contract. They should read like
executable documentation for a Python quant user and for future agents changing
the backtesting surface.

Good tests for this slice must:

- verify behavior the user relies on, not the private code path that produced it
- use deterministic, hand-computable fixtures
- name the scenario and expected contract in plain language
- assert exact values for counts, identities, sentinels, timestamps, and
  structured fields
- use tolerance only where floating-point math requires it
- keep human-readable report assertions resilient by checking sections and key
  labels, not an entire formatted string
- avoid broad snapshots that fail when harmless formatting changes
- include edge cases before they become production bugs
- keep fixture setup local unless it is truly shared across many tests

The test portfolio should follow a pyramid-shaped balance: many focused unit
tests for pure metric semantics, fewer integration tests that run the real
backtest path, and a small smoke layer that proves the public first-run
experience still works.

High-level integration failures should usually imply a missing focused test. If
an integration scenario finds a bug, the fix should add or update the smallest
contract test that would have caught the same behavior earlier.

## Proposed Test Placement

The implementation plan may refine exact filenames, but the first-beta
reporting tests should follow this placement unless a better repository-local
owner path exists by then:

- `tests/unit/backtest/test_result_reporting_metrics.py`
  - pure metric formulas and edge cases
- `tests/unit/backtest/test_result_reporting_records.py`
  - closed-trade rows, equity rows, structured sentinels, and value containers
- `tests/integration/research/test_backtest_result_reporting_contract.py`
  - real `BacktestEngine.run(...)` behavior for representative strategies
- `tests/integration/research/test_backtest_result_reporting_edge_cases.py`
  - cross-module edge cases that require engine, bars, strategy, and cost
    configuration together
- `tests/smoke/local/test_public_imports.py`
  - import and public-surface coverage for the reporting entry point
- `tests/smoke/local/test_backtest_result_reporting_quickstart.py`
  - one minimal documented first-run path from user-owned tabular data to a
    readable report, if it is not clearer to extend an existing smoke file
- `tests/structure/docs/test_backtest_result_reporting_docs.py`
  - product-spec routing, quickstart mention, and plan-to-product sync checks

Do not add root-level `tests/test_*.py` files. Do not put runtime-sensitive
reporting tests into `tests/perf` unless the implementation introduces an
explicit performance contract.

## Fixture Strategy

Fixtures should be small enough that a reviewer can recompute expected values
without running the implementation.

Preferred fixtures:

- three to eight `TimeBar` rows for unit and integration edge cases
- one canonical yearly CSV fixture only for regression or realism checks already
  covered by the current integration test pattern
- test-local strategies that produce deterministic fills:
  - no-trade strategy
  - buy-and-hold strategy with an open final position
  - single closed winning trade
  - single closed losing trade
  - flat closed trade
  - mixed win/loss trade sequence
  - partial close
  - order rejection, where the existing engine surface can produce one
  - carried-position intrabar exit that ends flat at bar close

Fixture data should avoid pandas, plotting libraries, external data downloads,
current timestamps, randomness, and live exchange adapters in the default lane.

Expected metric values should be written into the test as named expected values
or compact expected dataclasses. Avoid recomputing the same formula in the test
body, because that can copy the production bug into the assertion.

## Scenario Matrix

Scenario IDs are stable planning identifiers. The implementation plan should map
each accepted scenario to one or more concrete tests and may split scenarios
when that produces clearer tests.

### Public Surface And Quickstart

#### RR-SMOKE-001 Public Reporting Import

- Layer: smoke
- Intent: A user can import the public backtesting and reporting surface without
  reaching into private modules.
- Setup: Import `BacktestEngine`, `Strategy`, and `BarSeries` from documented
  package paths. No separate helper import is required to reach the canonical
  report from a completed run.
- Expected contract:
  - imports succeed from documented package paths
  - no private module path is needed in quickstart-like code
  - the canonical report is reachable as `result.report`
  - the import test does not instantiate live adapters or external services

#### RR-SMOKE-002 Minimal First Run Produces A Report

- Layer: smoke
- Intent: The quickstart path returns a readable and structured report after one
  local backtest.
- Setup: Three-bar or four-bar in-memory OHLCV series and one deterministic
  strategy.
- Expected contract:
  - `engine.run(...)` still returns the canonical result object
  - the reporting surface can be reached directly as `result.report`
  - the local smoke path checks reachability, not detailed metric correctness
  - no live adapter, external data, plotting stack, or broad formatted-output
    snapshot is required

#### RR-SMOKE-003 Documented First-Run Example Executes

- Layer: smoke
- Intent: The first copied reporting example remains executable for a beta user.
- Setup: The documented first-run reporting snippet or notebook cell chosen by
  the implementation plan, using `DataFrameDataSource` or the repository's
  equivalent user-owned tabular data path.
- Expected contract:
  - the example runs through the repository's local smoke or notebook validation
    lane
  - the example follows tabular data -> `engine.run(...)` -> returned
    `BacktestResult.report` access
  - the example produces a report through `result.report`
  - assertions remain limited to execution, public reachability, and a few stable
    labels; detailed report semantics stay in unit and integration tests

### Run Identity And Configuration

#### RR-INT-001 Run Identity Uses The Exact Input Dataset

- Layer: integration
- Intent: Users can compare runs without losing dataset context.
- Setup: In-memory `BarSeries` with symbol, timeframe, three timestamps, and
  deterministic close prices.
- Expected contract:
  - symbol equals the input bar series symbol
  - timeframe equals the input bar series timeframe
  - start timestamp equals the first bar timestamp
  - end timestamp equals the last bar timestamp
  - bar count equals the input row count
  - initial cash equals the engine configuration
  - execution model name is visible

#### RR-INT-002 Strategy Identity And Parameters Are Captured

- Layer: integration
- Intent: Users can distinguish parameterized runs of the same strategy family.
- Setup: A strategy with deterministic parameters exposed through
  `Strategy.parameters()`, an optional `Strategy.display_name`, and an optional
  `BacktestEngine.run(..., label=...)` value.
- Expected contract:
  - strategy class name is visible when no display name is provided
  - `Strategy.display_name` is visible when supplied
  - user-provided run label is preserved when provided and `None` when absent
  - deterministic strategy parameters are captured only when supplied through
    `Strategy.parameters()`
  - arbitrary public strategy attributes are not introspected

#### RR-INT-003 Empty Input Is Rejected Before Reporting

- Layer: integration
- Intent: Reporting should not invent identity or metrics for an empty dataset.
- Setup: Empty `BarSeries`, if the data contract permits constructing one.
- Expected contract:
  - the backtest or report creation raises the documented validation error
  - no partial report with fake start/end timestamps is returned
  - if a later API intentionally permits empty reports, start/end are `None` and
    `bar_count == 0`

### Execution Assumptions

#### RR-INT-004 Execution Settings Are Inspectable

- Layer: integration
- Intent: Users can see the assumptions that shaped the reported result.
- Setup: Engine configured with non-default `tick_size`, `slippage_ticks`, and
  `fee_rate`.
- Expected contract:
  - execution model name is visible
  - `order_activation_timing == "next_bar"`
  - `fill_price_basis == "conservative_ohlcv"`
  - `open_position_finalization == "mark_to_market"`
  - human-readable labels, if present, are not the only public contract
  - `tick_size`, `slippage_ticks`, and `fee_rate` match the run configuration
  - annual risk-free rate and periods-per-year are visible when risk metrics are
    computed

#### RR-INT-005 Order Rejections Are Reported Separately From Fills

- Layer: integration
- Intent: Rejected orders do not disappear from the research artifact.
- Setup: Deterministic strategy that submits an unaffordable or invalid order
  through the supported public strategy API.
- Expected contract:
  - raw fill count excludes rejected orders
  - rejection count matches the rejection event sequence
  - rejection rows include symbol, side, order type, reason, timestamp,
    quantity, order id if available, and tag
  - the report remains successful when the run has rejections and no fills

### Equity, Return, And Buy-And-Hold

#### RR-UNIT-001 Equity Return Series Includes The First Mark

- Layer: unit
- Intent: Risk metrics use the same return series basis across implementations.
- Setup: `initial_cash = 1000` and equity points `(1010, 1000, 1020)`.
- Expected contract:
  - first periodic return is `1010 / 1000 - 1`
  - later returns use previous equity as denominator
  - open-position unrealized PnL is already included in the equity input

#### RR-INT-006 Timestamped Equity Rows Match Input Bars

- Layer: integration
- Intent: Users can inspect and plot equity without reconstructing timestamps.
- Setup: A deterministic strategy over three or four bars.
- Expected contract:
  - equity row count equals bar count
  - row timestamps equal input bar timestamps in order
  - each equity row has `timestamp`, `equity`, and `drawdown`
  - final equity row equals final reported equity

#### RR-UNIT-002 Total Return And Active Return Use Final Equity

- Layer: unit
- Intent: Headline return semantics are stable.
- Setup: `initial_cash = 1000`, final equity `1100`, first close `100`, last
  close `105`.
- Expected contract:
  - total return is `0.10`
  - buy-and-hold return is `0.05`
  - active return is `0.05`
  - values are decimal ratios, not percentages

#### RR-UNIT-002A Equity Peak Uses The Full Equity Curve

- Layer: unit
- Intent: Peak equity is not confused with final equity.
- Setup: `initial_cash = 1000` and equity points `(1000, 1120, 1080)`.
- Expected contract:
  - final equity is `1080`
  - equity peak is `1120`
  - total return uses final equity, not peak equity
  - drawdown uses the same peak evidence

#### RR-UNIT-003 Buy-And-Hold Uses Full Input Close Range

- Layer: unit
- Intent: The beta baseline does not silently shift for strategy warmup.
- Setup: First close `100`, last close `120`, and a strategy that waits before
  trading.
- Expected contract:
  - buy-and-hold return is `0.20`
  - the value is independent of the first trade timestamp
  - no hidden warmup-adjusted start bar is used in beta reporting

#### RR-UNIT-004 Invalid Buy-And-Hold Denominator Is Undefined

- Layer: unit
- Intent: Invalid market data does not create misleading ratios.
- Setup: First close is `0` or negative.
- Expected contract:
  - buy-and-hold return is `None`
  - active return is `None` when it depends on undefined buy-and-hold return
  - structured output contains no `NaN` or string sentinel

### Annualization And Risk Metrics

#### RR-UNIT-005 Fixed-Duration Timeframes Produce Periods Per Year

- Layer: unit
- Intent: Annualized metrics are reproducible for common OHLCV timeframes.
- Setup: Timeframes `1m`, `5m`, `1h`, `4h`, `1d`, and `1w`.
- Expected contract:
  - each timeframe parses as integer plus fixed-duration unit
  - `m` means minutes
  - periods per year uses `365.2425 * 24 * 60 * 60 * 1000`
  - parsed values are exposed in the report
  - parseable timeframe cadence wins over timestamp gaps; for example, `1h`
    bars with two-hour timestamp gaps still use one-hour periods per year

#### RR-UNIT-006 Month-Like Timeframes Fall Back To Timestamp Deltas

- Layer: unit
- Intent: Monthly data is not treated as a fake fixed duration.
- Setup: Timeframes `1M`, `monthly`, or `1mo` with at least two positive
  timestamp deltas.
- Expected contract:
  - fixed-duration parser rejects month-like tokens
  - median positive timestamp delta is used when available
  - annualized metrics are `None` when no usable delta exists

#### RR-UNIT-007 Annualized Return Handles Degenerate Growth

- Layer: unit
- Intent: CAGR edge cases are explicit.
- Setup: Different final equity paths:
  - positive growth
  - zero ending growth
  - negative ending growth
  - unavailable periods per year
  - a hand-computable fixture with `initial_cash = 100`, final equity `121`,
    `n = 2`, and `periods_per_year = 2`
- Expected contract:
  - positive growth computes CAGR over `n / periods_per_year`
  - the hand-computable fixture returns `0.21`
  - zero ending growth returns `-1.0`
  - negative ending growth returns `None`
  - unavailable periods per year returns `None`

#### RR-UNIT-008 Volatility Requires At Least Two Returns

- Layer: unit
- Intent: Volatility is not reported from insufficient data.
- Setup: zero, one, and two periodic returns.
- Expected contract:
  - fewer than two returns produce `None`
  - two or more returns use sample standard deviation with `ddof=1`
  - the result is annualized by `sqrt(periods_per_year)`
  - a hand-computable fixture with returns `(0.01, 0.03)` and
    `periods_per_year = 1` returns approximately `0.0141421356`

#### RR-UNIT-009 Sharpe Handles Zero Standard Deviation

- Layer: unit
- Intent: Sharpe edge cases use deterministic typed sentinels.
- Setup: constant excess return sequences with zero, positive, and negative
  means, plus a non-constant fixture with returns `(0.01, 0.03)`,
  `periods_per_year = 1`, and zero risk-free rate.
- Expected contract:
  - zero standard deviation and zero mean returns `None`
  - zero standard deviation and positive mean returns `math.inf`
  - zero standard deviation and negative mean returns `-math.inf`
  - the non-constant fixture returns approximately `1.4142135624`
  - no public `NaN` is exposed

#### RR-UNIT-010 Non-Zero Risk-Free Rate Converts To Bar Period

- Layer: unit
- Intent: Sharpe does not subtract an annual rate directly from bar returns.
- Setup: annual risk-free rate greater than zero and known periods per year.
- Expected contract:
  - `period_rf = (1 + annual_risk_free_rate) ** (1 / periods_per_year) - 1`
  - Sharpe uses periodic excess returns
  - non-zero risk-free metrics are `None` when periods per year is unavailable

### Drawdown

#### RR-UNIT-011 Monotonic Equity Has No Drawdown

- Layer: unit
- Intent: Increasing equity does not create spurious risk.
- Setup: equity `(1000, 1010, 1020)`.
- Expected contract:
  - drawdown curve is all zeros
  - max drawdown is `0.0`
  - `longest_drawdown_bar_count` is `0`

#### RR-UNIT-012 Drawdown Is Non-Negative Magnitude

- Layer: unit
- Intent: Structured drawdown follows the `quantcraft` convention.
- Setup: equity `(1000, 900, 950, 1100)`.
- Expected contract:
  - drawdown values are non-negative
  - max drawdown is `0.10`
  - human-readable output may render a negative percentage, but structured data
    remains non-negative

#### RR-UNIT-013 Longest Drawdown Episode Is Distinct From Deepest Episode

- Layer: unit
- Intent: The beta metric means longest contiguous non-zero drawdown episode.
- Setup: equity path with one short deep drawdown and one longer shallow
  drawdown.
- Expected contract:
  - max drawdown comes from the deepest point
  - `longest_drawdown_bar_count` comes from the longest drawdown episode
  - an unrecovered drawdown ending at the final bar counts as an episode

### Closed Trades And Trade Quality

#### RR-UNIT-014 Closed Trade Rows Are Persisted

- Layer: unit
- Intent: Users can inspect trade-level evidence, not only aggregates.
- Setup: One buy fill followed by one sell fill that closes the position.
- Expected contract:
  - one closed-trade row is created
  - row includes entry timestamp, exit timestamp, quantity, entry price, exit
    price, gross PnL, net PnL, fees, net return, duration bars, entry tag,
    entry tags, and exit tag
  - raw `FillEvent` values remain separately available
  - reporting fill rows include fill facts plus `order_id`, `order_type`, and
    order tag without requiring `FillEvent.tag`

#### RR-UNIT-015 Partial Closes Use Weighted-Average Aggregate Accounting

- Layer: unit
- Intent: Partial exits produce auditable closed-trade rows without claiming FIFO
  lot semantics.
- Setup: Two entry fills that build one average-price position, followed by one
  exit fill that closes part of the position.
- Expected contract:
  - one closed-trade row is created for the closed quantity
  - entry price uses weighted average entry price
  - entry timestamp is the timestamp where the aggregate open position began
  - duration bars count from aggregate position open bar through the exit bar
  - allocated entry fee is proportional to closed quantity
  - remaining open inventory does not enter closed-trade stats
  - total fees still include all fills
  - when contributing entry tags differ, `entry_tag` is `None` and `entry_tags`
    preserves the contributing non-null tags in first-contribution order

#### RR-INT-007 Open Final Position Affects Equity But Not Closed Trades

- Layer: integration
- Intent: A buy-and-hold run reports unrealized outcome without pretending a
  closed trade occurred.
- Setup: Buy once and finish with an open long position.
- Expected contract:
  - final equity includes unrealized PnL
  - final balance remains cash-only
  - closed-trade count is zero
  - trade-quality denominatorless metrics are `None`
  - ending state is `open`

#### RR-UNIT-016 No Closed Trades Use Undefined Sentinels

- Layer: unit
- Intent: Absence of trades is not reported as zero performance.
- Setup: Empty closed-trade sequence.
- Expected contract:
  - closed-trade count is `0`
  - win rate, average win, average loss, profit factor, best trade, worst trade,
    average trade return, and expectancy return are `None`
  - existing legacy `BacktestSummary` may keep current zero defaults until a
    separate migration changes it

#### RR-UNIT-017 Win, Loss, And Flat Trades Are Classified Correctly

- Layer: unit
- Intent: Trade quality metrics do not misclassify zero-PnL trades.
- Setup: one winning, one losing, and one flat closed trade.
- Expected contract:
  - flat trade counts toward closed-trade count
  - flat trade is neither win nor loss
  - win rate uses winning trades divided by all closed trades
  - average win uses only winners
  - average loss uses only losers and is reported as positive magnitude

#### RR-UNIT-018 Profit Factor Edge Cases Are Stable

- Layer: unit
- Intent: Profit factor uses typed infinity and undefined sentinels.
- Setup: trade sets with all wins, all flat trades, all losses, and mixed
  wins/losses.
- Expected contract:
  - positive gross profit and no gross loss returns `math.inf`
  - no gross profit and no gross loss returns `None`
  - no gross profit and positive gross loss returns `0.0`
  - mixed wins/losses returns gross profit divided by absolute gross loss
  - profit factor classifies trades by net closed-trade PnL; a gross winner that
    becomes a net loser after fees is a losing trade for profit factor

#### RR-UNIT-019 Average Trade Return Differs From Expectancy Return

- Layer: unit
- Intent: Geometric and arithmetic trade-return metrics are not overloaded.
- Setup: closed-trade net returns `(0.10, -0.10)`.
- Expected contract:
  - expectancy return is arithmetic mean
  - average trade return is geometric mean
  - the two metric names remain distinct in structured output

#### RR-UNIT-020 Invalid Trade Return Denominators Are Excluded

- Layer: unit
- Intent: Bad denominators do not leak `NaN`.
- Setup: closed trade whose return denominator is zero or negative.
- Expected contract:
  - that trade's `net_return` is `None`
  - best/worst and geometric average use only defined trade returns
  - if no defined trade returns remain, return-based trade metrics are `None`

### Fees, Exposure, And Ending State

#### RR-UNIT-021 Fee Metrics Use Raw Fill Fees

- Layer: unit
- Intent: Fee drag is visible even when inventory remains open.
- Setup: fills with known entry and exit fees and `initial_cash = 1000`.
- Expected contract:
  - total fees equals the sum of raw fill fees
  - fee-to-initial-cash equals `total_fees / initial_cash`
  - closed-trade fee ratios exclude fees attached only to still-open inventory
    until that inventory closes
  - gross realized PnL and net realized PnL are both exposed
  - net realized PnL subtracts allocated closed-trade fees
  - a hand-computable partial-close fixture proves gross realized PnL, allocated
    entry fee, exit fee, closed-trade fees, total fees, net realized PnL, and
    fees left attached to open inventory

#### RR-INT-008 Exposure Counts Any Positive Position During A Bar

- Layer: integration
- Intent: Exposure reflects market participation, not only end-of-bar state.
- Setup: A strategy carries a positive position into a bar, exits intrabar, and
  is flat at that bar's close.
- Expected contract:
  - a bar with any positive position counts as exposed
  - exposure ratio equals exposed bars divided by total bars
  - a three-bar fixture with exposure during bars 2 and 3 reports
    `bars_in_position == 2`, `total_bars == 3`, and `exposure_ratio == 2 / 3`
  - satisfying this scenario requires persisted intrabar exposure evidence
  - an end-of-bar-only exposure implementation does not satisfy beta
    `exposure_ratio`

#### RR-INT-009 Ending State Is Explicit

- Layer: integration
- Intent: Users do not infer flat/open state from multiple raw fields.
- Setup: One flat-ending run and one open-ending run.
- Expected contract:
  - flat-ending run reports `ending_state == "flat"`
  - open-ending run reports `ending_state == "open"`
  - final position quantity and average entry price are visible

### Structured Output And Human-Readable Output

#### RR-UNIT-022 Structured Output Uses Typed Sentinels

- Layer: unit
- Intent: Notebooks and optimizers can consume metrics without string parsing.
- Setup: Report with undefined and infinite metrics.
- Expected contract:
  - undefined metrics are `None`
  - positive and negative infinity are `math.inf` and `-math.inf`
  - public structured output contains no `NaN`
  - public structured output contains no string sentinel such as `"n/a"`

#### RR-UNIT-023 Structured Field Names Are Stable

- Layer: unit
- Intent: Future optimization and notebook code can rank runs by metric name.
- Setup: One representative completed report.
- Expected contract:
  - P0 metric names from the result-reporting spec exist as named structured
    fields or mapping keys
  - grouped human-readable labels do not replace machine-readable names
  - structured values are available through `result.report` without parsing the
    formatted report
  - the implementation plan includes a field-name manifest for structured
    metrics not already named by the result-reporting spec

#### RR-INT-010 Human-Readable Report Is Grouped And Scan-Friendly

- Layer: integration
- Intent: A user can understand a run in one pass after `engine.run(...)`.
- Setup: Representative run with one closed trade, fees, drawdown, and an
  explicit ending state.
- Expected contract:
  - output contains grouped sections for headline return, risk, trade quality,
    costs, exposure/ending state, and execution assumptions
  - undefined metrics render as `n/a`
  - exact spacing, alignment, and full-string snapshots are not asserted
  - the output is not a raw dataclass dump

### Compatibility And Documentation Structure

#### RR-INT-011 Existing Result Semantics Remain Compatible

- Layer: integration
- Intent: Existing users and tests are not broken by adding richer reporting.
- Setup: Current deterministic backtest fixture used by
  `tests/integration/research/test_backtest_result_contract.py`.
- Expected contract:
  - current `BacktestResult` fields remain available
  - existing `BacktestSummary` zero defaults remain until an explicit migration
    plan changes them
  - new reporting surface does not require users to change existing basic
    `engine.run(...)` calls
  - the reporting surface is additive and directly discoverable from
    `BacktestResult.report`

#### RR-STRUCT-001 Product Spec Promotion Is Enforced

- Layer: structure
- Intent: The reporting contract does not remain only in transient plan docs.
- Setup: Product-spec routing after implementation.
- Expected contract:
  - durable reporting behavior is promoted or linked from the routed
    product-spec surface
  - quickstart or research ergonomics docs mention the first beta report
    experience
  - plan docs remain planning artifacts, not the only source of user-facing
    truth

#### RR-STRUCT-002 Test Layout Follows Repository Taxonomy

- Layer: structure
- Intent: New reporting tests stay discoverable and maintainable.
- Setup: Test tree after implementation.
- Expected contract:
  - unit tests live under `tests/unit`
  - integration tests live under `tests/integration`
  - local smoke tests live under `tests/smoke/local`
  - docs/repo guardrails live under `tests/structure`
  - no new root-level `tests/test_*.py` files are added

## Minimum Acceptance Set For First Implementation

The first implementation plan should treat these scenarios as the minimum
blocking test set before the result-reporting slice can be considered
beta-complete:

- `RR-SMOKE-001`
- `RR-SMOKE-002`
- `RR-SMOKE-003`
- `RR-INT-001`
- `RR-INT-002`
- `RR-INT-003`
- `RR-INT-004`
- `RR-INT-005`
- `RR-INT-006`
- `RR-INT-007`
- `RR-INT-008`
- `RR-INT-009`
- `RR-INT-010`
- `RR-INT-011`
- `RR-UNIT-001` through `RR-UNIT-023`
- `RR-STRUCT-001`
- `RR-STRUCT-002`

The implementation plan must also include runtime-sensitive verification gates:
`uv run poe verify` and `uv run poe verify-runtime`.

## Non-Goals For The Test Suite

Do not add tests in this slice for:

- plotting output
- optimizer ranking
- parameter grid search
- short trades
- leverage or margin
- multi-symbol portfolios
- paper trading or live trading
- live exchange adapters
- exact terminal alignment or full formatted report snapshots
- private helper function names unless those helpers become public contracts

## Sources

- `docs/plans/2026-04-30-backtest-result-reporting-spec.md`
- `docs/references/testing.md`
- https://docs.pytest.org/en/latest/explanation/goodpractices.html
- https://learn.microsoft.com/en-us/dotnet/core/testing/unit-testing-best-practices
- https://martinfowler.com/bliki/TestPyramid.html
- https://testing.googleblog.com/2015/01/testing-on-toilet-change-detector-tests.html

## Generator Work Log

- Planned slice order:
  1. Re-read the result-reporting beta spec.
  2. Review repository test taxonomy and existing backtest tests.
  3. Research testing best practices requested by the user.
  4. Draft unit, integration, smoke, and structure scenario matrix.
  5. Run repository/document verification.
- Notes:
  - The scenario set intentionally focuses on P0 reporting semantics.
  - The canonical report entry point is `result.report`; implementation
    planning may still choose internal filenames and non-public helper names.
  - The scenario set uses the existing `unit`, `integration`, `smoke`, and
    `structure` lanes instead of inventing a new test category.
  - A second five-agent review before implementation planning found material
    issues around smoke/integration boundary, optional P0 rejection testing,
    missing quickstart execution coverage, formula-copy risk in risk metric
    tests, intrabar exposure proof, structured field-name stability, strategy
    metadata, and additive result API migration. Auto-fixable findings were
    applied, and the user-approved directions are now reflected in the
    scenarios.
- Blockers or scope changes:
  - No human-intent blockers remain for the reviewed design decisions. The
    implementation plan still needs to choose test file mapping and any
    secondary field names not fixed by the result-reporting spec.

## Evaluator Review

- Findings:
  - No blocking findings for this planning-doc revision. The scenario matrix
    traces to the result-reporting beta spec, stays within the single-symbol
    first-beta scope, and separates unit, integration, smoke, and structure
    responsibilities.
  - The public API/DX decisions are now closed for test planning: smoke and
    integration tests target `result.report`, `BacktestEngine.run(..., label=...)`,
    `Strategy.display_name`, `Strategy.parameters()`, and the fixed execution
    assumption identifiers from the result-reporting spec.
  - The minimum acceptance set now includes empty-input and order-rejection
    reporting because current public surfaces can express both cases.
  - A third five-agent review found test gaps for `equity_peak`, structured
    execution assumptions, display-name metadata, numeric fee/PnL conservation,
    nominal annualization with timestamp gaps, net-of-fees profit factor, and
    intrabar exposure fixture feasibility. The auto-fixable gaps are now
    covered by this scenario matrix.
- Fresh verification evidence after final API/DX closure:
  - `uv run poe repo-check` passed: `repository checks passed`.
  - `uv run pytest tests/structure/docs tests/structure/repo -q` passed:
    `63 passed`.
- Final disposition:
  - Accepted for the test-scenario planning slice.
