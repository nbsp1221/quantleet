# Active Plan

- Date: 2026-04-16
- Task: Stage 2 implementation for moving backtest runtime ownership from `research` to `backtest`
- Status: `complete`
- Risk class: `Tier B`
- Requestor: Naki
- Owner: Codex

## Planner Contract

- Goal:
  - implement Stage 2 of the approved migration baseline by making
    `src/quantcraft/backtest` the real owner of the current backtest runtime
    implementation
  - preserve the current documented `quantcraft.research` public surface as a
    temporary compatibility layer while ownership moves
  - update only the directly coupled tests and runtime-sensitive
    documentation/checks needed to keep the repository truthful after the move
- Governing docs:
  - [`README.md`](../../README.md)
  - [`ARCHITECTURE.md`](../../ARCHITECTURE.md)
  - [`docs/product-specs/index.md`](../product-specs/index.md)
  - [`docs/product-specs/backtest-mvp.md`](../product-specs/backtest-mvp.md)
  - [`docs/product-specs/backtest.md`](../product-specs/backtest.md)
  - [`docs/product-specs/research-ergonomics.md`](../product-specs/research-ergonomics.md)
  - [`docs/design-docs/index.md`](../design-docs/index.md)
  - [`docs/design-docs/package-topology-and-naming.md`](../design-docs/package-topology-and-naming.md)
  - [`docs/RELIABILITY.md`](../RELIABILITY.md)
  - [`docs/SECURITY.md`](../SECURITY.md)
  - [`docs/plans/2026-04-16-current-codebase-gap-analysis.md`](2026-04-16-current-codebase-gap-analysis.md)
  - [`docs/plans/2026-04-16-codebase-gap-analysis-and-migration-blueprint.md`](2026-04-16-codebase-gap-analysis-and-migration-blueprint.md)
  - [`docs/plans/2026-04-16-stage-1-target-package-boundaries.md`](2026-04-16-stage-1-target-package-boundaries.md)
  - external reference requested by the user:
    - Anthropic, "Harness design for long-running application development"
- Why these are governing:
  - they define the approved capability-first target, the current backtest and
    research product contracts, the migration sequencing baseline, reliability
    triggers, and the planner/generator/evaluator discipline the user requested
- In-repo scope:
  - create the real backtest-owned modules needed for the current runtime:
    - engine
    - result/runtime summary types
    - execution model
    - order activation policy if required by the ownership boundary
  - convert current `research` backtest modules into compatibility shims or
    re-export surfaces instead of primary owners
  - update import surfaces and tests to reflect the new owner while preserving
    documented research-facing compatibility
  - update runtime-sensitive docs/tests only where ownership truth changes
  - update this active plan with synthesized research/review findings and fresh
    verification evidence
- Out-of-repo scope:
  - moving venue/provider protocol code into `integrations`
  - widening architecture-scanner domain knowledge beyond this slice
  - flattening package shapes beyond the directly touched backtest/runtime
    modules
  - Stage 4+ compatibility removal or deliberate breaking cleanup
- Tier A progression requested: `no`
- Approval record, if required:
  - requestor: `Naki`
  - human approver: `Naki`
  - countersignature or equivalent verification marker:
    - explicit user approval in the current chat on 2026-04-16 to create the
      Stage 2 plan, execute it immediately, use subagent orchestration, and
      read the requested Anthropic article
  - scope granted:
    - task-driven network access limited to the requested Anthropic article
    - Stage 2 runtime ownership move for `backtest`, including compatibility
      shims under `research`
    - shared-test and public-surface adjustments directly required by this move
  - expiration:
    - end of this Stage 2 slice
  - audit reference or sanitized audit link:
    - current chat transcript for 2026-04-16
- Verification commands:
  - targeted runtime lane:
    - `uv run pytest tests/unit/research/adapters/test_execution_model.py tests/unit/research/application/test_order_activation_policy.py tests/integration/research/test_backtest_engine_entrypoints.py tests/integration/research/test_backtest_result_contract.py tests/structure/architecture/test_backtest_runtime_hardening_boundaries.py tests/structure/repo/test_runtime_verification_lane.py tests/smoke/local/test_public_imports.py tests/integration/commands/test_built_artifact_imports.py -q`
  - stronger runtime lane:
    - `uv run poe verify-runtime`
  - repo/document lane:
    - `uv run poe repo-check`
- Success criteria:
  - the primary implementation of the backtest runtime lives under
    `src/quantcraft/backtest`
  - `quantcraft.backtest` exports the canonical runtime owner types rather than
    re-exporting research-owned implementations
  - the existing `quantcraft.research` and
    `quantcraft.research.application.backtest` surfaces still import cleanly as
    compatibility paths
  - runtime-sensitive docs/tests reflect the new owner wherever ownership truth
    is the point of the check
  - review fan-out closes with evidence and no material unresolved findings
- Out of scope:
  - Stage 3 guardrail widening beyond directly coupled runtime-trigger truth
  - Stage 4 integrations materialization
  - Stage 5 package flattening
  - Stage 6 legacy shim removal

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice:
  - `backtest` becomes the real source of truth for the moved runtime modules
  - no duplicate behavioral implementation remains under both `backtest` and
    `research`
  - existing research-facing imports continue to work as explicit compatibility
    paths for this stage
  - at least one read-only research split and one review fan-out are
    synthesized before the slice is closed
  - completion claims are backed by fresh targeted verification,
    `verify-runtime`, and `repo-check`
- Acceptance artifact location:
  - this active plan
- How the generator and evaluator agreed on done before execution:
  - done is ownership movement with compatibility, not full legacy cleanup
- Checks the evaluator will use:
  - diff review against the governing docs and Stage 2 scope
  - subagent evidence review
  - targeted runtime lane
  - `uv run poe verify-runtime`
  - `uv run poe repo-check`
- Auto-fail conditions:
  - duplicated runtime logic under both `research` and `backtest`
  - broken current public research import surface
  - ownership still materially living under `research` after the slice
  - missing review synthesis or missing fresh verification evidence

## Generator Work Log

- Planned slice order:
  1. run read-only research split for ownership move shape, public/test impact,
     and guardrail impact
  2. synthesize the minimal Stage 2 file set and compatibility strategy
  3. implement the backtest-owned modules and convert research modules to shims
  4. update directly coupled tests/docs for the moved ownership
  5. run targeted verification
  6. run review fan-out, fix findings, then run final verification
- Notes:
  - per the user instruction, git staging remains human-only; this slice will
    not run `git add`
  - this slice should follow the Anthropic harness pattern the user requested:
    explicit planner/generator/evaluator separation, written contract before
    edits, bounded handoff artifacts, and separate evaluator review
  - read-only research split used GPT-5.4 high explorers with disjoint scopes:
    - `Nash`: ownership move shape and minimal file set
    - `Turing`: public/test compatibility impact
    - `Plato`: guardrail and verification-lane implications
  - the final Stage 2 owned file group became:
    - `src/quantcraft/backtest/__init__.py`
    - `src/quantcraft/backtest/engine.py`
    - `src/quantcraft/backtest/execution_model.py`
    - `src/quantcraft/backtest/order_activation.py`
    - `src/quantcraft/backtest/results.py`
    - `src/quantcraft/backtest/runtime.py`
    - `src/quantcraft/backtest/strategy_runtime.py`
    - `src/quantcraft/research/__init__.py`
    - `src/quantcraft/research/application/__init__.py`
    - `src/quantcraft/research/application/_runtime.py`
    - `src/quantcraft/research/application/backtest.py`
    - `src/quantcraft/research/application/engine.py`
    - `src/quantcraft/research/application/order_activation.py`
    - `src/quantcraft/research/adapters/execution_model.py`
    - `src/quantcraft/_repo_tools.py`
    - `tests/unit/research/adapters/test_execution_model.py`
    - `tests/unit/research/application/test_order_activation_policy.py`
    - `tests/structure/architecture/test_backtest_runtime_hardening_boundaries.py`
    - `tests/structure/architecture/test_domain_boundaries.py`
    - `tests/structure/repo/test_runtime_verification_lane.py`
    - `docs/RELIABILITY.md`
    - `AGENTS.md`
    - this active plan
- Blockers or scope changes:
  - 2026-04-16: the initial implementation exposed a verification blind spot
    because `backtest` became a real owner before `_repo_tools.py` recognized
    `backtest` as a domain
  - 2026-04-16: to restore truthful verification inside this slice, scope was
    widened narrowly to include:
    - `src/quantcraft/_repo_tools.py`
    - `tests/structure/architecture/test_domain_boundaries.py`
    - `src/quantcraft/backtest/strategy_runtime.py`
    - `src/quantcraft/research/application/_runtime.py`
  - 2026-04-16: this widening remained inside Stage 2 because it was limited to
    direct ownership-proof and guardrail-truth work, not the broader Stage 3
    scanner expansion

## Evaluator Review

- Findings:
  - read-only research split converged on the same Stage 2 shape:
    - move the real runtime owner modules under `src/quantcraft/backtest`
    - keep `quantcraft.research` and `quantcraft.research.application.*` as
      temporary compatibility surfaces
    - update runtime-sensitive docs/tests where ownership truth is the point of
      the check
  - the first implementation passed runtime tests but exposed two reviewer
    findings:
    - `backtest` was not yet modeled by `_repo_tools.py`, creating a repo-check
      blind spot
    - `backtest.runtime` still depended on the private
      `research.application._runtime._StrategyDriver`
  - both reviewer blockers were resolved inside the slice:
    - `_repo_tools.py` now treats `backtest` as a Tier B domain and encodes the
      narrow Stage 2 allowlist needed for current architecture truth
    - `_StrategyDriver` and `_StrategyOrderState` now live under
      `src/quantcraft/backtest/strategy_runtime.py`
    - `research.application._runtime` now keeps `PositionView` and re-exports
      the moved runtime-driver symbols as compatibility shims
    - structure tests now assert the moved owner plus all directly touched shim
      modules
  - final architecture position for this slice:
    - `backtest` is now the real owner of engine, runtime, execution model,
      results, order activation, and strategy runtime driver
    - `research` remains the temporary compatibility surface for current public
      imports
- Verification evidence:
  - Anthropic harness reference reviewed:
    - planner / generator / evaluator separation
    - explicit written contract before edits
    - bounded handoff artifacts and evaluator signoff
    - source: https://www.anthropic.com/engineering/harness-design-long-running-apps
  - read-only research split:
    - `Nash`: ownership move file set and acceptance checklist
    - `Turing`: compatibility-surface and verification obligations
    - `Plato`: guardrail/doc implications and hidden blockers
  - focused runtime/compatibility lane:
    - `uv run pytest tests/unit/research/application/test_data_surface.py tests/unit/research/application/test_strategy_surface.py tests/unit/research/test_indicator_surface.py tests/unit/research/adapters/test_execution_model.py tests/unit/research/application/test_order_activation_policy.py tests/integration/research/test_backtest_engine_entrypoints.py tests/integration/research/test_backtest_result_contract.py tests/structure/architecture/test_backtest_runtime_hardening_boundaries.py tests/structure/architecture/test_domain_boundaries.py tests/structure/repo/test_runtime_verification_lane.py tests/smoke/local/test_public_imports.py tests/integration/commands/test_built_artifact_imports.py -q`
    - result: `84 passed`
  - targeted Stage 2 lane:
    - `uv run pytest tests/unit/research/adapters/test_execution_model.py tests/unit/research/application/test_order_activation_policy.py tests/integration/research/test_backtest_engine_entrypoints.py tests/integration/research/test_backtest_result_contract.py tests/structure/architecture/test_backtest_runtime_hardening_boundaries.py tests/structure/architecture/test_domain_boundaries.py tests/structure/repo/test_runtime_verification_lane.py tests/smoke/local/test_public_imports.py tests/integration/commands/test_built_artifact_imports.py -q`
    - result: `59 passed`
  - repo verification:
    - `uv run poe repo-check`
    - result: `repository checks passed`
  - full runtime verification:
    - `uv run poe verify-runtime`
    - result:
      - `283 passed, 3 skipped`
      - coverage policy check passed
      - build passed
      - repo check passed
      - notebook validation passed
      - perf check passed
  - review fan-out:
    - `Zeno`: Approved: no material findings.
    - `Lagrange`: initial guardrail/ownership-proof findings resolved; final
      result: Approved: no material findings.
    - `Einstein`: initial boundary blocker resolved after moving
      `_StrategyDriver` into `backtest`; final result: Approved: no material
      findings.
- Final disposition:
  - complete
