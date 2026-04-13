# Legacy Control-Plane Retirement Plan

- Date: 2026-04-14
- Task: retire or demote remaining low-signal workflow bureaucracy artifacts
- Status: `complete`
- Risk class: `Tier B`
- Requestor: repository owner
- Owner: Codex main agent

## Planner Contract

- Goal:
  - remove or clearly demote remaining legacy workflow-control artifacts that
    are no longer justified as active repo authority
- Governing docs:
  - [`../../AGENTS.md`](../../AGENTS.md)
  - [`../../ARCHITECTURE.md`](../../ARCHITECTURE.md)
  - [`../DESIGN.md`](../DESIGN.md)
  - [`../PLANS.md`](../PLANS.md)
  - [`../RELIABILITY.md`](../RELIABILITY.md)
  - [`../SECURITY.md`](../SECURITY.md)
  - [`2026-04-13-ce-workflow-migration-plan.md`](2026-04-13-ce-workflow-migration-plan.md)
- Why these are governing:
  - they define the repo entry contract, hard gates, and current migration
    sequencing for workflow and control-plane changes
- In-repo scope:
  - docs related to
    `docs/QUALITY_SCORE.md`, `docs/feedback-promotion-log.md`, and
    `docs/exec-plans/`
- Out-of-repo scope:
  - none
- Tier A progression requested: `no`
- Approval record, if required:
  - not required; no Tier A or out-of-repo scope requested
- Verification commands:
  - `uv run pytest tests/structure/docs/test_system_of_record_docs.py tests/structure/docs/test_plan_indexes.py tests/structure/repo/test_execution_plan_lifecycle.py tests/structure/repo/test_runtime_verification_lane.py -q`
  - `uv run python scripts/check_docs.py`
  - `uv run python scripts/repo_check.py`
  - `uv run poe verify`
- Success criteria:
  - top-level repo docs no longer describe low-signal legacy artifacts as active
    authority unless they remain intentionally load-bearing
  - surviving docs preserve enough rationale that future agents do not need the
    retired artifacts to understand the active contract
  - runtime, perf, live, coverage, and architecture hard gates remain intact
  - historical artifacts that remain in the repo are clearly marked historical
    or advisory rather than current workflow authority
- Out of scope:
  - changing product behavior, runtime semantics, or financial-domain hard gates

## Evaluator Acceptance Contract

- Evaluator owner:
  - Codex review pass plus fresh subagent review
- Done contract for this slice:
  - the repo has one honest active workflow surface, and any remaining legacy
    artifact is either retired or explicitly marked historical/advisory
- How the generator and evaluator agreed on done before execution:
  - evaluator requires docs, enforcement, and tests to describe the same state;
    any contradictory active/archive wording is a failure
- Checks the evaluator will use:
  - fresh targeted structure/docs tests
  - `scripts/check_docs.py`
  - `scripts/repo_check.py`
  - `uv run poe verify`
  - subagent review against Anthropic/OpenAI best-practice criteria
- Auto-fail conditions:
  - weakening architecture/runtime/live/perf/Tier A protections
  - leaving docs in a contradictory active/archive state
  - deleting rationale without a surviving pointer or replacement summary

## Generator Work Log

- Planned slice order:
  - decide final status of `QUALITY_SCORE`, `feedback-promotion-log`, and
    `exec-plans`
  - move still-useful rationale into surviving governing docs
  - rewrite the legacy artifacts as historical or advisory records
  - verify that the active entry docs and routing docs still form a coherent
    current surface
- Notes:
  - this docs-only slice does not weaken mechanical checks; it only retires
    these artifacts from active operator guidance
- Blockers or scope changes:
  - code and test retirement of the same legacy artifacts remains a separate
    follow-on slice outside the allowed file set for this task

## Evaluator Review

- Findings:
  - no blocking contradiction remains in the edited docs: active workflow
    authority is now routed through `AGENTS.md`, active plans under
    `docs/plans/`, and the governing design or product indexes
  - `QUALITY_SCORE.md`, `feedback-promotion-log.md`, and `docs/exec-plans/`
    now describe themselves as historical or advisory artifacts instead of
    current workflow authority
  - rationale for promotion policy and control-plane retirement now survives in
    `docs/DESIGN.md`, `core-beliefs.md`, `golden-principles.md`, and
    `doc-gardening.md`
- Verification evidence:
  - `uv run pytest tests/structure/docs/test_system_of_record_docs.py tests/structure/docs/test_plan_indexes.py tests/structure/repo/test_execution_plan_lifecycle.py tests/structure/repo/test_runtime_verification_lane.py -q`
  - `uv run python scripts/check_docs.py`
  - `uv run python scripts/repo_check.py`
- Final disposition:
  - complete for the docs cleanup slice; mechanical retirement of legacy checks
    remains a separate follow-on task
