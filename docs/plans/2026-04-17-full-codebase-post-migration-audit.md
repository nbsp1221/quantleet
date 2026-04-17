# Active Plan

- Date: 2026-04-17
- Task: Full codebase post-migration audit for completion, critical defects, and remaining legacy compatibility seams
- Status: `complete`
- Risk class: `Tier A`
- Requestor: `Naki`
- Owner: Codex

## Planner Contract

- Goal:
  - audit the current repository state against the approved post-Stage-6
    capability-first architecture
  - determine whether the migration work is actually complete in code, not just
    in plans
  - identify any critical bugs, mismatches, lingering legacy compatibility
    seams, fallback code paths, or topology violations that would contradict a
    "100% complete" claim
- Governing docs:
  - [`AGENTS.md`](../../AGENTS.md)
  - [`README.md`](../../README.md)
  - [`ARCHITECTURE.md`](../../ARCHITECTURE.md)
  - [`docs/product-specs/index.md`](../product-specs/index.md)
  - [`docs/product-specs/market-data.md`](../product-specs/market-data.md)
  - [`docs/product-specs/data-ingestion.md`](../product-specs/data-ingestion.md)
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
  - [`docs/plans/2026-04-16-current-codebase-gap-analysis.md`](2026-04-16-current-codebase-gap-analysis.md)
  - [`docs/plans/2026-04-17-stage-6-legacy-trace-removal.md`](2026-04-17-stage-6-legacy-trace-removal.md)
- Why these are governing:
  - they define the approved final topology, the intended shipped public
    surface, the verification contract, the Tier A review boundary, and the
    claimed completion state that this audit must challenge
- In-repo scope:
  - full read-only audit of the current `src/`, `tests/`, `docs/`, `scripts/`,
    and notebook-backed package surface
  - architecture/topology inventory
  - residual legacy-seam detection via code search and import-surface checks
  - critical bug search focused on current shipped code, not only recent diffs
  - fresh repository verification needed to support or contradict completion
    claims
  - active-plan update with synthesized findings, verification evidence, and
    final disposition
- Out-of-repo scope:
  - new feature work
  - refactors or bug fixes beyond minimal audit instrumentation if absolutely
    required to prove a finding
  - external system validation beyond repository-local commands
- Tier A progression requested: `yes`
- Approval record, if required:
  - requestor: `Naki`
  - human approver: `Naki`
  - countersignature or equivalent verification marker:
    - explicit user instruction in the current chat on 2026-04-17 to perform a
      100% full-codebase audit, using subagent orchestration, against the codebase
      rather than only the recent changes
  - scope granted:
    - repository-local Tier A audit of `trading` and `execution` as part of the
      codebase-wide completion review
    - read-only subagent review fan-out and repository verification
  - expiration:
    - end of this audit slice
  - audit reference or sanitized audit link:
    - current chat transcript for 2026-04-17
- Verification commands:
  - architecture/inventory support:
    - `rg --files src tests docs scripts`
    - `rg -n "research\\.application|research\\.adapters|data\\.domain|quantcraft\\.exchange|from quantcraft import .*BacktestEngine|from quantcraft import .*Exchange|__getattr__|import_module\\(" src tests docs notebooks`
  - default repository lane:
    - `uv run poe verify`
  - runtime-sensitive lane:
    - `uv run poe verify-runtime`
  - repo/document lane:
    - `uv run poe repo-check`
- Success criteria:
  - the audit explicitly states whether the post-migration work is actually
    complete, partially complete, or contradicted by current code
  - any remaining legacy compatibility seams or fallback code are named with
    exact file references
  - any critical or high-severity bugs found are named with exact file
    references and concrete reasoning
  - if no such issues are found, the audit says so explicitly and names the
    residual risks that still remain
  - subagent research split and review fan-out both complete with evidence
  - all completion claims in the audit are backed by fresh command output from
    this slice
- Out of scope:
  - making the fixes themselves unless a tiny corrective patch is required to
    complete the audit artifact cleanly

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice:
  - do not grade the migration by intent or plan text; grade it by the current
    repository state
  - findings must be ordered by severity and cite concrete files
  - reviewer fan-out must challenge both "the migration is done" and "no
    legacy seam remains" claims
  - any "100% complete" conclusion must fail if code search, tests, docs, or
    public import proofs still encode removed topology or fallback behavior
- Acceptance artifact location:
  - this active plan plus the final user-facing audit report
- How the generator and evaluator agreed on done before execution:
  - done means a defensible completion judgment with evidence, not a vague
    status update
- Checks the evaluator will use:
  - topology search against final architecture claims
  - read-only subagent findings
  - reviewer fan-out findings
  - `uv run poe verify`
  - `uv run poe verify-runtime`
  - `uv run poe repo-check`
- Auto-fail conditions:
  - summary-only review without evidence
  - no explicit verdict on remaining legacy seams
  - no fresh verification evidence
  - findings that are only about the recent diff rather than current codebase state

## Generator Work Log

- Planned slice order:
  1. inventory current repository topology and current legacy-signature strings
  2. run read-only research split with disjoint scopes
  3. synthesize a first-pass finding set
  4. run fresh verification commands
  5. run review fan-out on the audit conclusions
  6. update this plan with findings and final disposition
- Notes:
  - this is an audit slice, not an implementation slice
  - no `git add`; staging remains human-only
  - subagent use should remain read-only and evidence-bearing
- Blockers or scope changes:
  - 2026-04-17: one review delegate incorrectly reported stale `_repo_tools.py`
    allowlist and live-smoke import issues. Local source inspection showed the
    current file already imports `Exchange` and `MarketType` from
    `quantcraft.integrations.venues.ccxt` and has
    `ALLOWED_ROOT_MODULE_DEPENDENCIES = set()`, so those candidate findings
    were rejected during synthesis.
  - 2026-04-17: reviewer fan-out surfaced two reproducible correctness holes in
    the current shipped backtest/trading API. The parent verified both locally
    before treating them as material findings.

## Evaluator Review

- Findings:
  - High: `BacktestEngine` currently accepts `initial_cash <= 0`, and the
    runtime later divides by that value when computing `total_return`.
    Evidence:
    - [src/quantcraft/backtest/engine.py](../../src/quantcraft/backtest/engine.py)
      exposes `initial_cash` with no validation.
    - [src/quantcraft/backtest/runtime.py](../../src/quantcraft/backtest/runtime.py)
      computes `total_return = round((state.equity - initial_cash) / initial_cash, 12)`.
    - Fresh local reproduction during this audit:
      - `uv run python - <<'PY' ... BacktestEngine(initial_cash=0.0, ...) ...`
      - result: `ZeroDivisionError float division by zero`
    Why this matters:
    - this is a current correctness hole in the public backtest API, not merely
      a migration/doc issue.
  - High: `CostConfig` accepts negative values, and current matching/state code
    turns them into better-than-market fills and negative fees.
    Evidence:
    - [src/quantcraft/trading/domain/costs.py](../../src/quantcraft/trading/domain/costs.py)
      is an unconstrained dataclass.
    - [src/quantcraft/trading/domain/matching.py](../../src/quantcraft/trading/domain/matching.py)
      applies `slippage = costs.tick_size * costs.slippage_ticks` and
      `fee = round(fill_price * intent.quantity * costs.fee_rate, 12)` with no
      non-negative validation.
    - Fresh local reproduction during this audit:
      - `uv run python - <<'PY' ... CostConfig(tick_size=1.0, slippage_ticks=-2.0, fee_rate=-0.01) ...`
      - result:
        `FillEvent(symbol='BTC/USDT', side='buy', quantity=1.0, price=99.0, timestamp=1, fee=-0.99)`
    Why this matters:
    - this lets a caller create optimistic fills and negative fees through the
      current public backtest/trading API.
  - Medium: the migration cannot honestly be called `100% complete` yet because
    the governing docs still describe the repository as only partially aligned
    and the product spec still records an open backtest conformance gap.
    Evidence:
    - [README.md](../../README.md): “the current codebase now largely follows”
    - [ARCHITECTURE.md](../../ARCHITECTURE.md): “older layer-first remnants and
      compatibility cleanup debt”
    - [docs/design-docs/quantcraft-architecture.md](../design-docs/quantcraft-architecture.md):
      “This is not a claim that current code already matches the target.”
    - [docs/design-docs/package-topology-and-naming.md](../design-docs/package-topology-and-naming.md):
      “still contains older layer-first package remnants”
    - [docs/product-specs/backtest-mvp.md](../product-specs/backtest-mvp.md):
      “open conformance gap in parts of the limit-order backtest path”
    Why this matters:
    - even if the major shim-removal work is largely done, the repository’s own
      authority docs still present the migration and one runtime semantics area
      as incomplete.
  - Medium: active architecture/repo checks still encode migration-history
    concepts rather than only enduring steady-state contracts.
    Evidence:
    - [tests/structure/architecture/test_stage1_target_package_boundaries.py](../../tests/structure/architecture/test_stage1_target_package_boundaries.py)
    - [tests/structure/architecture/test_stage4_integrations_materialization.py](../../tests/structure/architecture/test_stage4_integrations_materialization.py)
    - [tests/structure/architecture/test_stage5_local_package_flattening.py](../../tests/structure/architecture/test_stage5_local_package_flattening.py)
    - [src/quantcraft/_repo_tools.py](../../src/quantcraft/_repo_tools.py)
      still parses legacy index-status-map schemas for repo-check support
    Why this matters:
    - these are not runtime bugs, but they are residual migration/control-plane
      seams that make “fully closed” too strong.
  - Low: dead legacy test buckets still exist on disk as `__pycache__` residue.
    Evidence:
    - `tests/unit/data/domain/__pycache__/...`
    - `tests/unit/research/domain/__pycache__/...`
    Why this matters:
    - not a shipped runtime problem, but it is residual topology noise.
  - Confirmed non-finding: the old public shim modules are largely gone.
    Evidence:
    - [src/quantcraft/__init__.py](../../src/quantcraft/__init__.py) exports no
      legacy root symbols
    - [tests/smoke/local/test_public_imports.py](../../tests/smoke/local/test_public_imports.py)
      and [tests/integration/commands/test_built_artifact_imports.py](../../tests/integration/commands/test_built_artifact_imports.py)
      both assert removed legacy imports now fail
    - code search across `src`, `tests`, and non-historical docs found no
      active source/doc references that still treat
      `quantcraft.exchange`, `quantcraft.data.domain`, or
      `quantcraft.research.application` as supported current imports
- Verification evidence:
  - Inventory and seam search:
    - `rg --files src tests docs scripts notebooks`
    - `rg -n "research\\.application|research\\.adapters|data\\.domain|quantcraft\\.exchange|from quantcraft import .*BacktestEngine|from quantcraft import .*Exchange|__getattr__|import_module\\(" src tests docs scripts notebooks`
    - `rg -n "shim|compat|compatibility|legacy|fallback|deprecated|transitional" src tests README.md ARCHITECTURE.md docs/design-docs docs/product-specs docs/references docs/RELIABILITY.md docs/SECURITY.md`
    - `rg -n "research\\.application|research\\.adapters|data\\.domain|quantcraft\\.exchange" src tests README.md ARCHITECTURE.md docs/design-docs docs/product-specs docs/references docs/RELIABILITY.md`
  - Importability sweep:
    - `uv run python - <<'PY' ... pkgutil.walk_packages ... importlib.import_module(...) ...`
    - result: `FAILURES=0`
  - Reproduced correctness holes:
    - `uv run python - <<'PY' ... BacktestEngine(initial_cash=0.0, ...) ...`
      -> `ZeroDivisionError float division by zero`
    - `uv run python - <<'PY' ... CostConfig(tick_size=1.0, slippage_ticks=-2.0, fee_rate=-0.01) ...`
      -> `FillEvent(... price=99.0 ... fee=-0.99)`
  - Fresh repository verification:
    - `uv run poe verify`
      - `286 passed, 3 skipped`
      - coverage policy check passed
      - build passed
      - `repository checks passed`
      - notebook validation passed for all 4 notebooks
    - `uv run poe verify-runtime`
      - `286 passed, 3 skipped`
      - coverage policy check passed
      - build passed
      - `repository checks passed`
      - notebook validation passed
      - `perf-check` passed: `2 passed`
    - `uv run poe repo-check`
      - `repository checks passed`
  - Read-only research split:
    - `Einstein`: topology residue and seam inventory
    - `Bernoulli`: public import surface and fallback behavior
    - `Carson`: guardrail and verification risk review
  - Review fan-out:
    - `Hegel`: approved synthesis, added product-spec/doc incompleteness finding
    - `Anscombe`: approved synthesis, added migration-history test/control-plane residue finding
    - `Epicurus`: blocker, added two reproducible correctness holes
- Final disposition:
  - `Not approved as 100% complete.`
  - The post-migration architecture work is largely real: legacy public shim
    imports are mostly gone and fresh repository verification passes.
  - But the repository still has:
    - two real correctness holes in the current public backtest/trading API
    - explicit governing-doc evidence that the migration and limit-order
      semantics are not fully closed
    - residual migration/control-plane seams in active tests and repo tooling
  - Honest overall verdict:
    - `major migration work largely landed`
    - `legacy public shim surface largely removed`
    - `no, this is not yet 100% complete`
    - `two high-severity bugs remain before that claim is defensible`
