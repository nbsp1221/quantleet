# Active Plan

- Date: 2026-04-16
- Task: Stage 3 implementation for widening architecture and verification guardrails to the approved capability-first topology
- Status: `complete`
- Risk class: `Tier A`
- Requestor: Naki
- Owner: Codex

## Planner Contract

- Goal:
  - implement Stage 3 of the approved migration baseline by making the
    repository guardrails understand the real capability-first topology after
    Stage 1 and Stage 2
  - close remaining mechanical blind spots around `integrations`, `_shared`,
    and the default verification bundle so later Stage 4/5 moves cannot outrun
    the checks
  - keep the slice additive and guardrail-oriented; this is not the stage that
    moves provider code or removes compatibility shims
- Governing docs:
  - [`README.md`](../../README.md)
  - [`AGENTS.md`](../../AGENTS.md)
  - [`ARCHITECTURE.md`](../../ARCHITECTURE.md)
  - [`docs/design-docs/index.md`](../design-docs/index.md)
  - [`docs/design-docs/package-topology-and-naming.md`](../design-docs/package-topology-and-naming.md)
  - [`docs/RELIABILITY.md`](../RELIABILITY.md)
  - [`docs/SECURITY.md`](../SECURITY.md)
  - [`docs/plans/2026-04-16-current-codebase-gap-analysis.md`](2026-04-16-current-codebase-gap-analysis.md)
  - [`docs/plans/2026-04-16-codebase-gap-analysis-and-migration-blueprint.md`](2026-04-16-codebase-gap-analysis-and-migration-blueprint.md)
  - [`docs/plans/2026-04-16-stage-2-backtest-ownership-move.md`](2026-04-16-stage-2-backtest-ownership-move.md)
  - external reference requested by the user:
    - Anthropic, "Harness design for long-running application development"
- Why these are governing:
  - they define the approved capability-first topology, the guardrail widening
    order after Stage 2, the repo-local verification contract, the safety
    boundary for touching `execution`, and the planner/generator/evaluator
    protocol the user explicitly requested
- In-repo scope:
  - widen architecture scanning so `integrations` and `_shared` are modeled by
    the repo checks instead of remaining blind spots
  - encode the minimal Stage 3 dependency rules needed by the target topology,
    especially `execution -> integrations` and integration-side translation into
    normalized `data` / `trading` contracts
  - strengthen structure tests so they prove the new topology-aware guardrails,
    not just the current absence of issues
  - widen the default verification bundle if needed so structure and local smoke
    checks are part of the default repository guardrail rather than advisory-only
  - update only the directly coupled docs and repo-contract tests needed to keep
    the repository truthful after the guardrail change
  - update this active plan with research/review synthesis and fresh verification
    evidence
- Out-of-repo scope:
  - moving venue or provider implementation into `integrations`
  - deleting compatibility shims
  - flattening package shapes
  - changing current product behavior
- Tier A progression requested: `no`
- Approval record, if required:
  - requestor: `Naki`
  - human approver: `Naki`
  - countersignature or equivalent verification marker:
    - explicit user approval in the current chat on 2026-04-16 to create the
      Stage 3 plan, execute it immediately, use subagent orchestration, and
      read the requested Anthropic article
  - scope granted:
    - task-driven network access limited to the requested Anthropic article
    - Stage 3 guardrail widening for architecture scanning, structure tests,
      runtime/repo verification wiring, and directly coupled docs
    - shared-test and shared-harness updates directly required by this slice
  - expiration:
    - end of this Stage 3 slice
  - audit reference or sanitized audit link:
    - current chat transcript for 2026-04-16
- Verification commands:
  - targeted guardrail lane:
    - `uv run pytest tests/structure/architecture/test_domain_boundaries.py tests/structure/architecture/test_stage1_target_package_boundaries.py tests/structure/architecture/test_backtest_runtime_hardening_boundaries.py tests/structure/repo/test_runtime_verification_lane.py tests/structure/repo/test_poe_task_contracts.py tests/smoke/local/test_public_imports.py tests/integration/commands/test_built_artifact_imports.py -q`
  - stronger runtime and harness lane:
    - `uv run poe verify-runtime`
  - default repository lane:
    - `uv run poe verify`
  - repo/document lane:
    - `uv run poe repo-check`
- Success criteria:
  - repo architecture scanning recognizes `integrations` and `_shared` as part
    of the target topology instead of treating them as root-module blind spots
  - dependency validation enforces a bounded Stage 3 rule set consistent with
    the approved topology
  - structure tests prove the Stage 3 guardrails directly
  - the default verification bundle includes the guardrail checks that the docs
    claim are part of the local reliability surface
  - read-only research split and review fan-out both complete with evidence and
    no material unresolved findings
- Out of scope:
  - Stage 4 `integrations` materialization
  - Stage 5 local package flattening
  - Stage 6 legacy removal

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice:
  - Stage 3 closes mechanical blind spots rather than merely adding more docs
  - the repository can mechanically distinguish target topology domains from
    accidental root-level modules
  - verification and structure-test claims are backed by current commands, not
    by stale assumptions from pre-Stage-3 docs
  - at least one read-only research split and one review fan-out are
    synthesized before the slice is closed
  - completion claims are backed by fresh targeted verification,
    `verify-runtime`, `verify`, and `repo-check`
- Acceptance artifact location:
  - this active plan
- How the generator and evaluator agreed on done before execution:
  - done is truthful mechanical enforcement for the new topology, not code
    movement into later stages
- Checks the evaluator will use:
  - diff review against the governing docs and Stage 3 scope
  - subagent evidence review
  - targeted guardrail lane
  - `uv run poe verify-runtime`
  - `uv run poe verify`
  - `uv run poe repo-check`
- Auto-fail conditions:
  - `integrations` or `_shared` remain invisible to the scanner after the slice
  - docs claim default guardrails that `verify` still does not execute
  - Stage 3 introduces behavior moves that belong to Stage 4+
  - missing research split, missing review fan-out, or missing fresh evidence

## Generator Work Log

- Planned slice order:
  1. run read-only research split for scanner/domain rules, verification bundle
     implications, and structure-test/doc obligations
  2. synthesize the minimal Stage 3 file set and dependency rules
  3. implement the scanner/test/doc changes with one writer
  4. run targeted verification
  5. run review fan-out, fix findings, and rerun final verification
- Notes:
  - per the user instruction, git staging remains human-only; this slice will
    not run `git add`
  - this slice follows the Anthropic harness pattern the user explicitly asked
    for: written planner contract first, single writer, separate evaluator
    stage, and evidence-bearing delegated research/review
  - read-only research split reused existing explorer threads because the host
    thread cap prevented spawning new ones
  - read-only research split used bounded handoff contracts with disjoint scopes:
    - `Nash`: scanner/domain-rule truth for `integrations` and `_shared`
    - `Turing`: verification bundle and runtime-lane wording truth
    - `Plato`: structure-test and public-surface boundary discipline
  - final Stage 3 owned file group became:
    - `src/quantcraft/_repo_tools.py`
    - `pyproject.toml`
    - `tests/structure/architecture/test_domain_boundaries.py`
    - `tests/structure/repo/test_runtime_verification_lane.py`
    - `AGENTS.md`
    - `docs/RELIABILITY.md`
    - this active plan
- Blockers or scope changes:
  - 2026-04-16: the verification-bundle research split showed that `verify`
    already includes structure and local smoke checks through `pytest -q`, so
    the planned `verify` widening was not needed and was intentionally skipped
  - 2026-04-16: review fan-out found one stale command-surface claim:
    `pyproject.toml` still described `verify-runtime` as the stronger lane for
    runtime-sensitive research changes only
  - 2026-04-16: review fan-out also found that the initial Stage 3 allowlist
    still rejected `data -> integrations`, which contradicted the approved
    architecture dependency rules
  - 2026-04-16: scope widened narrowly to include:
    - `pyproject.toml`
    - `tests/structure/repo/test_runtime_verification_lane.py`
  - 2026-04-16: this widening remained inside Stage 3 because it restored
    truthful guardrails and did not move product behavior or begin Stage 4
    `integrations` materialization

## Evaluator Review

- Findings:
  - read-only research split converged on the same Stage 3 shape:
    - `_repo_tools.py` was the primary scanner blind spot
    - `integrations` and `_shared` needed to be recognized as topology domains
    - the verification contract did not require changing `verify` because
      `pytest -q` already includes structure and local smoke tests
    - the real wording drift lived in `AGENTS.md`, `docs/RELIABILITY.md`, and
      `pyproject.toml` help text for `verify-runtime`
  - the first implementation passed the targeted lane but exposed two reviewer
    blockers:
    - `pyproject.toml` still described `verify-runtime` as the stronger lane
      for runtime-sensitive research changes only
    - `_repo_tools.py` still rejected `data -> integrations`, which undershot
      the approved dependency rules in `quantcraft-architecture.md`
  - both blockers were resolved inside the slice:
    - `verify-runtime` help text now matches the Stage 3 backtest-or-research
      wording and is pinned by `test_runtime_verification_lane.py`
    - `data -> integrations` is now explicitly allowed and proved by both a
      direct rule test and a repository-scan test
  - final architecture position for this slice:
    - scanner truth now recognizes `integrations` and `_shared` as topology
      domains instead of root-module blind spots
    - Stage 3 dependency validation now permits the minimal approved edges for
      `execution`, `data`, and `integrations`
    - the default verification bundle stayed unchanged because it was already
      truthful; Stage 3 fixed wording and proof, not task inflation
- Verification evidence:
  - Anthropic harness reference reviewed:
    - planner / generator / evaluator separation
    - written contract before edits
    - bounded handoff artifacts and separate evaluator signoff
    - source: https://www.anthropic.com/engineering/harness-design-long-running-apps
  - read-only research split:
    - `Nash`: scanner/domain-rule blind spots and bounded allowlist changes
    - `Turing`: verification-bundle truth and no-need-to-widen-verify finding
    - `Plato`: stage-boundary proof that smoke and built-artifact compatibility
      checks should remain unchanged in Stage 3
  - targeted guardrail lane:
    - `uv run pytest tests/structure/architecture/test_domain_boundaries.py tests/structure/architecture/test_stage1_target_package_boundaries.py tests/structure/architecture/test_backtest_runtime_hardening_boundaries.py tests/structure/repo/test_runtime_verification_lane.py tests/structure/repo/test_poe_task_contracts.py tests/smoke/local/test_public_imports.py tests/integration/commands/test_built_artifact_imports.py -q`
    - result: `48 passed`
  - repo verification:
    - `uv run poe repo-check`
    - result: `repository checks passed`
  - default repository verification:
    - `uv run poe verify`
    - result:
      - `288 passed, 3 skipped`
      - coverage policy check passed
      - build passed
      - repo check passed
      - notebook validation passed
  - stronger runtime verification:
    - `uv run poe verify-runtime`
    - result:
      - `288 passed, 3 skipped`
      - coverage policy check passed
      - build passed
      - repo check passed
      - notebook validation passed
      - perf check passed
  - review fan-out:
    - `Lagrange`: Approved: no material findings.
    - `Einstein`: initial command-surface blocker resolved; final result:
      Approved.
    - `Zeno`: initial dependency-rule blocker resolved; final result: Approved.
- Final disposition:
  - complete
