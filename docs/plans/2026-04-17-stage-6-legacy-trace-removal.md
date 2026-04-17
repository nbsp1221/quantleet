# Active Plan

- Date: 2026-04-17
- Task: Stage 6 implementation for deliberate breaking cleanup and removal of migration-only legacy traces
- Status: `complete`
- Risk class: `Tier A`
- Requestor: `Naki`
- Owner: Codex

## Planner Contract

- Goal:
  - implement Stage 6 of the approved migration baseline by removing
    migration-only compatibility shims and legacy import surfaces that no
    longer match the approved capability-first topology
  - prefer final architectural truth over backward compatibility because the
    project is still unreleased and the user explicitly approved breaking
    cleanup
  - leave justified local layering in place where it is still an intentional
    owner, rather than treating every remaining subpackage as legacy
- Governing docs:
  - [`README.md`](../../README.md)
  - [`AGENTS.md`](../../AGENTS.md)
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
  - [`docs/plans/2026-04-16-codebase-gap-analysis-and-migration-blueprint.md`](2026-04-16-codebase-gap-analysis-and-migration-blueprint.md)
  - [`docs/plans/2026-04-17-stage-5-local-package-flattening.md`](2026-04-17-stage-5-local-package-flattening.md)
  - external reference requested by the user:
    - Anthropic, "Harness design for long-running application development"
- Why these are governing:
  - they define the approved final topology, the current shipped product
    surface that must now be narrowed deliberately, the Tier A approval
    requirements for breaking cleanup, and the planner/generator/evaluator
    protocol the user explicitly requested
- In-repo scope:
  - remove migration-only root and package shim paths that still preserve the
    pre-migration layout, including:
    - `quantcraft` root lazy exports for `Exchange`, `MarketType`, and `TimeBar`
    - `src/quantcraft/exchange.py`
    - `src/quantcraft/data/domain/*`
    - `src/quantcraft/research/domain/*`
    - `src/quantcraft/research/application/*` compatibility shims that only
      forward to `backtest` or older `Strategy` locations
    - `src/quantcraft/research/adapters/execution_model.py`
  - move any remaining canonical research surface needed for the final topology
    to shallow owner paths under `src/quantcraft/research`
  - repoint internal code, tests, and documentation to the final owner paths
  - update structure, smoke, built-artifact, and runtime tests so they prove
    that legacy paths are gone rather than merely still compatible
  - narrow `_repo_tools.py` and related architecture checks so they no longer
    encode transitional compatibility edges that Stage 6 removes
  - update only directly coupled docs needed to keep the repo truthful after
    the breaking cleanup
  - update this active plan with research/review synthesis and fresh
    verification evidence
- Out-of-repo scope:
  - new product features
  - live-trading implementation
  - introducing `apps/*` code
  - flattening or renaming `trading.domain.*` purely for stylistic symmetry if
    it remains justified local layering
- Tier A progression requested: `yes`
- Approval record, if required:
  - requestor: `Naki`
  - human approver: `Naki`
  - countersignature or equivalent verification marker:
    - explicit user approval in the current chat on 2026-04-17 to create the
      Stage 6 plan, execute it immediately, use subagent orchestration, use
      GPT-5.4-high by default, and read the requested Anthropic article
  - scope granted:
    - task-driven network access limited to the requested Anthropic article
    - Stage 6 breaking cleanup for migration-only compatibility shims and
      directly coupled source, test, and documentation updates
    - Tier A review discipline for any directly touched `trading`-adjacent
      structure checks or contract proofs
  - expiration:
    - end of this Stage 6 slice
  - audit reference or sanitized audit link:
    - current chat transcript for 2026-04-17
- Verification commands:
  - targeted Stage 6 lane:
    - `uv run pytest tests/unit/data tests/unit/research tests/unit/backtest tests/unit/integrations/venues/ccxt/test_market_data.py tests/integration/research tests/structure/architecture/test_domain_boundaries.py tests/structure/architecture/test_backtest_runtime_hardening_boundaries.py tests/structure/architecture/test_stage4_integrations_materialization.py tests/structure/architecture/test_stage5_local_package_flattening.py tests/smoke/local/test_public_imports.py tests/integration/commands/test_built_artifact_imports.py -q`
  - default repository lane:
    - `uv run poe verify`
  - stronger runtime and harness lane:
    - `uv run poe verify-runtime`
  - repo/document lane:
    - `uv run poe repo-check`
- Success criteria:
  - migration-only compatibility imports removed by this slice fail cleanly
    instead of silently re-exporting current owners
  - final public surface is capability-first:
    - `quantcraft.data` for data contracts and data sources
    - `quantcraft.backtest` for backtest runtime and result surface
    - `quantcraft.research` for strategy and indicator ergonomics
    - `quantcraft.integrations.*` for exchange/provider protocol code
  - `Strategy` no longer requires the legacy
    `quantcraft.research.application.strategy` owner path
  - docs and tests no longer describe or prove the removed legacy paths as
    supported imports
  - read-only research split and review fan-out both complete with evidence and
    no material unresolved findings
  - completion claims are backed by fresh targeted verification, `verify`,
    `verify-runtime`, and `repo-check`
- Out of scope:
  - adding new public facade files beyond what Stage 6 needs to land the final
    owner paths
  - removing justified local layering that still materially improves clarity

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice:
  - Stage 6 removes legacy traces rather than preserving them behind new names
  - final owner paths are shallower and clearer than the transitional shim
    layout they replace
  - removed compatibility imports fail in local and built-artifact smoke proof
  - no transitional docs remain that still advertise the removed shim surface
  - research split and review fan-out both return evidence-bearing findings and
    are synthesized explicitly in this plan
  - completion claims are backed by fresh targeted verification, `verify`,
    `verify-runtime`, and `repo-check`
- Acceptance artifact location:
  - this active plan
- How the generator and evaluator agreed on done before execution:
  - done is deliberate breaking cleanup of legacy traces, not further staged
    compatibility preservation
- Checks the evaluator will use:
  - diff review against the governing docs and Stage 6 scope
  - subagent evidence review
  - targeted Stage 6 lane
  - `uv run poe verify`
  - `uv run poe verify-runtime`
  - `uv run poe repo-check`
- Auto-fail conditions:
  - deleted shim paths are still importable
  - docs or smoke tests still treat removed shim paths as valid public imports
  - Stage 6 removes justified local layering without evidence that it was only
    legacy compatibility
  - missing research split, missing review fan-out, or missing fresh
    verification evidence

## Generator Work Log

- Planned slice order:
  1. run read-only research split for final import surface, remaining shim
     inventory, and Tier A caution on final cleanup scope
  2. synthesize the minimal Stage 6 file set and final public import contract
  3. implement the breaking cleanup with one writer
  4. run targeted verification
  5. run review fan-out, fix findings, and rerun final verification
- Notes:
  - per the user instruction, git staging remains human-only; this slice will
    not run `git add`
  - this slice follows the Anthropic harness pattern the user explicitly asked
    for: written planner contract first, single writer, separate evaluator
    stage, and evidence-bearing delegated research/review
  - preferred subagent model was GPT-5.4 high read-only research and review
    delegates; the host thread cap blocked new delegates, so existing GPT-5.4
    high explorer/reviewer threads were reused with bounded handoff contracts
  - read-only research split used disjoint scopes:
    - `Einstein`: final public import contract
    - `Bernoulli`: remaining shim inventory and canonical owner mapping
    - `Carson`: guardrail, verification, and Tier A caution
  - final Stage 6 owned file group became:
    - `src/quantcraft/__init__.py`
    - `src/quantcraft/_repo_tools.py`
    - `src/quantcraft/research/__init__.py`
    - `src/quantcraft/research/strategy.py`
    - removal of:
      - `src/quantcraft/exchange.py`
      - `src/quantcraft/data/domain/`
      - `src/quantcraft/data/adapters/exchange_backend.py`
      - `src/quantcraft/research/domain/`
      - `src/quantcraft/research/application/`
      - `src/quantcraft/research/adapters/`
    - direct doc updates:
      - `README.md`
      - `ARCHITECTURE.md`
      - `docs/design-docs/quantcraft-architecture.md`
      - `docs/RELIABILITY.md`
      - `docs/references/testing.md`
      - `docs/product-specs/market-data.md`
      - `docs/product-specs/data-ingestion.md`
      - `docs/product-specs/backtest-mvp.md`
      - `docs/product-specs/research-ergonomics.md`
      - `docs/references/research-ergonomics-quickstart.md`
      - affected notebooks
    - direct proof updates:
      - smoke and built-artifact import proofs
      - Stage 4/5/6 structure proofs
      - runtime-verification trigger proof
      - unit/integration tests repointed to final owner paths
- Blockers or scope changes:
  - 2026-04-17: research split converged on keeping `trading.domain.*` as
    justified local layering; Stage 6 intentionally did not flatten Tier A
    trading ownership
  - 2026-04-17: the parent chose to include
    `src/quantcraft/data/adapters/exchange_backend.py` in Stage 6 rather than
    defer it, so that all exchange-era compatibility shims could be removed in
    one breaking-cleanup pass
  - 2026-04-17: the parent also expanded Stage 6 to relocate active tests from
    `tests/unit/research/application`, `tests/unit/research/adapters`, and
    `tests/unit/market_data` into final capability-aligned locations after
    reviewer feedback showed those paths were still teaching the removed
    topology
  - 2026-04-17: initial review fan-out surfaced three blocker classes:
    - stale transitional wording in architecture docs
    - runtime-verification trigger lists missing the final owner files
    - smoke/build/structure proofs not asserting absence of
      `quantcraft.research.adapters` itself
  - 2026-04-17: all blockers were resolved inside the slice before final
    verification:
    - docs were rewritten to reflect the post-Stage-6 package shape
    - `docs/RELIABILITY.md` and the matching repo test now include
      `src/quantcraft/backtest/strategy_runtime.py` and
      `src/quantcraft/research/strategy.py`
    - smoke/build/structure proofs now assert `quantcraft.research.adapters`
      and other removed legacy roots fail cleanly

## Evaluator Review

- Findings:
  - read-only research split converged on a bounded final surface:
    - keep `quantcraft.data` as the public data contract and source namespace
    - keep `quantcraft.backtest` as the public backtest runtime and result
      namespace
    - keep `quantcraft.research` as the public strategy and indicator
      ergonomics namespace
    - keep `quantcraft.integrations.venues.ccxt` as the current exchange
      protocol surface
    - remove root `quantcraft` symbol exports and all migration-only shim
      namespaces under `data` and `research`
  - the implementation matches that final Stage 6 shape:
    - `Strategy` now lives at `src/quantcraft/research/strategy.py`
    - `PositionView` was folded into the same owner instead of leaving
      `research.application._runtime` behind
    - all research-side backtest compatibility modules were removed
    - all remaining root/data exchange compatibility shims were removed
    - tests and docs now import from the final capability owners
  - review fan-out produced three blocker rounds before final approval:
    - stale architecture wording still described pre-Stage-6 placements
    - runtime-verification triggers missed the final owner files
    - smoke/build/structure proofs missed `quantcraft.research.adapters` and
      active test paths still encoded the removed topology
  - all reviewer blockers were resolved inside the slice:
    - architecture and package-topology docs now describe the current tree
      truthfully
    - verification trigger docs/tests now include the final strategy runtime
      owners
    - legacy shim absence is proved locally, in the built wheel, and in
      structure tests
    - active tests were moved to `tests/unit/backtest`,
      `tests/unit/research`, and `tests/unit/integrations/venues/ccxt`
  - final Stage 6 position for this slice:
    - deliberate breaking cleanup is complete for the Stage 1-5 compatibility
      traces under root, `data`, and `research`
    - `trading.domain.*` remains as justified local layering, not as a
      migration shim
- Verification evidence:
  - Anthropic harness reference reviewed:
    - planner / generator / evaluator separation
    - written contract before edits
    - bounded handoff artifacts and separate evaluator signoff
    - source: https://www.anthropic.com/engineering/harness-design-long-running-apps
  - read-only research split:
    - `Einstein`: final supported imports should be capability-first and root
      exports should disappear
    - `Bernoulli`: `research/application`, `research/domain`,
      `research/adapters`, `data/domain`, and exchange shims were confirmed as
      shim-only and removable after relocating `Strategy`
    - `Carson`: guardrail updates were required for removed shim roots and
      final runtime-trigger files; `trading.domain.*` should remain untouched
  - targeted Stage 6 lane:
    - `uv run pytest tests/unit/data tests/unit/research tests/unit/backtest tests/unit/integrations/venues/ccxt/test_market_data.py tests/integration/research tests/structure/architecture/test_domain_boundaries.py tests/structure/architecture/test_backtest_runtime_hardening_boundaries.py tests/structure/architecture/test_stage4_integrations_materialization.py tests/structure/architecture/test_stage5_local_package_flattening.py tests/smoke/local/test_public_imports.py tests/integration/commands/test_built_artifact_imports.py tests/structure/docs/test_research_ergonomics_quickstart.py tests/structure/repo/test_repository_entrypoint_docs.py tests/structure/repo/test_runtime_verification_lane.py tests/structure/repo/test_indicator_refactor_contracts.py -q`
    - result: `210 passed in 1.47s`
  - default repository verification:
    - `uv run poe verify`
    - result:
      - `286 passed, 3 skipped`
      - coverage policy check passed
      - build passed
      - repo check passed
      - notebook validation passed
  - stronger runtime verification:
    - `uv run poe verify-runtime`
    - result:
      - `286 passed, 3 skipped`
      - coverage policy check passed
      - build passed
      - repo check passed
      - notebook validation passed
      - perf check passed
  - repo verification:
    - `uv run poe repo-check`
    - result: `repository checks passed`
  - review fan-out:
    - `Hegel`: Approved: no material findings.
    - `Anscombe`: Approved: no material findings.
    - `Epicurus`: Approved: no material findings.
