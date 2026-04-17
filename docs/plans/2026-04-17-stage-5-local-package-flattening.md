# Active Plan

- Date: 2026-04-17
- Task: Stage 5 implementation for flattening local package shapes where that materially improves legibility
- Status: `complete`
- Risk class: `Tier A`
- Requestor: `Naki`
- Owner: Codex

## Planner Contract

- Goal:
  - implement Stage 5 of the approved migration baseline by flattening
    context-local package shapes that are still dominated by ceremonial
    `domain / application / adapters` remnants
  - make canonical owners shallower where that improves navigation without
    changing shipped behavior
  - preserve current documented and tested import paths through compatibility
    shims, leaving deliberate breaking cleanup to Stage 6
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
  - [`docs/plans/2026-04-16-stage-4-integrations-materialization.md`](2026-04-16-stage-4-integrations-materialization.md)
  - external reference requested by the user:
    - Anthropic, "Harness design for long-running application development"
- Why these are governing:
  - they define the approved capability-first topology, the current shipped
    product surfaces, the migration baseline for Stage 5, the safety tiering
    for touching `trading`, and the planner/generator/evaluator protocol the
    user explicitly requested
- In-repo scope:
  - evaluate `data`, `research`, and `trading` independently for flattening
    opportunities
  - move canonical owners to shallower context-local module paths where the
    move is clearly legibility-improving and low-risk
  - keep compatibility shims for existing tested or documented imports that are
    not yet ready for Stage 6 removal
  - delete empty or ceremonial local packages only when no current test or
    runtime path depends on them
  - update directly coupled structure, smoke, integration, and unit tests to
    prove the new owner versus shim boundary
  - update only directly coupled docs or repo-check truth that would otherwise
    become stale because of this slice
  - update this active plan with research/review synthesis and fresh
    verification evidence
- Out-of-repo scope:
  - deliberate removal of compatibility shims
  - breaking public API cleanup
  - Stage 6 legacy path removal
  - live-trading behavior or execution-side product features
  - introducing `apps/*` product surfaces
- Tier A progression requested: `yes`
- Approval record, if required:
  - requestor: `Naki`
  - human approver: `Naki`
  - countersignature or equivalent verification marker:
    - explicit user approval in the current chat on 2026-04-17 to create the
      Stage 5 plan, execute it immediately, use subagent orchestration, use
      GPT-5.4-high by default, and read the requested Anthropic article
  - scope granted:
    - task-driven network access limited to the requested Anthropic article
    - Stage 5 package-shape flattening across `data`, `research`, and
      `trading`, including directly coupled tests and docs
    - Tier A package-shape work under `trading` as long as the slice preserves
      current behavior and does not begin Stage 6 shim removal
  - expiration:
    - end of this Stage 5 slice
  - audit reference or sanitized audit link:
    - current chat transcript for 2026-04-17
- Verification commands:
  - targeted Stage 5 lane:
    - `uv run pytest tests/unit/data tests/unit/trading tests/unit/research tests/integration/research/test_backtest_engine_entrypoints.py tests/integration/research/test_backtest_result_contract.py tests/structure/architecture/test_domain_boundaries.py tests/structure/architecture/test_stage1_target_package_boundaries.py tests/structure/architecture/test_stage4_integrations_materialization.py tests/smoke/local/test_public_imports.py tests/integration/commands/test_built_artifact_imports.py -q`
  - default repository lane:
    - `uv run poe verify`
  - stronger runtime and harness lane:
    - `uv run poe verify-runtime`
  - repo/document lane:
    - `uv run poe repo-check`
- Success criteria:
  - at least one context-local layer-first remnant is replaced by a shallower
    canonical owner path with preserved current behavior
  - any remaining `domain / application / adapters` subpackages touched by this
    slice are either still justified or reduced to explicit compatibility shims
  - current tested public and compatibility imports continue to work
  - read-only research split and review fan-out both complete with evidence and
    no material unresolved findings
  - completion claims are backed by fresh targeted verification, `verify`,
    `verify-runtime`, and `repo-check`
- Out of scope:
  - final public-surface narrowing
  - root compatibility alias deletion
  - removing `quantcraft.research.application.*` or `quantcraft.trading.domain.*`
    compatibility paths purely for cleanliness

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice:
  - Stage 5 materially improves local package legibility instead of just
    renaming files
  - canonical owner paths become shallower where touched by the slice
  - compatibility shims stay shallow and behavior-neutral
  - no Stage 6 cleanup is smuggled into this slice
  - research split and review fan-out both return evidence-bearing findings and
    are synthesized explicitly in this plan
  - completion claims are backed by fresh targeted verification, `verify`,
    `verify-runtime`, and `repo-check`
- Acceptance artifact location:
  - this active plan
- How the generator and evaluator agreed on done before execution:
  - done is bounded flattening with preserved current behavior, not final shim
    deletion
- Checks the evaluator will use:
  - diff review against the governing docs and Stage 5 scope
  - subagent evidence review
  - targeted Stage 5 lane
  - `uv run poe verify`
  - `uv run poe verify-runtime`
  - `uv run poe repo-check`
- Auto-fail conditions:
  - touched contexts remain equally or more confusing after the slice
  - Stage 5 deletes compatibility paths that Stage 6 is supposed to retire
  - behavior changes or public import breakage are introduced
  - missing research split, missing review fan-out, or missing fresh
    verification evidence

## Generator Work Log

- Planned slice order:
  1. run read-only research split for `data`, `research`, and `trading`
     flattening candidates plus test/guardrail impact
  2. synthesize the minimal Stage 5 file set and decide the canonical owner
     paths for this slice
  3. implement the flattening with one writer while preserving current
     behavior through bounded shims where needed
  4. run targeted verification
  5. run review fan-out, fix findings, and rerun final verification
- Notes:
  - per the user instruction, git staging remains human-only; this slice will
    not run `git add`
  - this slice follows the Anthropic harness pattern the user explicitly asked
    for: written planner contract first, single writer, separate evaluator
    stage, and evidence-bearing delegated research/review
  - preferred subagent model is GPT-5.4 high read-only research and review
    delegates; if the host thread cap blocks new delegates, fallback reuse will
    be recorded explicitly
  - read-only research split used bounded handoff contracts with disjoint
    scopes:
    - `Einstein`: `data` flattening candidates
    - `Bernoulli`: `research` flattening candidates
    - `Carson`: `trading` flattening candidates and Tier A caution
  - the final Stage 5 owned file group became:
    - `src/quantcraft/data/bars.py`
    - `src/quantcraft/data/sources.py`
    - `src/quantcraft/data/__init__.py`
    - `src/quantcraft/data/domain/__init__.py`
    - `src/quantcraft/data/domain/bars.py`
    - `src/quantcraft/data/domain/sources.py`
    - `src/quantcraft/data/adapters/ccxt_source.py`
    - `src/quantcraft/data/adapters/csv_source.py`
    - `src/quantcraft/data/adapters/dataframe_source.py`
    - `src/quantcraft/data/adapters/exchange_backend.py`
    - `src/quantcraft/backtest/engine.py`
    - `src/quantcraft/integrations/venues/ccxt/market_data.py`
    - `src/quantcraft/exchange.py`
    - `src/quantcraft/research/series.py`
    - `src/quantcraft/research/domain/__init__.py`
    - `src/quantcraft/research/domain/series.py`
    - `src/quantcraft/research/application/strategy.py`
    - `src/quantcraft/research/indicators/runtime/factory.py`
    - `src/quantcraft/trading/application/__init__.py`
    - `src/quantcraft/trading/adapters/__init__.py`
    - `src/quantcraft/data/application/__init__.py`
    - `tests/unit/data/test_bars.py`
    - `tests/unit/data/domain/test_bars.py`
    - `tests/unit/data/domain/test_sources.py`
    - `tests/unit/research/test_series.py`
    - `tests/unit/research/domain/test_series.py`
    - `tests/unit/research/indicators/runtime/test_factory.py`
    - `tests/unit/research/test_indicator_surface.py`
    - `tests/structure/repo/test_indicator_refactor_contracts.py`
    - `tests/structure/architecture/test_backtest_mvp_slice1.py`
    - `tests/structure/architecture/test_stage4_integrations_materialization.py`
    - `tests/structure/architecture/test_stage5_local_package_flattening.py`
    - `tests/smoke/local/test_public_imports.py`
    - `tests/integration/commands/test_built_artifact_imports.py`
    - this active plan
- Blockers or scope changes:
  - 2026-04-17: research split did not support full `trading.domain.*`
    flattening in this slice because Tier A guardrails and coverage rules are
    still pinned to `trading/domain/*`; the accepted `trading` move was
    narrowed to removal of empty placeholder package paths only
  - 2026-04-17: review fan-out found that deleting only
    `trading/application/__init__.py` and `trading/adapters/__init__.py`
    overclaimed package removal because the directories still survived as
    namespace packages; the fix was to remove the empty directories and add
    runtime proofs that those package paths no longer import
  - 2026-04-17: review fan-out also found that `data/application/__init__.py`
    remained as an empty ceremonial package even though no current runtime or
    test path depended on it; the fix was to remove that package and update the
    Stage 5 proofs accordingly

## Evaluator Review

- Findings:
  - read-only research split did not support one large flatten-everything move;
    it converged on three bounded decisions instead:
    - `data`: make `bars.py` and `sources.py` the shallow canonical owners and
      keep `data.domain*` as compatibility shims
    - `research`: make `series.py` the shallow canonical owner and keep
      `research.domain*` as compatibility shims
    - `trading`: do not flatten `trading.domain.*` yet; only remove empty
      placeholder package paths
  - the implementation matches that bounded Stage 5 shape:
    - canonical `data` contracts now live in `src/quantcraft/data/bars.py` and
      `src/quantcraft/data/sources.py`
    - canonical research series contracts now live in
      `src/quantcraft/research/series.py`
    - `data.domain*` and `research.domain*` are reduced to explicit re-export
      shims
    - empty ceremonial package paths under `data/application`,
      `trading/application`, and `trading/adapters` are removed
  - review fan-out produced two real blockers before final approval:
    - the initial Stage 5 trading cleanup only deleted `__init__.py` files and
      left empty directories importable as namespace packages
    - built-artifact proof initially covered only package-level shims, not the
      rewritten Stage 5 shim submodules
  - both blockers were resolved inside the slice:
    - empty directories were removed and local/built-artifact smoke tests now
      assert those package paths fail to import
    - built-artifact and local smoke tests now import
      `quantcraft.data.domain.bars`, `quantcraft.data.domain.sources`, and
      `quantcraft.research.domain.series` directly and prove identity with the
      new canonical owners
- Verification evidence:
  - Anthropic harness reference reviewed:
    - planner / generator / evaluator separation
    - written contract before edits
    - bounded handoff artifacts and separate evaluator signoff
    - source: https://www.anthropic.com/engineering/harness-design-long-running-apps
  - read-only research split:
    - `Einstein`: recommended flattening `data.domain` ownership into
      `quantcraft.data.bars` and `quantcraft.data.sources`
    - `Bernoulli`: recommended flattening `research.domain.series` into
      `quantcraft.research.series`
    - `Carson`: recommended against flattening `trading.domain.*` in this slice
      and limited the safe move to deletion of empty placeholder package paths
  - targeted Stage 5 lane:
    - `uv run pytest tests/unit/data tests/unit/trading tests/unit/research tests/integration/research/test_backtest_engine_entrypoints.py tests/integration/research/test_backtest_result_contract.py tests/structure/architecture/test_domain_boundaries.py tests/structure/architecture/test_stage1_target_package_boundaries.py tests/structure/architecture/test_stage4_integrations_materialization.py tests/structure/architecture/test_stage5_local_package_flattening.py tests/smoke/local/test_public_imports.py tests/integration/commands/test_built_artifact_imports.py -q`
    - result: `200 passed`
  - default repository verification:
    - `uv run poe verify`
    - result:
      - `306 passed, 3 skipped`
      - coverage policy check passed
      - build passed
      - repo check passed
      - notebook validation passed
  - stronger runtime verification:
    - `uv run poe verify-runtime`
    - result:
      - `306 passed, 3 skipped`
      - coverage policy check passed
      - build passed
      - repo check passed
      - notebook validation passed
      - perf check passed
  - repo verification:
    - `uv run poe repo-check`
    - result: `repository checks passed`
  - review fan-out:
    - `Hegel`: initial namespace-package blocker resolved; final result:
      Approved.
    - `Anscombe`: initial placeholder-package blocker resolved; final result:
      Approved.
    - `Epicurus`: initial shim-proof blocker resolved; final result: Approved.
- Final disposition:
  - complete
