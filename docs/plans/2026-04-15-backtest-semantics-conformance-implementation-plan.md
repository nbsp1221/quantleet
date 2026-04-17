# Backtest Limit-Semantics Conformance Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Bring the shipped backtest runtime into conformance with the conservative limit-order execution contract without moving bar-aware logic into the shared `trading` matcher.

**Architecture:** Keep `quantcraft.trading` as a generic executable-event matcher and move all OHLC approximation into the `quantcraft.backtest` adapter/runtime layer. Replace the current eager four-point synthetic event tuple with per-bar decisive executable ticks derived from a canonical path, then preserve result-surface and runtime guarantees with focused integration and perf checks.

**Tech Stack:** Python 3.13, `uv`, `pytest`, Poe tasks, existing `quantcraft.backtest`, `quantcraft.trading`, and `quantcraft.research` packages

---

## Handoff Contract

Scope:
- Close the remaining limit-order conformance gap in the current backtest runtime.

Owner:
- One writer working in `src/quantcraft/backtest/*` plus the affected test and doc files listed below.

Acceptance criteria:
- Resting limit orders touched during continuous intrabar movement fill at the limit price, not the bar extreme.
- Resting limit orders crossed by a gap fill at `open`.
- The first bar has no synthetic gap segment because no real `prev_close` exists yet.
- Marketable limits at bar start fill immediately at the first executable price no worse than the limit.
- `trading.domain.matching` remains bar-agnostic.
- Non-increasing bar timestamps are still rejected before any gap/path generation.
- The default verification and runtime-sensitive verification lanes pass after the change.

Evidence required:
- Focused unit and integration red/green proof for the new limit semantics.
- Fresh `uv run poe verify`
- Fresh `uv run poe verify-runtime`

Next-step note:
- Implement semantic correctness first. Only add acceleration work if the corrected path regresses the current runtime gate.

## Current-State Analysis

The current limit-order gap is caused by the backtest adapter, not by the shared matcher.

1. [`src/quantcraft/backtest/execution_model.py`](../../src/quantcraft/backtest/execution_model.py)
   - materializes every bar as four isolated executable ticks plus a `BarEvent`
   - uses bar extrema directly as executable prices
   - cannot express “touched intrabar at the limit price” because it only emits endpoint ticks

2. [`src/quantcraft/backtest/runtime.py`](../../src/quantcraft/backtest/runtime.py)
   - consumes one eager whole-run event tuple via `events_from_bars(...)`
   - has no per-bar hook where active orders can shape decisive synthetic ticks without changing the canonical path

3. [`src/quantcraft/trading/domain/matching.py`](../../src/quantcraft/trading/domain/matching.py)
   - is intentionally generic and should stay unchanged except for tests proving the backtest layer did the right thing

4. Current tests still freeze parts of the old behavior
   - [`tests/unit/backtest/test_execution_model.py`](../../tests/unit/backtest/test_execution_model.py)
   - [`tests/integration/research/test_backtest_execution_semantics.py`](../../tests/integration/research/test_backtest_execution_semantics.py)
   - [`tests/integration/research/test_backtest_result_contract.py`](../../tests/integration/research/test_backtest_result_contract.py)

The implementation should therefore:
- add failing tests for the promoted contract first
- introduce a canonical path representation in `backtest`
- change the backtest runtime to request per-bar decisive ticks from the execution model
- rebaseline affected deterministic result contracts
- only then decide whether runtime acceleration is needed

### Task 1: Lock The Promoted Semantics With Red Tests

**Files:**
- Modify: `tests/unit/backtest/test_execution_model.py`
- Modify: `tests/integration/research/test_backtest_execution_semantics.py`
- Modify: `tests/integration/research/test_backtest_result_contract.py`
- Modify: `tests/integration/research/support_backtest_runner.py`

**Step 1: Write the failing unit tests**

Add unit coverage for:
- a resting sell limit touched on a rising intrabar segment fills at the limit price
- a resting buy limit touched on a falling intrabar segment fills at the limit price
- a resting gap-crossed limit fills at `open`
- the first bar has no synthetic gap segment and therefore no pre-history gap fill rule
- a marketable limit at bar start fills at the first executable price no worse than the limit
- non-increasing timestamps are still rejected before any gap/path generation
- no synthetic executable tick is emitted solely from a favorable bar extreme when the conservative fill should be at the limit

```python
def test_rising_segment_sell_limit_touches_at_limit_price() -> None:
    bar = TimeBar(
        timestamp=120,
        open=100.0,
        high=120.0,
        low=95.0,
        close=118.0,
        volume=10.0,
    )

    ticks = tuple(
        ConservativeOHLCVExecutionModel().tick_events_for_bar(
            symbol="BTC/USDT",
            previous_close=100.0,
            bar=bar,
            active_intents=(
                OrderIntent(
                    symbol="BTC/USDT",
                    side="sell",
                    quantity=1.0,
                    order_type="limit",
                    limit_price=110.0,
                ),
            ),
            tick_size=1.0,
        )
    )

    assert tuple(tick.bids[0][0] for tick in ticks) == (100.0, 110.0)
```

**Step 2: Run the focused unit test to verify it fails**

Run: `uv run pytest tests/unit/backtest/test_execution_model.py -q`

Expected: FAIL because `tick_events_for_bar(...)` and conservative decisive ticks do not exist yet.

**Step 3: Write the failing integration tests**

Add integration assertions covering:
- a take-profit sell limit fills at the limit price instead of the bar high
- a buy limit crossed by a gap fills at `open`
- a marketable limit activates at the next bar and fills immediately at the first executable price
- deterministic result summaries that currently rely on optimistic fill prices are updated to the promoted conservative outcome

```python
def test_backtest_runner_fills_resting_sell_limit_at_limit_price_not_bar_high() -> None:
    result = run_engine_backtest(
        bars=fixture_bar_series(),
        strategy=DeterministicEntryExitStrategy(),
        costs=CostConfig(tick_size=1.0, slippage_ticks=1.0, fee_rate=0.001),
    )

    assert tuple(fill.price for fill in result.trade_log) == (111.0, 114.0)
```

**Step 4: Run the focused integration tests to verify they fail**

Run: `uv run pytest tests/integration/research/test_backtest_execution_semantics.py tests/integration/research/test_backtest_result_contract.py -q`

Expected: FAIL on the old optimistic expectations.

**Step 5: Commit**

```bash
git add tests/unit/backtest/test_execution_model.py tests/integration/research/test_backtest_execution_semantics.py tests/integration/research/test_backtest_result_contract.py tests/integration/research/support_backtest_runner.py
git commit -m "🧪 Lock conservative backtest limit semantics"
```

### Task 2: Introduce A Canonical Path Representation In `backtest`

**Files:**
- Create: `src/quantcraft/backtest/path.py`
- Modify: `tests/unit/backtest/test_execution_model.py`

**Step 1: Write the failing path-model tests**

Cover:
- first-bar behavior uses `previous_close=None` and therefore emits no gap segment
- gap segment creation from `previous_close -> open`
- bullish intrabar route `open -> low -> high -> close`
- bearish intrabar route `open -> high -> low -> close`
- ordered decisive crossing prices for active limits along a monotonic segment

```python
def test_first_bar_has_no_gap_segment() -> None:
    segments = canonical_segments(
        previous_close=None,
        bar=TimeBar(
            timestamp=120,
            open=100.0,
            high=120.0,
            low=90.0,
            close=118.0,
            volume=10.0,
        ),
    )

    assert segments == (
        PriceSegment(start=100.0, end=90.0, kind="intrabar"),
        PriceSegment(start=90.0, end=120.0, kind="intrabar"),
        PriceSegment(start=120.0, end=118.0, kind="intrabar"),
    )


def test_canonical_segments_include_gap_then_intrabar_route() -> None:
    segments = canonical_segments(
        previous_close=95.0,
        bar=TimeBar(
            timestamp=120,
            open=100.0,
            high=120.0,
            low=90.0,
            close=118.0,
            volume=10.0,
        ),
    )

    assert segments == (
        PriceSegment(start=95.0, end=100.0, kind="gap"),
        PriceSegment(start=100.0, end=90.0, kind="intrabar"),
        PriceSegment(start=90.0, end=120.0, kind="intrabar"),
        PriceSegment(start=120.0, end=118.0, kind="intrabar"),
    )
```

**Step 2: Run the focused unit test to verify it fails**

Run: `uv run pytest tests/unit/backtest/test_execution_model.py::test_canonical_segments_include_gap_then_intrabar_route -q`

Expected: FAIL because `PriceSegment` and `canonical_segments` do not exist yet.

**Step 3: Add the minimal path module**

Implement:
- `PriceSegment`
- `canonical_segments(previous_close: float | None, bar)`
- helper(s) to derive ordered decisive crossing prices for active limits on one segment

```python
@dataclass(frozen=True, slots=True)
class PriceSegment:
    start: float
    end: float
    kind: Literal["gap", "intrabar"]

    @property
    def is_rising(self) -> bool:
        return self.end > self.start
```

**Step 4: Run the unit tests to verify they pass**

Run: `uv run pytest tests/unit/backtest/test_execution_model.py -q`

Expected: PASS for the new path-shape tests while the runtime-integration tests still fail.

**Step 5: Commit**

```bash
git add src/quantcraft/backtest/path.py tests/unit/backtest/test_execution_model.py
git commit -m "feat: add canonical backtest path model"
```

### Task 3: Refactor The Execution Model To Emit Per-Bar Decisive Ticks

**Files:**
- Modify: `src/quantcraft/backtest/execution_model.py`
- Modify: `src/quantcraft/backtest/runtime.py`
- Modify: `tests/unit/backtest/test_execution_model.py`
- Modify: `tests/integration/research/test_backtest_execution_semantics.py`

**Step 1: Write the failing API-transition tests**

Cover:
- `tick_events_for_bar(... previous_close=None ...)` produces first-bar intrabar ticks without a synthetic gap
- the execution model now works one bar at a time
- the runtime no longer depends on one eager tuple of all synthetic events
- the first executable tick of the bar is always `open` when active intents must be evaluated there
- non-increasing timestamps are still rejected before per-bar gap/path generation

```python
def test_execution_model_emits_bar_local_ticks_only() -> None:
    model = ConservativeOHLCVExecutionModel()
    bar = TimeBar(
        timestamp=120,
        open=110.0,
        high=112.0,
        low=108.0,
        close=109.0,
        volume=12.0,
    )

    ticks = tuple(
        model.tick_events_for_bar(
            symbol="BTC/USDT",
            previous_close=104.0,
            bar=bar,
            active_intents=(),
            tick_size=1.0,
        )
    )

    assert ticks == ()
```

**Step 2: Run the focused tests to verify they fail**

Run: `uv run pytest tests/unit/backtest/test_execution_model.py tests/integration/research/test_backtest_execution_semantics.py -q`

Expected: FAIL because the current contract is still `events_from_bars(...)`.

**Step 3: Change the execution-model contract and runtime loop**

Refactor the model so it exposes:
- `tick_events_for_bar(symbol, previous_close: float | None, bar, active_intents, tick_size) -> Iterable[TickEvent]`
- `bar_event(bars, bar) -> BarEvent`

Refactor `_run_backtest(...)` so it:
- validates `bars.rows` are strictly increasing before starting the per-bar loop
- iterates `bars.rows` directly
- activates pending intents once before requesting decisive ticks for the bar
- feeds each decisive tick into the unchanged `match_order_intent(...)`
- emits the `BarEvent` only after tick processing
- marks the bar on `bar.close` for equity/reporting even when no decisive tick was needed

Do not add bar-aware special cases to `trading.domain.matching`.

**Step 4: Run the focused tests to verify they pass**

Run: `uv run pytest tests/unit/backtest/test_execution_model.py tests/integration/research/test_backtest_execution_semantics.py -q`

Expected: PASS for the new conservative limit tests.

**Step 5: Commit**

```bash
git add src/quantcraft/backtest/execution_model.py src/quantcraft/backtest/runtime.py tests/unit/backtest/test_execution_model.py tests/integration/research/test_backtest_execution_semantics.py
git commit -m "feat: emit conservative decisive ticks per bar"
```

### Task 4: Rebaseline Deterministic Contracts And Clarify Any Newly Materialized Rule

**Files:**
- Modify: `tests/integration/research/test_backtest_execution_semantics.py`
- Modify: `tests/integration/research/test_backtest_result_contract.py`
- Modify: `tests/integration/research/support_backtest_runner.py`
- Modify: `tests/integration/research/test_backtest_engine_entrypoints.py`
- Modify: `docs/design-docs/backtest-execution-semantics.md`

**Step 1: Write the failing deterministic-contract assertions**

Update the affected deterministic contracts so they assert the conservative outcomes now intended by the design doc.

This includes:
- revised trade-log prices
- revised final equity / total return when the old result depended on optimistic limit fills
- one exact trade-log contract for `OlderLimitThenNewerMarketExitStrategy`
- one exact summary contract for `OlderLimitThenNewerMarketExitStrategy`
- explicit coverage for any same-open ordering rule that the corrected runtime now makes visible

```python
def test_backtest_runner_produces_conservative_trade_log_and_summary() -> None:
    result = run_engine_backtest(
        bars=fixture_bar_series(),
        strategy=DeterministicEntryExitStrategy(),
    )

    assert tuple(fill.price for fill in result.trade_log) == (111.0, 114.0)
```

**Step 2: Run the focused deterministic tests to verify they fail**

Run: `uv run pytest tests/integration/research/test_backtest_execution_semantics.py tests/integration/research/test_backtest_result_contract.py tests/integration/research/test_backtest_engine_entrypoints.py -q`

Expected: FAIL until the expected summary numbers and helper strategies are updated.

**Step 3: Update the contracts and design note**

Modify:
- helper strategies/fixtures only where needed for legible semantics proofs
- deterministic result assertions to the new conservative outcomes
- the explicit same-open multi-order contracts in both:
  - `tests/integration/research/test_backtest_execution_semantics.py`
  - `tests/integration/research/test_backtest_result_contract.py`
- the design doc if the implementation makes one previously implicit rule explicit

Likely doc addition:
- when multiple already-active orders become executable at the same bar-local decisive tick, evaluation order follows the active-intent order already preserved by the runtime

**Step 4: Run the focused tests to verify they pass**

Run: `uv run pytest tests/integration/research/test_backtest_execution_semantics.py tests/integration/research/test_backtest_result_contract.py tests/integration/research/test_backtest_engine_entrypoints.py -q`

Expected: PASS

**Step 5: Commit**

```bash
git add tests/integration/research/test_backtest_execution_semantics.py tests/integration/research/test_backtest_result_contract.py tests/integration/research/support_backtest_runner.py tests/integration/research/test_backtest_engine_entrypoints.py docs/design-docs/backtest-execution-semantics.md
git commit -m "📝 Rebaseline deterministic backtest contracts"
```

### Task 5: Verify Runtime Cost, Then Add Narrow Acceleration Only If Needed

**Files:**
- Modify if needed: `src/quantcraft/backtest/path.py`
- Modify if needed: `src/quantcraft/backtest/execution_model.py`
- Modify if needed: `tests/unit/backtest/test_execution_model.py`
- Create if needed: `tests/perf/test_backtest_limit_execution_benchmark.py`
- Verify: `tests/perf/test_rsi_backtest_benchmark.py`

**Step 1: Run the runtime-sensitive lane on the correct-but-unoptimized implementation**

Run: `uv run poe verify-runtime`

Expected:
- semantic tests pass
- the existing perf gate covers the canonical market-order path only
- perf gate either still passes or exposes the specific runtime regression to fix on that canonical path

**Step 2: If the perf gate already passes, skip code changes and record that no acceleration was needed**

Evidence:
- passing `perf-check` output
- an explicit note in the implementation report that limit-heavy traversal is not currently a repo-gated perf contract unless a new benchmark is added in this slice

**Step 3: If the perf gate fails, add the smallest outcome-equivalent optimization**

Allowed examples:
- skip intrabar tick emission when no active intents exist
- derive decisive crossing prices from active limits without materializing irrelevant intermediate prices
- avoid building whole-run tuples when the runtime can consume bar-local iterables directly
- if the corrected limit path needs dedicated measurement, add a narrow advisory benchmark for persistent active limit orders without promoting it to the repo gate in the same change unless the team explicitly wants that policy change

Forbidden:
- altering the canonical path based on current orders
- turning favorable bar extremes into executable prices
- moving bar-aware fill logic into `trading`

**Step 4: Re-run unit and perf checks**

Run:
- `uv run pytest tests/unit/backtest/test_execution_model.py -q`
- `uv run pytest tests/perf/test_rsi_backtest_benchmark.py -q -x --run-perf`
- `uv run pytest tests/perf/test_backtest_limit_execution_benchmark.py -q -x --run-perf` if the new advisory benchmark was added

Expected: PASS with unchanged semantic outcomes.

**Step 5: Commit**

```bash
git add src/quantcraft/backtest/path.py src/quantcraft/backtest/execution_model.py tests/unit/backtest/test_execution_model.py
test -f tests/perf/test_backtest_limit_execution_benchmark.py && git add tests/perf/test_backtest_limit_execution_benchmark.py || true
git commit -m "⚡ Preserve backtest semantics under runtime gate"
```

## Final Verification

Run the full proof set after the last task:

```bash
uv run pytest tests/unit/backtest tests/unit/trading tests/integration/research/test_backtest_execution_semantics.py tests/integration/research/test_backtest_result_contract.py -q
uv run pytest tests/integration/research/test_canonical_rsi_contract.py tests/integration/research/test_canonical_ema_cross_contract.py tests/integration/research/test_macd_regression_contract.py -q
uv run poe verify
uv run poe verify-runtime
```

Expected:
- the promoted conservative limit-order contract is covered by both unit and integration tests
- the deterministic result surface matches the new semantics
- the repo-local default and runtime-sensitive verification bundles pass
