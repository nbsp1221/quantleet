# Single-Asset Strategy DSL Migration Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a compatibility-preserving single-asset-first strategy authoring path so current `Strategy` users can omit `symbol` in common `buy()` / `sell()` calls during `on_bar()` while the internal engine keeps explicit symbol-bearing intents.

**Architecture:** Keep the current shipped `quantleet.research.Strategy` as the public base class and preserve explicit `symbol=...` support. Implement symbol inference only inside the active single-asset bar callback, so the public authoring UX gets simpler without changing the shared runtime contract or introducing multi-asset/runtime architecture work early.

**Tech Stack:** Python 3.13, strict mypy, pytest, repo-local structure/doc tests, Ruff, existing `quantleet.research` + `quantleet.backtest` runtime

---

- Date: 2026-04-18
- Task: Compatibility-preserving single-asset strategy DSL migration
- Status: `complete`
- Risk class: `Tier B`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal:
  - produce a concrete implementation plan for the next code slice that makes
    current single-asset strategy authoring less noisy without breaking the
    shipped `Strategy` API or jumping early into multi-asset/runtime work
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/backtest-mvp.md`
  - `docs/product-specs/research-ergonomics.md`
  - `docs/product-specs/data-ingestion.md`
  - `docs/references/research-ergonomics-quickstart.md`
  - `docs/design-docs/unified-strategy-runtime-design.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
- Why these are governing:
  - they define the current shipped public strategy contract, the current
    single-symbol MVP scope, the approved long-lived runtime direction, and the
    verification expectations for touching `research/strategy.py`
- In-repo scope:
  - additive migration of current `Strategy` order helpers
  - unit, integration, structure, and documentation updates needed to ship that
    migration coherently
- Out-of-repo scope:
  - `MultiAssetStrategy`
  - `Target`-first runtime output migration
  - allocator/risk engine/runtime adapter implementation
  - paper/live runtime implementation
- Tier A progression requested: `no`
- Approval record, if required:
  - None. This plan stays inside current Tier B research/backtest scope.
- Verification commands:
  - targeted TDD checks during implementation
  - `uv run pytest tests/unit/research/test_strategy_surface.py tests/integration/research/test_backtest_execution_semantics.py tests/structure/docs/test_research_ergonomics_quickstart.py tests/structure/repo/test_repository_entrypoint_docs.py -q`
  - `uv run poe verify-runtime`
  - `uv run poe repo-check`
- Success criteria:
  - current `Strategy` users can continue calling `buy(symbol=...)` and
    `sell(symbol=...)`
  - inside the active single-asset `on_bar()` context, `buy(quantity=...)` and
    `sell(quantity=...)` also work and emit `OrderIntent` with the current bar
    symbol
  - docs and quickstart examples describe the new preferred single-asset usage
    honestly, including continued explicit-symbol compatibility
  - no long-lived runtime claims are smuggled into the current shipped product
    contract
- Out of scope:
  - adding `close()`
  - renaming `Strategy`
  - adding `SingleAssetStrategy`
  - changing `OrderIntent`
  - changing `BacktestEngine`

## Evaluator Acceptance Contract

- Evaluator owner:
  - Codex
- Evaluator-owned done contract for this slice:
  - done means the current public strategy surface is simpler for single-asset
    users, while compatibility and documentation remain explicit and verifiable
- Acceptance artifact location:
  - `docs/plans/2026-04-18-single-asset-strategy-dsl-migration-plan.md`
- How the generator and evaluator agreed on done before execution:
  - the plan treats this as one narrow additive migration, not as the first
    implementation step of the entire unified runtime architecture
- Checks the evaluator will use:
  - targeted unit/integration/structure/doc tests
  - `uv run poe verify-runtime`
  - `uv run poe repo-check`
- Auto-fail conditions:
  - explicit-symbol compatibility is broken
  - docs imply current support for multi-asset/public runtime layers that do
    not exist
  - the implementation leaks symbol inference outside the active `on_bar()`
    context

## Generator Work Log

- Planned slice order:
  - freeze expected additive behavior in tests
  - implement symbol inference in `Strategy`
  - update docs and quickstart assets
  - run runtime-sensitive verification and close the slice
- Notes:
  - This plan intentionally avoids introducing new public base classes.
- Blockers or scope changes:
  - None during planning.

## Implementation Tasks

### Task 1: Freeze The Additive Strategy Contract In Tests

**Files:**
- Modify: `tests/unit/research/test_strategy_surface.py`
- Modify: `tests/integration/research/test_backtest_execution_semantics.py`
- Possibly modify: `tests/integration/research/support_backtest_runner.py`

**Step 1: Write the failing unit tests**

Add focused tests to `tests/unit/research/test_strategy_surface.py` that prove:

- `Strategy.buy(quantity=1.0)` inside `on_bar()` resolves to the current
  `bar.symbol`
- `Strategy.sell(quantity=1.0)` inside `on_bar()` resolves to the current
  `bar.symbol`
- `Strategy.buy(symbol=bar.symbol, quantity=1.0)` still works exactly as today
- omitting `symbol` outside the active `on_bar()` context still fails
- if no active symbol exists, the error is explicit and helpful

Illustrative test shapes:

```python
def test_buy_without_symbol_uses_current_bar_symbol() -> None:
    class ImplicitBuyStrategy(Strategy):
        def on_bar(self, bar: BarEvent) -> None:
            self.buy(quantity=1.0, tag="entry")

    strategy = ImplicitBuyStrategy()
    runtime = _runtime(strategy)
    runtime.handle_bar(_closed_bar(symbol="BTC/USDT"))

    assert runtime.order_state().pending == (
        OrderIntent(
            symbol="BTC/USDT",
            side="buy",
            quantity=1.0,
            order_type="market",
            tag="entry",
        ),
    )


def test_buy_without_symbol_outside_on_bar_still_fails() -> None:
    strategy = BuyOnFirstBarStrategy()

    with pytest.raises(ValueError, match="during on_bar"):
        strategy.buy(quantity=1.0)
```

**Step 2: Run unit tests to verify they fail**

Run:

```bash
uv run pytest tests/unit/research/test_strategy_surface.py -q
```

Expected:

- FAIL because `Strategy.buy()` and `Strategy.sell()` currently require
  `symbol`

**Step 3: Write the failing integration tests**

Add one end-to-end integration check in
`tests/integration/research/test_backtest_execution_semantics.py` proving that
an implicit-symbol market-entry strategy still fills on the next bar through the
public `BacktestEngine` path.

If the existing helper module keeps the tests cleaner, add a small strategy in
`tests/integration/research/support_backtest_runner.py` such as:

```python
class ImplicitSymbolBuyAndHoldStrategy(Strategy):
    def init(self) -> None:
        self._entered = False

    def on_bar(self, bar) -> None:
        if not self._entered:
            self._entered = True
            self.buy(quantity=1.0, tag="entry")
```

Then verify:

- the trade log still fills on the next bar
- the fill symbol is the series symbol

**Step 4: Run the integration test to verify it fails**

Run:

```bash
uv run pytest tests/integration/research/test_backtest_execution_semantics.py -q
```

Expected:

- FAIL because the strategy helper still requires explicit `symbol`

**Step 5: Commit**

```bash
git add tests/unit/research/test_strategy_surface.py tests/integration/research/test_backtest_execution_semantics.py tests/integration/research/support_backtest_runner.py
git commit -m "test: freeze additive single-asset strategy helper contract"
```

### Task 2: Implement Symbol Inference Without Breaking Explicit Symbol Support

**Files:**
- Modify: `src/quantleet/research/strategy.py`

**Step 1: Implement minimal runtime-state support**

Extend `Strategy` runtime state so it can remember the active symbol while
processing a closed bar.

Expected implementation shape:

```python
def _reset_runtime_state(self) -> None:
    ...
    self._active_bar_symbol: str | None = None

def _handle_bar(self, bar: BarEvent) -> None:
    if not bar.is_closed:
        raise ValueError(...)
    self._handling_bar = True
    self._active_bar_symbol = bar.symbol
    try:
        self.on_bar(bar)
    except Exception:
        self._pending_order_intents.clear()
        raise
    finally:
        self._active_bar_symbol = None
        self._handling_bar = False
```

**Step 2: Make `symbol` optional in helper signatures**

Change helper signatures to:

```python
def buy(
    self,
    *,
    quantity: float,
    symbol: str | None = None,
    order_type: OrderType = "market",
    limit_price: float | None = None,
    tag: str | None = None,
) -> None: ...
```

and the equivalent for `sell()`.

Resolve the symbol through one helper:

```python
def _resolve_order_symbol(self, symbol: str | None) -> str:
    if symbol is not None:
        return symbol
    if self._active_bar_symbol is None:
        raise ValueError("symbol is required unless the strategy is inside an active single-asset on_bar context")
    return self._active_bar_symbol
```

Important:

- keep explicit `symbol=...` support unchanged
- do not infer symbols outside the active bar callback
- do not change `OrderIntent`

**Step 3: Run the focused tests**

Run:

```bash
uv run pytest tests/unit/research/test_strategy_surface.py tests/integration/research/test_backtest_execution_semantics.py -q
```

Expected:

- PASS for the new additive behavior
- PASS for existing explicit-symbol behavior

**Step 4: Run type and lint checks for touched code**

Run:

```bash
uv run ruff check src/quantleet/research/strategy.py tests/unit/research/test_strategy_surface.py tests/integration/research/test_backtest_execution_semantics.py tests/integration/research/support_backtest_runner.py
uv run mypy src
```

Expected:

- Ruff clean
- mypy clean

**Step 5: Commit**

```bash
git add src/quantleet/research/strategy.py tests/unit/research/test_strategy_surface.py tests/integration/research/test_backtest_execution_semantics.py tests/integration/research/support_backtest_runner.py
git commit -m "feat: allow implicit symbol in single-asset strategy helpers"
```

### Task 3: Update The Shipped Docs And Quickstart To Match The Additive Contract

**Files:**
- Modify: `docs/product-specs/research-ergonomics.md`
- Modify: `docs/product-specs/data-ingestion.md`
- Modify: `docs/references/research-ergonomics-quickstart.md`
- Modify: `notebooks/research-ergonomics-quickstart.ipynb`
- Modify: `tests/structure/docs/test_research_ergonomics_quickstart.py`
- Modify: `tests/structure/repo/test_repository_entrypoint_docs.py`

**Step 1: Write the failing structure/doc tests**

Update structure tests to require the new contract language and examples.

Add assertions such as:

- research ergonomics spec explains that explicit `symbol=...` is still
  supported
- single-asset `on_bar()` examples may omit `symbol`
- quickstart examples use the simpler single-asset form
- docs do not claim `MultiAssetStrategy`, `Target`, allocator, or live runtime
  support as current shipped behavior

Illustrative assertions:

```python
assert "single-asset workflows may omit `symbol` inside `on_bar()`" in research_spec
assert "explicit `symbol=...` remains supported" in research_spec
assert "self.buy(quantity=1)" in quickstart
assert "self.sell(quantity=1)" in quickstart
```

**Step 2: Run structure/doc tests to verify they fail**

Run:

```bash
uv run pytest tests/structure/docs/test_research_ergonomics_quickstart.py tests/structure/repo/test_repository_entrypoint_docs.py -q
```

Expected:

- FAIL because current docs still say explicit `symbol` is required everywhere

**Step 3: Update docs conservatively**

Update `docs/product-specs/research-ergonomics.md` to say:

- `buy()` / `sell()` currently accept explicit `symbol=...`
- in the current single-symbol `on_bar()` workflow, they may omit `symbol`
- internal runtime intents still carry symbol explicitly

Update `docs/references/research-ergonomics-quickstart.md`,
`docs/product-specs/data-ingestion.md`, and the quickstart notebook so the
single-asset examples prefer:

```python
self.buy(quantity=1)
self.sell(quantity=1)
```

Keep one explicit example or note showing that `symbol=...` still works for
advanced/future-facing cases.

**Step 4: Run the structure/doc tests again**

Run:

```bash
uv run pytest tests/structure/docs/test_research_ergonomics_quickstart.py tests/structure/repo/test_repository_entrypoint_docs.py -q
```

Expected:

- PASS

**Step 5: Commit**

```bash
git add docs/product-specs/research-ergonomics.md docs/product-specs/data-ingestion.md docs/references/research-ergonomics-quickstart.md notebooks/research-ergonomics-quickstart.ipynb tests/structure/docs/test_research_ergonomics_quickstart.py tests/structure/repo/test_repository_entrypoint_docs.py
git commit -m "docs: promote implicit symbol single-asset strategy usage"
```

### Task 4: Run Full Runtime-Sensitive Verification And Close The Slice

**Files:**
- Review only: all files touched in Tasks 1-3

**Step 1: Run focused regression sweep**

Run:

```bash
uv run pytest tests/unit/research/test_strategy_surface.py tests/integration/research/test_backtest_execution_semantics.py tests/structure/docs/test_research_ergonomics_quickstart.py tests/structure/repo/test_repository_entrypoint_docs.py -q
```

Expected:

- PASS with no failures

**Step 2: Run the runtime-sensitive repository lane**

Run:

```bash
uv run poe verify-runtime
```

Expected:

- full correctness lane passes
- perf gate passes
- build passes
- repo-check passes
- notebook validation passes

**Step 3: Run repo-check explicitly for the final docs state**

Run:

```bash
uv run poe repo-check
```

Expected:

- `repository checks passed`

**Step 4: Evaluator review checklist**

Confirm all of the following before closing:

- current explicit-symbol examples still work unchanged
- symbol-free helpers work only inside the active single-asset `on_bar()`
  context
- docs describe the feature as additive, not as a multi-asset runtime arrival
- no current public docs imply `SingleAssetStrategy`, `MultiAssetStrategy`, or
  target-oriented runtime outputs are already shipped

**Step 5: Commit**

```bash
git add src/quantleet/research/strategy.py tests docs notebooks
git commit -m "feat: ship additive single-asset strategy helper migration"
```

## Evaluator Review

- Findings:
  - The narrowest safe next slice is not a new strategy hierarchy; it is a
    compatibility-preserving symbol-inference feature on the existing shipped
    `Strategy` surface.
  - The implementation must update docs and structure tests in the same slice,
    otherwise the repository will immediately drift between shipped behavior and
    stated contract.
  - `verify-runtime` is the right final gate because this slice touches
    `src/quantleet/research/strategy.py`, which the reliability docs already
    classify as runtime-sensitive.
- Verification evidence:
  - Planning source inspection:
    - `src/quantleet/research/strategy.py`
    - `src/quantleet/research/__init__.py`
    - `src/quantleet/backtest/strategy_runtime.py`
    - `tests/unit/research/test_strategy_surface.py`
    - `tests/integration/research/test_backtest_execution_semantics.py`
    - `tests/integration/research/support_backtest_runner.py`
    - `tests/structure/docs/test_research_ergonomics_quickstart.py`
    - `tests/structure/repo/test_repository_entrypoint_docs.py`
    - `docs/product-specs/research-ergonomics.md`
    - `docs/product-specs/data-ingestion.md`
    - `docs/references/research-ergonomics-quickstart.md`
  - Fresh planning verification:
    - `uv run poe repo-check` -> `repository checks passed`
- Final disposition:
  - Accepted as the next implementation slice.
