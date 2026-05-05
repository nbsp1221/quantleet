# Stop Limit Cross-Engine Experiment Plan

- Date: 2026-04-27
- Task: Design, execute, and promote stop-limit cross-engine backtest evidence
- Status: `complete`
- Risk class: `Tier B`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal: define a repeatable experiment that compares Quantleet stop-limit behavior against other backtesting engines, explains any differences, and promotes validated stop-limit entry behavior into Quantleet-owned regression tests.
- Governing docs:
  - [`../PLANS.md`](../PLANS.md)
  - [`../../AGENTS.md`](../../AGENTS.md)
  - [`../product-specs/stop-limit.md`](../product-specs/stop-limit.md)
  - [`2026-04-27-stop-limit-test-scenarios.md`](2026-04-27-stop-limit-test-scenarios.md)
  - [`2026-04-27-stop-limit-implementation.md`](2026-04-27-stop-limit-implementation.md)
- Why these are governing: this is a plan artifact under `docs/plans/`; the stop-limit product spec and test scenario plan define the Quantleet contract being cross-checked.
- In-repo scope:
  - write and maintain this experiment design and execution record;
  - add Quantleet-owned canonical regression tests for the three promoted stop-limit strategy shapes under `tests/support_backtest.py` and `tests/integration/research/`.
- Out-of-repo scope: create and run an isolated `/tmp` uv experiment workspace for cross-engine stop-limit comparison.
- Tier A progression requested: `no`
- Approval record, if required:
  - Requestor: user
  - Human approver: user
  - Verification marker: 2026-04-27 chat instruction, "실제로 실험을 진행, 그리고 나한테 최종 보고해줘"
  - Granted scope: create `/tmp/quantleet-stop-limit-crosscheck`, install external Python backtesting libraries with `uv`, run local experiments against the repository CSV, and report results.
  - Expiration: this experiment slice only.
  - Audit reference: this plan document.
- Verification commands:
  - `uv run poe repo-check`
  - `uv run pytest tests/integration/research/test_canonical_stop_limit_crosscheck_regression.py -q`
  - `uv run pytest tests/integration/research/test_canonical_stop_limit_crosscheck_regression.py tests/integration/research/test_canonical_stop_limit_contract.py tests/integration/research/test_stop_limit_execution_semantics.py tests/integration/research/test_backtest_execution_semantics.py -q`
  - `uv run poe verify-runtime`
- Success criteria:
  - The document names candidate strategies and libraries with source evidence.
  - The document explicitly says equal output is not the primary goal.
  - The document forbids OCO, OTO, OCOTO, bracket, and attached child-order APIs.
  - The document defines how differences will be categorized before deciding whether Quantleet is wrong.
  - The `/tmp` experiment produces Quantleet baseline outputs and external engine outputs or documented blockers.
  - The promoted tests distinguish cross-engine validated stop-limit entry fills from Quantleet-specific full-result regression snapshots.
- Out of scope:
  - Modifying production Quantleet code.
  - Searching for alpha-producing strategies.

## Experiment Thesis

This experiment is a confidence measurement, not an equality contest.

The useful result is not "every engine prints the same numbers." Different backtesting engines make different assumptions about order activation, OHLC path reconstruction, gaps, slippage, fill price improvement, and order priority. The experiment is successful when each observed difference can be traced to a known engine policy or adapter limitation. An unexplained difference is the signal that requires deeper investigation.

The experiment must compare a single `stop_limit` order primitive:

- allowed: one independent stop-limit order submitted by a strategy signal
- allowed: ordinary market or limit orders used separately for deterministic setup
- forbidden: OCO, OTO, OCOTO, bracket orders, attached stop-loss/take-profit legs, contingent child orders, or any API that cancels/manages a sibling order automatically
- forbidden: using stop-loss/take-profit abstractions as a proxy when the engine cannot submit an independent stop-limit order

## Data

Use the existing canonical CSV:

- [`../../tests/fixtures/backtest/binance_usdm_btcusdtusdt_1h_2025.csv`](../../tests/fixtures/backtest/binance_usdm_btcusdtusdt_1h_2025.csv)
- Symbol label in adapters: `BTC/USDT:USDT` when supported, otherwise a simple synthetic symbol such as `BTCUSDT`
- Timeframe: 1 hour
- OHLCV columns only
- Initial cash: `1_000_000.0`
- Quantity: fixed `1.0`
- Fees, spread, slippage: first run at zero to isolate order semantics; optional second run with Quantleet canonical costs
- Position model: long-only unless an engine requires explicit signed orders for exits

## Strategy Candidates

These strategies are selected because they exercise the stop-limit lifecycle, not because they are expected to produce alpha.

### 1. Opening Range Breakout Stop-Limit Entry

External basis:

- Tradapt describes Opening Range Breakout as a classic strategy with clear opening-range high/low entry criteria and notes a buy-stop alternative above the opening range high: <https://www.tradapt.com/resources/strategies/opening-range-breakout>

Experiment form:

- Build an opening range from the first N bars of each UTC day.
- If flat and price closes near/below the opening range high, submit one buy stop-limit entry:
  - `stop_price = opening_range_high + buffer`
  - `limit_price = stop_price + allowed_slippage_band`
- If already in position, exit using a plain market order on a simple deterministic condition, such as next-bar market exit after M bars.

Why it is useful:

- Tests stop-limit as breakout entry.
- Produces gap-through cases where trigger occurs but limit may not fill.
- Closely mirrors an existing Quantleet canonical stop-market family, but replaces only the order type.

Restrictions:

- Do not attach profit target or stop loss.
- Do not submit both long and short breakout orders at the same time as OCO.
- Use only one side in the first experiment pass.

### 2. Donchian Breakout Stop-Limit Entry

External basis:

- Donchian channels are commonly described as breakout/trend-following tools; Turtelli notes the practical decision between stop-order entries and close-based entries: <https://www.turtelli.com/articles/donchian-channels-for-traders>

Experiment form:

- Compute a Donchian upper band from the prior 20 highs.
- If flat and the entry condition appears, submit one buy stop-limit entry:
  - `stop_price = prior_20_high + buffer`
  - `limit_price = stop_price + allowed_slippage_band`
- Exit with a plain market order after a deterministic holding-period rule or an opposite-band close rule. If using the opposite-band rule, the exit must be a separate market order, not a paired stop.

Why it is useful:

- Exercises long-lived pending stop-limit entries.
- Produces triggered-but-unfilled orders that can carry across bars.
- Uses a well-known trend-following breakout shape already represented in Quantleet stop-market canonical coverage.

Restrictions:

- No pyramiding in the first pass.
- No simultaneous buy-stop and sell-stop pair.
- No attached risk orders.

### 3. Inside Bar Breakout Stop-Limit Entry

External basis:

- QuantVPS describes inside bar breakout entries as using stop orders around the mother bar high/low: <https://www.quantvps.com/blog/inside-bar-breakout-strategy>

Experiment form:

- Detect an inside bar where current high/low is inside the prior "mother" bar.
- If flat after a bullish setup, submit one buy stop-limit order:
  - `stop_price = mother_high + buffer`
  - `limit_price = stop_price + allowed_slippage_band`
- Exit with a simple market order after a fixed holding period.

Why it is useful:

- Creates tight trigger bands and many cases where OHLC path assumptions matter.
- Makes gap-through and same-bar trigger/fill differences visible.
- Simple enough to port across engines without relying on advanced order APIs.

Restrictions:

- Test bullish setup only first.
- Do not use both mother-bar high and low orders as an OCO pair.
- Do not attach stop loss below the mother bar.

## Library Candidates

The initial experiment should target at least five engines. The first five below are the primary set because their documentation exposes a stop-limit-capable order path.

### Tier 0: Anchor Cross-Check Engine

0. NautilusTrader
   - Evidence: NautilusTrader documents `STOP_LIMIT` as a first-class order type and describes emulated orders where Nautilus watches a trigger price and submits a `LIMIT` order when the condition is met.
   - Source: <https://nautilustrader.io/docs/latest/concepts/orders/>
   - Evidence: NautilusTrader backtesting docs describe `STOP_LIMIT` fill-price behavior and explicitly state that limit-type orders can rest after triggering and remain unfilled if the market does not reach the limit price.
   - Source: <https://nautilustrader.io/docs/latest/concepts/backtesting>
   - Expected adapter call: use the order factory's stop-limit path with explicit `instrument_id`, `order_side`, `quantity`, stop price, limit price, and `TriggerType` configured as close to last/trade triggering as the available data permits.
   - Known comparison risk: Nautilus has a richer event-driven, venue/account/order-emulation model than Quantleet. Adapter work may be heavier than simpler libraries, and trigger source configuration must be recorded carefully.
   - Why it is the anchor: it is philosophically closest to Quantleet's direction because it treats order semantics, emulation, backtesting, and live/paper execution as one coherent trading-engine model rather than a chart-only backtest helper.

### Tier 1: Primary Cross-Check Engines

1. Backtrader
   - Evidence: Backtrader documents `StopLimit`, where `price` is the trigger and `plimit` is the implicit limit price. Its execution note says the stop trigger uses stop matching and then turns into limit matching.
   - Source: <https://www.backtrader.com/blog/posts/2015-08-08-order-creation-execution/order-creation-execution/>
   - Expected adapter call: `self.buy(exectype=bt.Order.StopLimit, price=stop_price, plimit=limit_price, size=1.0)`
   - Known comparison risk: Backtrader applies its own OHLC price-improvement assumptions and starts matching from the next bar after order creation.

2. backtesting.py
   - Evidence: `Strategy.buy()` and `Strategy.sell()` accept both `limit` and `stop`; docs state limit, stop-limit, and stop-market orders fill when their conditions are met.
   - Source: <https://kernc.github.io/backtesting.py/doc/backtesting/backtesting.html>
   - Expected adapter call: `self.buy(size=1, stop=stop_price, limit=limit_price)`
   - Known comparison risk: short/exit behavior differs from Quantleet; docs warn that `sell()` is not necessarily a close unless configured or explicitly closed.

3. Zipline Reloaded / Zipline 3
   - Evidence: `order()` accepts `limit_price` and `stop_price`; docs state passing both is equivalent to `StopLimitOrder(limit_price, stop_price)`.
   - Source: <https://zipline.ml4trading.io/api-reference.html>
   - Expected adapter call: `order(asset, 1, limit_price=limit_price, stop_price=stop_price)`
   - Known comparison risk: asset ingestion and calendar setup may dominate adapter complexity; daily/minute-style simulation details may not match Quantleet's 1h CSV path.

4. PyAlgoTrade
   - Evidence: docs expose `enterLongStopLimit(instrument, stopPrice, limitPrice, quantity, ...)` and `enterShortStopLimit(...)`.
   - Source: <https://gbeced.github.io/pyalgotrade/docs/v0.17/html/strategy.html>
   - Expected adapter call: `enterLongStopLimit(symbol, stop_price, limit_price, 1, goodTillCanceled=True)`
   - Known comparison risk: project is archived/deprecated, but it remains valuable as an independent event-driven order-semantics baseline.

5. Lumibot
   - Evidence: docs expose simple `stop_limit` order creation and separately document advanced order classes such as bracket, OCO, and OTO.
   - Source: <https://lumibot.lumiwealth.com/strategy_methods.orders/strategies.strategy.Strategy.create_order.html>
   - Expected adapter call: create a simple order with `order_class=SIMPLE`, `order_type="stop_limit"`, `stop_price=...`, and the library's required limit field.
   - Known comparison risk: verify whether the current backtesting broker actually simulates stop-limit fills for the chosen asset type; older Lumibot PyPI documentation warned that some stop/limit backtest behavior was ignored, so this must be checked empirically before trusting results.

### Tier 2: Optional Or Fallback Engines

6. PyBroker
   - Evidence: docs support stop simulation and "setting a limit price" on stop exits.
   - Source: <https://www.pybroker.com/en/latest/notebooks/8.%20Applying%20Stops.html>
   - Use only if it can express a single independent stop-limit order without attached stop-loss/profit semantics.
   - If it requires entry-attached stops or take-profit/stop-loss lifecycle, exclude it from primary comparison.

7. QuantConnect LEAN
   - Evidence: LEAN has a `StopLimitOrder` type with `StopTriggered` and `LimitPrice`.
   - Source: <https://www.lean.io/docs/v2/lean-engine/class-reference/cs/classQuantConnect_1_1Orders_1_1StopLimitOrder.html>
   - Use only if the `/tmp` environment can run it reproducibly without excessive setup.
   - Because this may require more than a Python `uv` sandbox, keep it optional.

## Experimental Protocol

1. Create an isolated workspace under `/tmp`, for example `/tmp/quantleet-stop-limit-crosscheck`.
2. Use `uv` per engine to isolate dependencies:
   - one subdirectory per engine
   - one script per strategy per engine, or one adapter script with `--engine` and `--strategy`
3. Copy or read the canonical CSV from the repository path. Do not modify the repository fixture.
4. Normalize all adapters to emit the same JSON result schema:
   - engine name and version
   - strategy name
   - input CSV path and sha256
   - configuration: cash, quantity, fees, slippage, buffer, limit band
   - submitted orders count
   - filled orders count
   - final cash/equity/position
   - normalized fill log: timestamp, side, quantity, price, fee if available, tag if available
   - open orders at end, if available
   - engine warnings or adapter limitations
5. Run Quantleet through the same schema first.
6. Run external engines one at a time.
7. Diff each external result against Quantleet at three layers:
   - order lifecycle: submit, trigger, fill, carry, cancel/expire
   - fill log: side, timestamp, quantity, price
   - portfolio result: cash, equity, position, fees
8. Classify every difference before treating it as a bug.

## Difference Taxonomy

Each mismatch must be assigned one primary cause:

- `activation_timing`: same-bar vs next-bar order activation.
- `trigger_direction_policy`: engine derives stop direction from side, while Quantleet derives from stop price vs last evaluated reference.
- `gap_trigger_policy`: gap-through fills at open, triggers without fill, or uses stop price.
- `post_trigger_limit_policy`: limit can fill at the trigger point, later in the same bar, only later bars, or not at all.
- `ohlc_path_policy`: engine assumes a different intra-bar sequence.
- `price_improvement_policy`: engine fills at open/better price instead of strict trigger/limit tick.
- `priority_policy`: older active orders vs newly triggered orders are ordered differently.
- `position_model_policy`: engine opens short/hedged trades where Quantleet treats flat sells as no-op.
- `fee_slippage_policy`: cost model mismatch.
- `rounding_policy`: tick size or decimal rounding mismatch.
- `adapter_limitation`: the engine API cannot express the exact independent stop-limit primitive.
- `unexplained`: requires investigation before promotion to automated tests.

## Acceptance Criteria For The Experiment

The experiment is complete when:

- NautilusTrader has either a completed run or a documented setup blocker.
- At least five total engines have either a completed run or a documented blocker.
- All three strategies have a Quantleet baseline JSON output.
- At least three external engines successfully run all three strategies.
- Every mismatch has a taxonomy label and a short explanation.
- Any `unexplained` mismatch has a reproduction row-level example from the CSV.
- No strategy uses OCO, OTO, OCOTO, bracket, or attached child-order APIs.

## Promotion Criteria For Automated Tests

Do not automatically convert all experiment cases into tests.

Promote only cases that:

- expose a clear engine-independent contract;
- map directly to the product spec;
- can be expressed with small synthetic OHLCV data; and
- are stable without depending on third-party library behavior.

Good promotion candidates:

- gap-through trigger without fill;
- trigger and fill on the same decisive point;
- trigger then limit fill later in the same bar path;
- trigger then limit fill on a later bar;
- no reuse of pre-trigger high/low;
- FIFO ordering between older active limit and newly triggered stop-limit.

Poor promotion candidates:

- exact portfolio totals from external engines;
- differences caused by library-specific slippage;
- differences caused by library-specific OHLC path inference;
- cases requiring bracket/OCO/OTO semantics.

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice:
  - Document must be present under `docs/plans/`.
  - Document must include strategy selection, library selection, experiment protocol, mismatch taxonomy, and explicit non-goals.
  - Document must cite external sources for strategy and library choices.
  - Promoted canonical tests must separate cross-engine validated stop-limit entry-fill evidence from Quantleet-specific full-result regression snapshots.
- Acceptance artifact location: this document.
- How the generator and evaluator agreed on done before execution: the slice started as an experiment document, then user-approved execution, Nautilus follow-up, and canonical test promotion were recorded as scoped approval records in this same active plan.
- Checks the evaluator will use:
  - Read the document against the user constraints.
  - Run focused canonical stop-limit regression tests.
  - Run runtime-sensitive repository verification.
- Auto-fail conditions:
  - Treating equal output as the only success criterion.
  - Using OCO, OTO, OCOTO, bracket, or attached stop-loss/take-profit as a stop-limit proxy.
  - Selecting libraries without documented stop-limit support or an explicit caveat.

## Generator Work Log

- Planned slice order:
  - Research stop-limit-capable backtesting engines.
  - Research simple strategy shapes that naturally use stop-limit order entry.
  - Write this experiment plan.
  - Run repo-check.
- Notes:
  - NautilusTrader is the anchor engine because its order model and backtesting/live execution philosophy are closest to Quantleet's intended direction.
  - Backtrader, backtesting.py, Zipline, PyAlgoTrade, and Lumibot form the remaining primary engine set.
  - PyBroker and LEAN are fallback candidates, not required first-pass engines.
  - Lumibot must be empirically checked because its current docs show simple stop-limit order construction, while older package docs warned about backtest limitations for stop/limit orders.
  - Execution workspace: `/tmp/quantleet-stop-limit-crosscheck`.
  - Generated artifacts:
    - `/tmp/quantleet-stop-limit-crosscheck/REPORT.md`
    - `/tmp/quantleet-stop-limit-crosscheck/comparison_summary.json`
    - `/tmp/quantleet-stop-limit-crosscheck/results/*.json`
  - Successful full runs:
    - Quantleet baseline: `opening_range`, `donchian`, `inside_bar`
    - `backtesting.py`: all three strategies
    - `backtrader`: all three strategies
    - `PyAlgoTrade`: all three strategies
  - Capability probes with documented setup blockers:
    - NautilusTrader 1.225.0: `STOP_LIMIT` exists; full run needs a dedicated venue/instrument/bar-subscription adapter.
    - Zipline Reloaded 3.1.1: `StopLimitOrder(limit_price, stop_price)` exists; full run needs CSV bundle/data-portal setup.
    - Lumibot 4.5.5: `Strategy.create_order` exposes `stop_price` and `stop_limit_price`; full run needs a CSV-backed broker/data adapter and SIMPLE order verification.
  - Primary result:
    - `backtesting.py` matched Quantleet fill-by-fill for all three strategies.
    - `backtrader` matched Quantleet fill-by-fill for all three strategies after adapter datetime normalization.
    - `PyAlgoTrade` differed on timed market exit behavior; first mismatches were exits, not stop-limit entries.
  - Nautilus follow-up execution approval:
    - Requestor: user
    - Human approver: user
    - Verification marker: 2026-04-27 chat instruction, "nautilus만 이번에는 본격적으로 교차검증해봐"
    - Granted scope: clone/read NautilusTrader official repository or docs under `/tmp`, install/run Nautilus with `uv`, build a Nautilus-only CSV adapter, compare its output to Quantleet, and report.
    - Expiration: Nautilus follow-up slice only.
    - Audit reference: this plan document.
  - Nautilus follow-up execution results:
    - Official source clone: `/tmp/nautilus_trader_official`
    - Adapter script: `/tmp/quantleet-stop-limit-crosscheck/scripts/run_nautilus.py`
    - Report: `/tmp/quantleet-stop-limit-crosscheck/NAUTILUS_REPORT.md`
    - Machine summary: `/tmp/quantleet-stop-limit-crosscheck/nautilus_comparison_summary.json`
    - Full runs completed for `opening_range`, `donchian`, and `inside_bar`.
    - Stop-limit BUY fills matched Quantleet for all three strategies after normalizing to the CSV's 0.1 price precision.
    - Full fills did not exactly match because Nautilus' plain market exit leg fills from `on_bar` at the current bar close, while Quantleet records the request at the next executable tick, which is the next bar open in this experiment.
    - Mismatch classification: `market_exit_policy`, not `stop_limit_policy`.
  - Canonical test promotion approval:
    - Requestor: user
    - Human approver: user
    - Verification marker: 2026-04-27 chat instruction, "이 3개의 전략을 마찬가지로 테스트 코드에 고정시킬거야"
    - Granted scope: promote the three cross-engine stop-limit strategies to in-repository canonical regression tests under `tests/support_backtest.py` and `tests/integration/research/`.
    - Expiration: canonical test promotion slice only.
    - Audit reference: this plan document.
  - Canonical test promotion acceptance target:
    - Add canonical strategy helpers for `opening_range`, `donchian`, and `inside_bar` stop-limit entries.
    - Add integration tests that pin the stop-limit entry-fill digest as cross-engine evidence.
    - Add integration tests that pin `BacktestSummary`, first/last fill samples, and full trade-log digest as Quantleet-owned regression snapshots.
    - Keep external-engine outputs out of the assertions; external engines remain evidence, while Quantleet's public result contract is the durable test artifact.
  - Canonical test promotion implementation:
    - Added `tests/integration/research/test_canonical_stop_limit_crosscheck_regression.py`.
    - Added reusable stop-limit canonical helpers to `tests/support_backtest.py`.
    - Renamed the test intent from "cross-engine contract" to "cross-engine evidence and Quantleet full regression" after review clarified that external engines validated the entry leg, while full portfolio totals also include Quantleet-specific exit, fee, and slippage policy.
- Blockers or scope changes:
  - NautilusTrader, Zipline Reloaded, and Lumibot were not promoted from capability probes to full runs in this slice because their setup complexity is adapter-specific and not a stop-limit capability gap.

## Evaluator Review

- Findings:
  - No Quantleet stop-limit mismatch was found in the successful cross-engine runs.
  - `PyAlgoTrade` mismatches are classified as `activation_timing/market_exit_policy`; they occur on the timed market exit leg, while the initial stop-limit entries match the expected trigger prices.
  - Nautilus follow-up resolved the adapter blocker: full Nautilus runs now exist for all three strategies, and no stop-limit entry mismatch was found.
  - Subagent review found no correctness issue in the strategy helpers and confirmed the `/tmp` signal comparison had no mismatches for all three promoted strategies.
  - Subagent review found two process/test-contract issues that were fixed before final: the planner scope now includes canonical test promotion, and the promoted tests now distinguish entry-fill evidence from full Quantleet regression snapshots.
- Verification evidence:
  - `uv run poe repo-check` passed: `repository checks passed`.
  - `uv run pytest tests/integration/research/test_canonical_stop_limit_crosscheck_regression.py -q` passed: `3 passed`.
  - `uv run pytest tests/integration/research/test_canonical_stop_limit_crosscheck_regression.py tests/integration/research/test_canonical_stop_limit_contract.py tests/integration/research/test_stop_limit_execution_semantics.py tests/integration/research/test_backtest_execution_semantics.py -q` passed: `42 passed`.
  - `uv run poe verify-runtime` passed after canonical test promotion:
    - `ruff check .`: passed
    - `mypy src`: `Success: no issues found in 51 source files`
    - `pytest -q`: `451 passed, 3 skipped`
    - coverage check: `coverage policy check passed`
    - `uv build`: source distribution and wheel built successfully
    - `repo_check.py`: `repository checks passed`
    - `notebook_validate.py`: four notebooks validated
    - `pytest tests/perf/test_rsi_backtest_benchmark.py -q -x --run-perf`: `2 passed`
- Final disposition:
  - Complete. The experiment was executed in `/tmp/quantleet-stop-limit-crosscheck`, and the three promoted stop-limit strategy shapes are now covered by Quantleet-owned canonical regression tests.
