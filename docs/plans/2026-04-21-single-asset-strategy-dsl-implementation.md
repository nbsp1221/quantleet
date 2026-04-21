# Single-Asset Strategy DSL Implementation

- Date: 2026-04-21
- Task: Compatibility-preserving single-asset strategy helper ergonomics
- Status: `active`
- Risk class: `Tier B`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal:
  - let current single-symbol strategy authors omit `symbol` in common
    `buy()` / `sell()` calls during the active `on_bar()` callback while the
    internal runtime continues to use explicit symbol-bearing intents and
    orders, and make the shipped examples/tests prefer that symbol-free style
    except where explicit-symbol compatibility itself is under test
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/backtest-mvp.md`
  - `docs/product-specs/research-ergonomics.md`
  - `docs/design-docs/index.md`
  - `docs/design-docs/package-topology-and-naming.md`
  - `docs/design-docs/unified-strategy-runtime-design.md`
  - `docs/references/research-ergonomics-quickstart.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/DESIGN.md`
  - `docs/PLANS.md`
- Why these are governing:
  - they define the current shipped single-symbol research/backtest surface,
    the capability-first package rules, the current runtime-sensitive
    verification lane, and the approved long-lived direction that public
    strategy ergonomics may be simpler than the internal symbol-bearing kernel
- In-repo scope:
  - `src/quantcraft/research/strategy.py`
  - runtime touchpoints needed to carry the active bar symbol only inside
    current bar handling
  - unit and integration tests for additive helper behavior
  - documentation and quickstart updates for the additive UX contract
  - example, notebook, and non-symbol-focused test cleanup so the visible
    single-symbol style matches the shipped helper ergonomics
- Out-of-repo scope:
  - multi-asset strategy surfaces
  - `stop_*` orders
  - `%` sizing
  - paper/live runtime
  - changes to `OrderIntent`, runtime `Order`, or backtest matching semantics
- Tier A progression requested: `no`
- Approval record, if required:
  - None. This slice stays within Tier B `research` and `backtest`.
- Verification commands:
  - `uv run pytest tests/unit/research/test_strategy_surface.py tests/integration/research/test_backtest_execution_semantics.py tests/structure/docs/test_research_ergonomics_quickstart.py -q`
  - `uv run poe verify-runtime`
  - `uv run poe repo-check`
- Success criteria:
  - `Strategy.buy(symbol=...)` and `Strategy.sell(symbol=...)` continue to work
    unchanged
  - inside the active single-symbol `on_bar()` callback, `buy(quantity=...)`
    and `sell(quantity=...)` infer the current `bar.symbol`
  - omitting `symbol` outside the active `on_bar()` callback still fails with
    a clear error
  - internal `OrderIntent` and runtime `Order` objects remain explicit about
    symbol identity
  - docs and quickstart describe the additive behavior honestly without
    implying shipped multi-asset support
  - shipped examples, notebooks, and non-symbol-focused tests default to
    symbol-free `buy()` / `sell()` in active `on_bar()` usage
- Out of scope:
  - adding new strategy base classes
  - changing `sell()` long-only semantics
  - changing public backtest entrypoints
  - introducing a new order lifecycle or sizing model

## Evaluator Acceptance Contract

- Evaluator owner:
  - Codex
- Evaluator-owned done contract for this slice:
  - done means the public `Strategy` surface is less noisy for the current
    single-symbol workflow while all internal runtime contracts stay explicit
    and compatible
- Acceptance artifact location:
  - `docs/plans/2026-04-21-single-asset-strategy-dsl-implementation.md`
- How the generator and evaluator agreed on done before execution:
  - this is an additive ergonomics slice only; if the diff starts changing
    order semantics, matching semantics, or multi-asset architecture claims,
    it is out of scope
- Checks the evaluator will use:
  - focused unit/integration/doc tests
  - `uv run poe verify-runtime`
  - `uv run poe repo-check`
- Auto-fail conditions:
  - explicit-symbol compatibility breaks
  - symbol inference leaks outside active `on_bar()` handling
  - docs claim current support broader than the actual shipped single-symbol
    behavior

## Generator Work Log

- Planned slice order:
  - add failing tests for additive helper behavior
  - implement active-bar symbol inference with tight scope
  - update docs/examples
  - run runtime-sensitive verification
  - evaluate the diff against the plan
- Notes:
  - the older 2026-04-18 migration plan is historical guidance only; this file
    is the active authority for the current slice
- Blockers or scope changes:
  - `uv run poe verify-runtime` initially failed on a pre-existing Ruff E501 in
    `tests/structure/docs/test_system_of_record_docs.py`; fixed mechanically so
    the required gate could run cleanly from the current repo state.
  - scope extended within the same ergonomics slice to normalize examples,
    notebooks, and non-symbol-specific regression fixtures to the new preferred
    single-symbol helper style.

## Evaluator Review

- Findings:
  - No material scope drift. The implementation stays inside `research`
    ergonomics plus supporting tests/docs.
  - The additive contract is preserved: explicit `symbol=...` still works, and
    symbol inference is limited to active `on_bar()` handling.
  - The only non-feature change was a mechanical line-wrap in a structure test
    needed to satisfy the repository lint gate.
  - Follow-up cleanup normalized shipped examples, notebooks, and non-symbol-
    focused regression fixtures to the new symbol-free single-symbol style.
    Remaining explicit `symbol=...` usage is reserved for explicit-symbol
    compatibility tests and historical planning/research docs.
  - Read-only subagent review fan-out surfaced four valid improvements:
    stronger explicit-symbol compatibility assertions, an end-to-end
    symbol-free `sell()` regression, notebook/test coherence for symbol-free
    examples, and removal of one duplicate integration fixture plus one dead
    public-facing error branch. All four were applied before the final
    verification pass.
- Verification evidence:
  - `uv run pytest tests/unit/research/test_strategy_surface.py tests/integration/research/test_backtest_execution_semantics.py tests/structure/docs/test_research_ergonomics_quickstart.py tests/integration/research/test_backtest_result_contract.py tests/integration/research/test_canonical_rsi_contract.py tests/integration/research/test_canonical_limit_entry_contract.py tests/integration/research/test_canonical_limit_exit_contract.py tests/integration/research/test_canonical_limit_mixed_contract.py -q` -> `41 passed in 1.12s`
  - `uv run poe verify-runtime` -> passed
  - `uv run poe repo-check` -> `repository checks passed`
- Final disposition:
  - Accepted.
