# Active Plan

- Date: 2026-04-17
- Task: Post-migration completion hardening for the remaining five material issues
- Status: `complete`
- Risk class: `Tier A`
- Requestor: `Naki`
- Owner: Codex

## Planner Contract

- Goal:
  - resolve the five material issues identified by the post-migration audits so
    the repository can honestly claim the architecture migration is complete
  - close the two correctness holes in the shipped backtest and trading API
  - remove the remaining accidental public-surface leak and migration-history
    residue
  - align governing docs with the corrected repository state
- Governing docs:
  - [`AGENTS.md`](../../AGENTS.md)
  - [`README.md`](../../README.md)
  - [`ARCHITECTURE.md`](../../ARCHITECTURE.md)
  - [`docs/product-specs/index.md`](../product-specs/index.md)
  - [`docs/product-specs/backtest.md`](../product-specs/backtest.md)
  - [`docs/product-specs/backtest-mvp.md`](../product-specs/backtest-mvp.md)
  - [`docs/product-specs/research-ergonomics.md`](../product-specs/research-ergonomics.md)
  - [`docs/design-docs/index.md`](../design-docs/index.md)
  - [`docs/design-docs/quantcraft-architecture.md`](../design-docs/quantcraft-architecture.md)
  - [`docs/design-docs/package-topology-and-naming.md`](../design-docs/package-topology-and-naming.md)
  - [`docs/RELIABILITY.md`](../RELIABILITY.md)
  - [`docs/SECURITY.md`](../SECURITY.md)
  - [`docs/DESIGN.md`](../DESIGN.md)
  - [`docs/PLANS.md`](../PLANS.md)
  - [`docs/plans/2026-04-17-full-codebase-post-migration-audit.md`](2026-04-17-full-codebase-post-migration-audit.md)
  - [`docs/plans/2026-04-17-second-pass-audit-completeness-check.md`](2026-04-17-second-pass-audit-completeness-check.md)
- Why these are governing:
  - they define the current public surface, the approved package topology, the
    repository verification contract, the Tier A boundary, and the exact audit
    findings that this hardening slice must close
- In-repo scope:
  - add semantic validation for `BacktestEngine.initial_cash`
  - add semantic validation for `CostConfig`
  - narrow the `quantcraft.integrations.venues.ccxt` public facade to the
    intended stable surface and add negative proof tests
  - replace migration-history-named structure checks and legacy control-plane
    residue with steady-state contracts where feasible in this slice
  - update governing docs so they no longer overstate transitional debt once
    the underlying issues are actually closed
  - refresh tests, smoke proofs, and built-artifact checks as needed
- Out-of-repo scope:
  - new product features
  - live exchange validation
  - unresolved limit-order semantics redesign beyond documenting any remaining
    intentional gap
- Tier A progression requested: `yes`
- Approval record, if required:
  - requestor: `Naki`
  - human approver: `Naki`
  - countersignature or equivalent verification marker:
    - explicit user instruction in the current chat on 2026-04-17 to proceed
      from the audit findings into concrete remediation planning
  - scope granted:
    - repository-local Tier A remediation planning for `trading` and
      backtest-adjacent runtime validation
    - use of read-only subagent research split and review fan-out during the
      implementation slice that will follow this plan
  - expiration:
    - end of the remediation slice that executes this plan
  - audit reference or sanitized audit link:
    - current chat transcript for 2026-04-17
- Verification commands:
  - targeted bugfix lanes:
    - `uv run pytest tests/unit/backtest tests/unit/trading tests/smoke/local/test_public_imports.py tests/integration/commands/test_built_artifact_imports.py -q`
    - `uv run pytest tests/structure/architecture tests/structure/repo -q`
  - default repository lane:
    - `uv run poe verify`
  - runtime-sensitive lane:
    - `uv run poe verify-runtime`
  - repo/document lane:
    - `uv run poe repo-check`
- Success criteria:
  - `BacktestEngine` rejects invalid `initial_cash` before runtime summary math
  - `CostConfig` rejects invalid semantic values before matching/state logic can
    create optimistic fills or negative fees
  - `quantcraft.integrations.venues.ccxt` exports only the intended public
    facade, and tests prove helper leakage is absent
  - active architecture/repo checks no longer rely on migration-stage naming or
    legacy schema compatibility where steady-state contracts can replace them
  - governing docs are updated so they do not claim transitional debt that has
    actually been removed
  - fresh verification passes and reviewer fan-out signs off on the slice
- Out of scope:
  - broad cleanup unrelated to the five audited material issues
  - redesigning unrelated APIs or extending feature scope

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice:
  - findings must be reported first and must distinguish between issues closed
    by code, issues intentionally left open, and any new issue discovered while
    fixing the audited set
  - do not claim “100% complete” unless code, tests, and governing docs all
    align on that status
  - negative assertions for removed public leaks or removed migration-history
    residue must be proven by tests or repo checks, not only by code review
- Acceptance artifact location:
  - this active plan plus the final user-facing remediation report
- How the generator and evaluator agreed on done before execution:
  - done means the known five-issue set is either closed with evidence or
    explicitly narrowed to a smaller residual set with justification
- Checks the evaluator will use:
  - targeted bugfix tests
  - structure/repo checks
  - `uv run poe verify`
  - `uv run poe verify-runtime`
  - `uv run poe repo-check`
  - read-only review fan-out
- Auto-fail conditions:
  - success claim without fresh verification
  - docs updated to say complete while code/tests still contradict that claim
  - public-surface narrowing without negative smoke/build proof
  - validation changes that silently alter semantics without corresponding tests

## Generator Work Log

- Planned slice order:
  1. write this active remediation plan
  2. audit exact current owners/tests for each of the five findings
  3. implement correctness validation fixes first
  4. narrow the `ccxt` facade and add negative proof tests
  5. replace migration-history residue in active checks with steady-state
     contract naming and logic where feasible
  6. update governing docs only after code and tests justify it
  7. run verification
  8. run review fan-out and record final disposition
- Notes:
  - no `git add`; staging remains human-only
  - fixes should prefer minimal, explicit validation and contract clarification
    over architectural churn
  - if the limit-order semantics gap remains real after code inspection, do not
    erase that warning just to make docs read “complete”
- Blockers or scope changes:
  - 2026-04-17: the `backtest-mvp` limit-order conformance-gap note remains
    real after local inspection of `src/quantcraft/backtest/execution_model.py`,
    so this slice did not remove that warning.
  - 2026-04-17: review fan-out rejected a blanket “fully complete overall”
    claim because the product-spec gap above remains open even after the
    architecture/topology residue was closed.

## Evaluator Review

- Findings:
  - Closed: `BacktestEngine` now rejects invalid `initial_cash` at
    construction time in
    [src/quantcraft/backtest/engine.py](../../src/quantcraft/backtest/engine.py).
    New targeted proof lives in
    [tests/unit/backtest/test_engine.py](../../tests/unit/backtest/test_engine.py).
  - Closed: `CostConfig` now rejects invalid semantic values at dataclass
    construction time in
    [src/quantcraft/trading/domain/costs.py](../../src/quantcraft/trading/domain/costs.py).
    New targeted proof lives in
    [tests/unit/trading/test_costs.py](../../tests/unit/trading/test_costs.py).
  - Closed: the `quantcraft.integrations.venues.ccxt` package facade now
    exports only `Exchange` and `MarketType` via
    [src/quantcraft/integrations/venues/ccxt/__init__.py](../../src/quantcraft/integrations/venues/ccxt/__init__.py),
    and negative smoke/build assertions prove helper leakage is absent in
    [tests/smoke/local/test_public_imports.py](../../tests/smoke/local/test_public_imports.py)
    and
    [tests/integration/commands/test_built_artifact_imports.py](../../tests/integration/commands/test_built_artifact_imports.py).
  - Closed: migration-history residue in active checks was reduced to
    steady-state contracts by:
    - removing legacy routing-index status-map fallback from
      [src/quantcraft/_repo_tools.py](../../src/quantcraft/_repo_tools.py)
    - replacing stage-named structure tests with steady-state topology tests:
      - [test_capability_package_roots.py](../../tests/structure/architecture/test_capability_package_roots.py)
      - [test_ccxt_integration_ownership.py](../../tests/structure/architecture/test_ccxt_integration_ownership.py)
      - [test_local_package_topology.py](../../tests/structure/architecture/test_local_package_topology.py)
  - Closed: governing architecture docs no longer describe package topology as
    an unfinished migration target:
    - [README.md](../../README.md)
    - [ARCHITECTURE.md](../../ARCHITECTURE.md)
    - [docs/design-docs/quantcraft-architecture.md](../design-docs/quantcraft-architecture.md)
    - [docs/design-docs/package-topology-and-naming.md](../design-docs/package-topology-and-naming.md)
  - Remaining material issue:
    - [docs/product-specs/backtest-mvp.md](../product-specs/backtest-mvp.md)
      still accurately documents an open limit-order backtest conformance gap.
      This slice intentionally did not change the underlying execution-model
      semantics, so an honest repository-wide “100% complete” claim is still
      premature.
- Verification evidence:
  - Red-phase proof:
    - `uv run pytest tests/unit/backtest/test_engine.py tests/unit/trading/test_costs.py tests/smoke/local/test_public_imports.py tests/integration/commands/test_built_artifact_imports.py -q`
    - result before implementation: `15 failed, 6 passed`
  - Targeted passing lanes after implementation:
    - `uv run pytest tests/unit/backtest/test_engine.py tests/unit/trading/test_costs.py tests/smoke/local/test_public_imports.py tests/integration/commands/test_built_artifact_imports.py tests/structure/architecture/test_capability_package_roots.py tests/structure/architecture/test_ccxt_integration_ownership.py tests/structure/architecture/test_local_package_topology.py tests/structure/architecture/test_backtest_runtime_hardening_boundaries.py tests/structure/repo/test_index_status_maps.py -q`
      - `42 passed in 0.86s`
    - `uv run pytest tests/unit/backtest tests/unit/trading tests/smoke/local/test_public_imports.py tests/integration/commands/test_built_artifact_imports.py -q`
      - `50 passed in 0.87s`
    - `uv run pytest tests/structure/architecture tests/structure/repo -q`
      - `88 passed in 0.30s`
    - `uv run pytest tests/structure/docs tests/structure/repo -q`
      - `60 passed in 0.18s`
  - Fresh repository verification:
    - `uv run poe verify`
      - `301 passed, 3 skipped`
    - `uv run poe verify-runtime`
      - `301 passed, 3 skipped`
      - `perf-check`: `2 passed`
    - `uv run poe repo-check`
      - `repository checks passed`
  - Read-only research split:
    - validation findings and boundaries: `Einstein`
    - ccxt public-surface recommendations: `Bernoulli`
    - guardrail/docs residue recommendations: `Carson`
  - Review fan-out:
    - `Anscombe`: `Approved: no material findings.`
    - `Epicurus`: initially found stale governance residue in
      `quantcraft-architecture.md`; parent fixed the doc before final synthesis
    - `Hegel`: confirmed one remaining material issue outside this slice's code
      changes — the still-real `backtest-mvp` limit-order conformance gap
- Final disposition:
  - `Partially approved.`
  - This slice closed four of the five audited material issues:
    1. `initial_cash` validation bug
    2. `CostConfig` semantic-validation bug
    3. accidental `ccxt` public-facade leak
    4. migration-history residue in active checks and architecture wording
  - It did **not** close the separate product-level `backtest-mvp`
    limit-order conformance gap, which remains accurately documented and still
    blocks any honest “100% complete overall” claim.
