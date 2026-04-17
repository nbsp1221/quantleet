# Active Plan

- Date: 2026-04-16
- Task: Stage 4 implementation for materializing `integrations` ownership for the current CCXT-backed exchange and historical-ingestion path
- Status: `complete`
- Risk class: `Tier B`
- Requestor: Naki
- Owner: Codex

## Planner Contract

- Goal:
  - implement Stage 4 of the approved migration baseline by making
    `quantcraft.integrations` the real owner of the current CCXT-backed venue
    protocol code
  - reduce `data` and root-level ownership of external integration logic while
    preserving the current public import surface and current product behavior
  - leave later cleanup work for Stage 5 and Stage 6 instead of prematurely
    removing compatibility shims
- Governing docs:
  - [`README.md`](../../README.md)
  - [`AGENTS.md`](../../AGENTS.md)
  - [`ARCHITECTURE.md`](../../ARCHITECTURE.md)
  - [`docs/product-specs/index.md`](../product-specs/index.md)
  - [`docs/product-specs/market-data.md`](../product-specs/market-data.md)
  - [`docs/product-specs/data-ingestion.md`](../product-specs/data-ingestion.md)
  - [`docs/design-docs/index.md`](../design-docs/index.md)
  - [`docs/design-docs/package-topology-and-naming.md`](../design-docs/package-topology-and-naming.md)
  - [`docs/RELIABILITY.md`](../RELIABILITY.md)
  - [`docs/SECURITY.md`](../SECURITY.md)
  - [`docs/plans/2026-04-16-current-codebase-gap-analysis.md`](2026-04-16-current-codebase-gap-analysis.md)
  - [`docs/plans/2026-04-16-codebase-gap-analysis-and-migration-blueprint.md`](2026-04-16-codebase-gap-analysis-and-migration-blueprint.md)
  - [`docs/plans/2026-04-16-stage-3-guardrail-widening.md`](2026-04-16-stage-3-guardrail-widening.md)
  - external reference requested by the user:
    - Anthropic, "Harness design for long-running application development"
- Why these are governing:
  - they define the approved capability-first topology, the current market-data
    and ingestion contract, the Stage 4 migration intent, the repo-local
    verification surface, and the planner/generator/evaluator protocol the user
    explicitly requested
- In-repo scope:
  - create the first real `quantcraft.integrations.venues` owner package for
    the current CCXT-backed market-data exchange logic
  - move the current CCXT-backed exchange implementation out of
    `quantcraft.data.adapters.exchange_backend` into the new canonical owner
  - keep `quantcraft.exchange` and
    `quantcraft.data.adapters.exchange_backend` as compatibility shims only
  - repoint `CCXTDataSource` and related internal callers at the canonical
    integrations owner where it improves ownership clarity
  - add or update structure/unit/smoke tests so Stage 4 proves canonical owner
    placement plus shim compatibility
  - update only the directly coupled docs or plan records needed to keep the
    repository truthful after the move
  - update this active plan with research/review synthesis and fresh
    verification evidence
- Out-of-repo scope:
  - adding execution-side broker or live-trading integrations
  - Stage 5 local package flattening
  - Stage 6 legacy path removal or deliberate breaking import cleanup
  - adding a public `apps/*` surface
- Tier A progression requested: `no`
- Approval record, if required:
  - requestor: `Naki`
  - human approver: `Naki`
  - countersignature or equivalent verification marker:
    - explicit user approval in the current chat on 2026-04-16 to create the
      Stage 4 plan, execute it immediately, use subagent orchestration, and
      read the requested Anthropic article
  - scope granted:
    - task-driven network access limited to the requested Anthropic article
    - Stage 4 ownership movement for the current CCXT-backed data integration
      path and directly coupled tests/docs
    - compatibility-shim updates required to keep the existing public import
      surface stable during this stage
  - expiration:
    - end of this Stage 4 slice
  - audit reference or sanitized audit link:
    - current chat transcript for 2026-04-16
- Verification commands:
  - targeted Stage 4 lane:
    - `uv run pytest tests/unit/data/adapters/test_ccxt_source.py tests/unit/market_data/test_exchange_fetch_ohlcv.py tests/integration/research/test_backtest_engine_entrypoints.py tests/structure/architecture/test_domain_boundaries.py tests/structure/architecture/test_stage1_target_package_boundaries.py tests/structure/architecture/test_stage4_integrations_materialization.py tests/smoke/local/test_public_imports.py tests/integration/commands/test_built_artifact_imports.py -q`
  - default repository lane:
    - `uv run poe verify`
  - stronger runtime and harness lane:
    - `uv run poe verify-runtime`
  - repo/document lane:
    - `uv run poe repo-check`
- Success criteria:
  - the current CCXT-backed exchange implementation has a canonical owner under
    `quantcraft.integrations.venues`
  - `quantcraft.data.adapters.exchange_backend` and `quantcraft.exchange` are
    compatibility shims rather than the true implementation owner
  - current public imports still work, including root `Exchange` and
    `quantcraft.data.CCXTDataSource`
  - tests prove both canonical ownership and compatibility-shim survival
  - read-only research split and review fan-out both complete with evidence and
    no material unresolved findings
- Out of scope:
  - removing compatibility exports
  - modeling non-CCXT data vendors
  - execution-side venue translation

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice:
  - Stage 4 creates a real `integrations` owner instead of only shuffling files
  - the new owner is the code path used by the current data/exchange behavior
  - compatibility shims remain shallow and behavior-neutral
  - research split and review fan-out both return evidence-bearing findings and
    are synthesized explicitly in this plan
  - completion claims are backed by fresh targeted verification, `verify`,
    `verify-runtime`, and `repo-check`
- Acceptance artifact location:
  - this active plan
- How the generator and evaluator agreed on done before execution:
  - done is canonical ownership plus preserved current behavior, not legacy
    removal
- Checks the evaluator will use:
  - diff review against the governing docs and Stage 4 scope
  - subagent evidence review
  - targeted Stage 4 lane
  - `uv run poe verify`
  - `uv run poe verify-runtime`
  - `uv run poe repo-check`
- Auto-fail conditions:
  - the canonical implementation still lives under `data` or root shims
  - compatibility shims retain non-trivial behavior instead of pure forwarding
  - Stage 4 changes public behavior or begins Stage 5/6 cleanup
  - missing research split, missing review fan-out, or missing fresh
    verification evidence

## Generator Work Log

- Planned slice order:
  1. run read-only research split for canonical owner placement, shim strategy,
     and test/verification impact
  2. synthesize the minimal Stage 4 file set and choose the canonical
     `integrations` owner shape
  3. implement the move with one writer while preserving compatibility shims
  4. run targeted verification
  5. run review fan-out, fix findings, and rerun final verification
- Notes:
  - per the user instruction, git staging remains human-only; this slice will
    not run `git add`
  - this slice follows the Anthropic harness pattern the user explicitly asked
    for: written planner contract first, single writer, separate evaluator
    stage, and evidence-bearing delegated research/review
  - read-only research split reused existing explorer/reviewer threads because
    the host thread cap prevented spawning new GPT-5.4-high workers
  - read-only research split used bounded handoff contracts with disjoint
    scopes:
    - `Nash`: canonical owner placement under `quantcraft.integrations`
    - `Turing`: compatibility and test-impact risk for the current shim paths
    - `Plato`: verification and architecture-guardrail impact
  - final Stage 4 owned file group became:
    - `src/quantcraft/integrations/venues/__init__.py`
    - `src/quantcraft/integrations/venues/ccxt/__init__.py`
    - `src/quantcraft/integrations/venues/ccxt/market_data.py`
    - `src/quantcraft/data/adapters/exchange_backend.py`
    - `src/quantcraft/exchange.py`
    - `src/quantcraft/data/adapters/ccxt_source.py`
    - `tests/unit/data/adapters/test_ccxt_source.py`
    - `tests/unit/market_data/test_exchange_fetch_ohlcv.py`
    - `tests/integration/research/test_backtest_engine_entrypoints.py`
    - `tests/structure/architecture/test_stage4_integrations_materialization.py`
    - `tests/smoke/local/test_public_imports.py`
    - `tests/integration/commands/test_built_artifact_imports.py`
    - this active plan
- Blockers or scope changes:
  - 2026-04-16: the preferred orchestration model was new GPT-5.4-high
    explorers/reviewers, but the host thread cap blocked new subagent threads;
    existing read-only explorer/reviewer threads were reused instead
  - 2026-04-16: the first targeted lane failed because the canonical owner was
    imported through `quantcraft.integrations.venues.ccxt.__init__`, which hid
    the real monkeypatch surface inside `market_data.py`; the implementation
    was narrowed so runtime imports point directly at
    `quantcraft.integrations.venues.ccxt.market_data`
  - 2026-04-16: initial reviewer fan-out found one blocker:
    runtime verification did not prove that
    `quantcraft.data.adapters.exchange_backend` still worked as a
    compatibility shim at runtime
  - 2026-04-16: that blocker was resolved by adding runtime shim assertions to
    `tests/smoke/local/test_public_imports.py` and
    `tests/integration/commands/test_built_artifact_imports.py`
  - 2026-04-16: `verify` and `verify-runtime` were briefly run in parallel and
    interfered through shared `dist/` wheel artifacts; final verification was
    rerun serially and only the serial runs are accepted as evidence

## Evaluator Review

- Findings:
- read-only research split converged on the same Stage 4 shape:
  - the canonical owner should live under
    `quantcraft.integrations.venues.ccxt.market_data`
  - `quantcraft.data.adapters.exchange_backend` and `quantcraft.exchange`
    should become forwarding compatibility shims only
  - Stage 4 did not require new scanner policy or verification-lane changes
    because Stage 3 had already widened those guardrails
- the implementation now matches that Stage 4 ownership boundary:
  - CCXT-backed venue protocol code lives in
    `src/quantcraft/integrations/venues/ccxt/market_data.py`
  - `src/quantcraft/data/adapters/exchange_backend.py` is a shim that
    re-exports the canonical owner
  - `src/quantcraft/exchange.py` is a shim that re-exports the canonical owner
  - `src/quantcraft/data/adapters/ccxt_source.py` now imports its owner-facing
    CCXT helpers from the canonical integrations path
- the first targeted run exposed one real implementation issue:
  - importing through `quantcraft.integrations.venues.ccxt.__init__` made the
    monkeypatch-heavy tests ineffective because `_fetch_ohlcv_range` still
    executed against `market_data.py` globals
  - this was corrected by pointing runtime imports and test patch points
    directly at `quantcraft.integrations.venues.ccxt.market_data`
- review fan-out produced one blocker and two clean approvals:
  - `Zeno`: Approved: no material findings.
  - `Lagrange`: Approved: no material findings.
  - `Einstein`: initial blocker on missing runtime proof for the
    `exchange_backend` shim; final result after fix: Approved.
- final Stage 4 position for this slice:
  - the current CCXT-backed data integration has a real canonical owner under
    `integrations`
  - current public imports remain stable
  - the compatibility shims are proved both structurally and at runtime
- Verification evidence:
  - Anthropic harness reference reviewed:
    - planner / generator / evaluator separation
    - written contract before edits
    - bounded handoff artifacts and separate evaluator signoff
    - source: https://www.anthropic.com/engineering/harness-design-long-running-apps
  - read-only research split:
    - `Nash`: recommended `quantcraft.integrations.venues.ccxt.market_data` as
      the canonical owner and identified Stage 4 boundaries
    - `Turing`: identified the monkeypatch/import-alias trap and the minimal
      shim/runtime proof obligations
    - `Plato`: confirmed that Stage 4 needed one new structure test but no new
      scanner or verification-lane policy
  - targeted Stage 4 lane:
    - `uv run pytest tests/unit/data/adapters/test_ccxt_source.py tests/unit/market_data/test_exchange_fetch_ohlcv.py tests/integration/research/test_backtest_engine_entrypoints.py tests/structure/architecture/test_domain_boundaries.py tests/structure/architecture/test_stage1_target_package_boundaries.py tests/structure/architecture/test_stage4_integrations_materialization.py tests/smoke/local/test_public_imports.py tests/integration/commands/test_built_artifact_imports.py -q`
    - result: `60 passed`
  - default repository verification:
    - `uv run poe verify`
    - result:
      - `294 passed, 3 skipped`
      - coverage policy check passed
      - build passed
      - repo check passed
      - notebook validation passed
  - stronger runtime verification:
    - `uv run poe verify-runtime`
    - result:
      - `294 passed, 3 skipped`
      - coverage policy check passed
      - build passed
      - repo check passed
      - notebook validation passed
      - perf check passed
  - repo verification:
    - `uv run poe repo-check`
    - result: `repository checks passed`
  - review fan-out:
    - `Zeno`: Approved: no material findings.
    - `Lagrange`: Approved: no material findings.
    - `Einstein`: Approved: no material findings.
- Final disposition:
  - complete
