# Active Plan

- Date: 2026-04-16
- Task: Stage 1 implementation for target package boundaries without behavior moves
- Status: `complete`
- Risk class: `Tier B`
- Requestor: Naki
- Owner: Codex

## Planner Contract

- Goal:
  - implement Stage 1 of the approved migration baseline by introducing the
    missing target package roots under `src/quantcraft`
  - keep the slice additive and non-destructive: create package boundaries and
    facades without moving current behavior ownership yet
  - preserve current documented public imports while making the target topology
    importable
- Governing docs:
  - [`README.md`](../../README.md)
  - [`ARCHITECTURE.md`](../../ARCHITECTURE.md)
  - [`docs/product-specs/index.md`](../product-specs/index.md)
  - [`docs/product-specs/backtest-mvp.md`](../product-specs/backtest-mvp.md)
  - [`docs/product-specs/research-ergonomics.md`](../product-specs/research-ergonomics.md)
  - [`docs/design-docs/index.md`](../design-docs/index.md)
  - [`docs/design-docs/quantcraft-architecture.md`](../design-docs/quantcraft-architecture.md)
  - [`docs/design-docs/package-topology-and-naming.md`](../design-docs/package-topology-and-naming.md)
  - [`docs/RELIABILITY.md`](../RELIABILITY.md)
  - [`docs/SECURITY.md`](../SECURITY.md)
  - [`docs/plans/2026-04-16-current-codebase-gap-analysis.md`](2026-04-16-current-codebase-gap-analysis.md)
  - external reference requested by the user:
    - Anthropic, "Harness design for long-running application development"
- Why these are governing:
  - they define the approved target topology, the current shipped backtest and
    research contracts, the migration baseline, verification rules, and the
    planner/generator/evaluator discipline the user explicitly asked to follow
- In-repo scope:
  - create `src/quantcraft/backtest/`, `src/quantcraft/execution/`, and
    `src/quantcraft/integrations/` package roots
  - add minimal Stage 1 facades or package skeletons consistent with the target
    topology
  - add or update tests that prove the new package roots exist without breaking
    current public surfaces
  - update only the active plan and any tightly coupled test/document references
    needed for this slice
  - if full repo verification is blocked by a tiny pre-existing doc assertion
    drift unrelated to the Stage 1 code move, repair only the minimal doc text
    needed to restore the repo lane and record that scope change explicitly
- Out-of-repo scope:
  - moving runtime behavior out of `research`
  - moving exchange/provider protocol code into `integrations`
  - widening architecture scanning or runtime-sensitive verification triggers
  - changing released-facing docs to make the new packages canonical
- Tier A progression requested: `yes`
- Approval record, if required:
  - requestor: `Naki`
  - human approver: `Naki`
  - countersignature or equivalent verification marker:
    - explicit user approval in the current chat on 2026-04-16 to create the
      Stage 1 plan, execute it immediately, use subagent orchestration, and read
      the requested Anthropic article
  - scope granted:
    - task-driven network access limited to the requested Anthropic article
    - Stage 1 package-boundary implementation including the introduction of an
      `execution` package root without live behavior
  - expiration:
    - end of this Stage 1 slice
  - audit reference or sanitized audit link:
    - current chat transcript for 2026-04-16
- Verification commands:
  - targeted fast lane:
    - `uv run pytest tests/structure/architecture/test_stage1_target_package_boundaries.py tests/smoke/local/test_public_imports.py tests/integration/commands/test_built_artifact_imports.py -q`
  - repo lane:
    - `uv run poe repo-check`
  - default full lane:
    - `uv run poe verify`
- Success criteria:
  - `quantcraft.backtest`, `quantcraft.execution`, and `quantcraft.integrations`
    exist as importable package roots
  - Stage 1 does not move current backtest or exchange behavior ownership out of
    existing modules
  - current root, data, and research public imports still pass smoke and
    built-artifact checks
  - the new backtest package exposes only additive compatibility facades, not a
    second implementation
  - implementation and review evidence are captured in this active plan
- Out of scope:
  - Stage 2 backtest ownership move
  - Stage 3 guardrail widening
  - Stage 4 integrations materialization
  - Stage 5 flattening
  - Stage 6 legacy removal

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice:
  - the implementation must add package roots without deleting any currently
    documented or tested import surface
  - `backtest` facades, if added, must point at current research-owned
    implementation rather than creating duplicate runtime logic
  - `execution` and `integrations` must remain boundary-only packages in this
    slice
  - at least one read-only research split and one review fan-out must be
    synthesized before closing the slice
- Acceptance artifact location:
  - this active plan
- How the generator and evaluator agreed on done before execution:
  - done is Stage 1 package-boundary introduction with preserved public
    contracts, not behavioral migration
- Checks the evaluator will use:
  - diff review against the governing docs and Stage 1 scope
  - subagent evidence review
  - targeted pytest lane
  - `uv run poe repo-check`
  - `uv run poe verify`
- Auto-fail conditions:
  - any behavior move out of `research` or `data`
  - any broken existing public import surface
  - any overlapping or duplicated backtest implementation
  - missing reviewer synthesis or missing fresh verification evidence

## Generator Work Log

- Planned slice order:
  1. run read-only research split to pin the exact Stage 1 file set and test
     needs
  2. add failing or missing tests for Stage 1 package roots and additive
     facades
  3. implement minimal package roots and compatibility facades
  4. run targeted verification
  5. run review fan-out, fix any findings, then run final verification
- Notes:
  - this slice follows the same harness principles the user pointed to in the
    Anthropic article: explicit planner/generator/evaluator separation, written
    acceptance contract, and bounded downstream handoffs
  - the owned Stage 1 file group for this slice is:
    - `src/quantcraft/backtest/__init__.py`
    - `src/quantcraft/execution/__init__.py`
    - `src/quantcraft/integrations/__init__.py`
    - `tests/structure/architecture/test_stage1_target_package_boundaries.py`
    - `tests/smoke/local/test_public_imports.py`
    - `tests/integration/commands/test_built_artifact_imports.py`
    - this active plan
  - unrelated previously staged docs from earlier slices were not modified by
    this Stage 1 implementation and are excluded from the Stage 1 ownership
    judgment
  - the following tiny doc blocker repairs were performed only to restore the
    repo-wide verification lane and are excluded from the Stage 1 ownership
    judgment:
    - `docs/references/research-ergonomics-quickstart.md`
    - `docs/product-specs/backtest-mvp.md`
    - `docs/product-specs/data-ingestion.md`
- Blockers or scope changes:
  - 2026-04-16: the repo-wide `verify` lane exposed two pre-existing doc/test
    assertion drifts outside the Stage 1 code path; the slice is allowed to
    repair only the minimal doc text needed to restore full verification

## Evaluator Review

- Findings:
  - read-only research split converged on the same minimal Stage 1 design:
    - add `quantcraft.backtest`, `quantcraft.execution`, and
      `quantcraft.integrations` package roots
    - keep `execution` and `integrations` boundary-only in this slice
    - keep current runtime ownership under `research`
    - expose only additive backtest facades from the new `backtest` package
  - implementation stayed within that slice:
    - `quantcraft.backtest` re-exports the current research-owned
      `BacktestEngine`, `BacktestResult`, `BacktestSummary`, and
      `ExposureSummary`
    - `quantcraft.execution` and `quantcraft.integrations` are importable empty
      boundary roots
    - no behavior was moved out of `research` or `data`
  - one review fan-out finding identified an incomplete contract assertion for
    `ExposureSummary`; the tests were tightened so the new backtest package must
    expose the existing research-owned type rather than any duplicate
  - repo-wide verification exposed three pre-existing doc assertion drifts
    outside the Stage 1 code path; the slice repaired only the minimal doc text
    required to restore `verify`
  - those doc repairs are verification unblockers, not part of the owned Stage
    1 package-boundary deliverable
- Verification evidence:
  - Anthropic harness reference reviewed:
    - planner / generator / evaluator split
    - explicit sprint contract before work
    - structured handoff artifacts
    - source: https://www.anthropic.com/engineering/harness-design-long-running-apps
  - read-only research split:
    - `Turing`: minimal package-root and facade design
    - `Maxwell`: public-surface and test obligations
    - `Fermat`: Tier A and verification-surface analysis
  - targeted Stage 1 verification:
    - `uv run pytest tests/structure/architecture/test_stage1_target_package_boundaries.py tests/structure/architecture/test_domain_boundaries.py tests/structure/architecture/test_backtest_runtime_hardening_boundaries.py tests/smoke/local/test_public_imports.py tests/integration/commands/test_built_artifact_imports.py -q`
    - result: `26 passed`
  - repo verification:
    - `uv run poe repo-check`
    - result: `repository checks passed`
  - full verification:
    - `uv run poe verify`
    - result:
      - `273 passed, 3 skipped`
      - coverage policy check passed
      - build passed
      - repo check passed
      - notebook validation passed
  - review fan-out:
    - `Banach`: Approved: no material findings.
    - `Raman`: initial packaging-diff finding resolved after staging the full
      Stage 1 file set and finalizing the active plan artifact; final result:
      Approved: no material findings.
    - `Helmholtz`: initial `ExposureSummary` contract finding resolved by
      identity assertions and final Stage 1 scope wording; final result:
      Approved: no material findings.
- Final disposition:
  - complete
