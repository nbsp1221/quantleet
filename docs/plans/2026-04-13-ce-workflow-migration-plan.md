# Compound Engineering Workflow Evaluation And Corrective Migration Plan

## Status

- Status: `proposed`
- Class: `migration plan`
- Scope: evaluate whether Compound Engineering principles should replace
  `quantcraft`'s local workflow bureaucracy, without making the repo entry
  contract depend on opaque external commands

Related documents:

- [../../AGENTS.md](../../AGENTS.md)
- [../../ARCHITECTURE.md](../../ARCHITECTURE.md)
- [../RELIABILITY.md](../RELIABILITY.md)
- [../SECURITY.md](../SECURITY.md)
- [../design-docs/architecture-governance.md](../design-docs/architecture-governance.md)
- [../product-specs/backtest-mvp.md](../product-specs/backtest-mvp.md)
- [../product-specs/research-ergonomics.md](../product-specs/research-ergonomics.md)
- [TEMPLATE.md](TEMPLATE.md)
- [trials/TEMPLATE.md](trials/TEMPLATE.md)
- [2026-04-14-legacy-control-plane-retirement.md](2026-04-14-legacy-control-plane-retirement.md)

## Goal

Test whether the repo should adopt a CE-aligned workflow model while keeping the
repo contract self-contained.

The target workflow behavior is:

1. planner creates a structured plan artifact
2. generator executes only the approved in-repo slice
3. evaluator reviews against the plan and fresh verification evidence

What this plan is **not** allowed to do:

- treat external `ce:*` commands as the standing repo contract
- rewrite authority before evidence exists
- delete complexity before proving it is non-load-bearing
- weaken financial or architecture hard gates

## Corrective Judgment

The previous migration slice made two mistakes:

1. it rewrote the repo entry contract too early
2. it treated a blocked or host-unavailable record as if it were evidence of a
   successful authority trial

This corrective plan resets sequencing.

Until the evidence gate passes:

- `AGENTS.md` must stay repo-local and self-contained
- plans and trials must be structured artifacts
- CE remains a candidate workflow model, not the active repo authority

## Harness Principles Applied Here

This migration follows the harness-design principles summarized in the
repo-local harness reference set, especially
[`../references/openai-harness-engineering.md`](../references/openai-harness-engineering.md):

- separate planner, generator, and evaluator responsibilities
- pass state through structured artifacts rather than implicit chat memory
- remove complexity only after proving it is not load-bearing

In this repo that means:

- active plan artifacts live under `docs/plans/`
- evaluator evidence lives in review notes or trial records
- hard gates stay mechanical until a narrower successor is proved

## Current State Inventory

### Protected invariants

These are real safety or correctness constraints and are not optional:

- Tier A human gate for `trading` and `execution`
- architecture dependency boundaries
- explicit runtime/perf/live verification policy
- canonical backtest and research contract tests

### Bureaucratic control-plane candidates

These are legitimate delete or simplification candidates, but only after proof:

- quality score freshness and evidence bookkeeping
- status-map metadata enforcement
- execution-plan lifecycle bookkeeping
- broad system-of-record inventory checks
- duplicated workflow reference docs

## Required End State

If the migration succeeds, the repo should end up with:

- one self-contained repo entry contract
- structured planner/generator/evaluator artifacts
- a thinner set of repo-local hard gates
- no workflow bureaucracy kept only out of habit

If the migration fails, the repo should still keep:

- the repaired self-contained contract
- the existing hard gates
- an honest record of what evidence was missing

## Repo Contract Requirement

The standing repo contract must remain understandable to a newcomer reading only
repo-local files.

That means:

- `AGENTS.md` may describe workflow semantics
- `AGENTS.md` may point to repo-local plans, specs, and checks
- `AGENTS.md` may mention Compound Engineering as an experiment or migration
  topic
- `AGENTS.md` may **not** require knowledge of an external `ce:*` command
  surface in order to understand how to work in this repo

External host tooling is an implementation detail.

## Invariant Mapping

Every retained invariant needs a post-migration owner.

| Invariant | Current enforcer | Required successor state |
| --- | --- | --- |
| Tier A work needs human approval | `AGENTS.md`, `docs/SECURITY.md`, `docs/RELIABILITY.md` | active plan contains verifiable approval record before work is treated as approved |
| Architecture boundaries stay mechanical | `scripts/check_architecture.py`, `tests/structure/architecture/test_domain_boundaries.py` | retained or replacement mechanical check still passes |
| Runtime-sensitive work triggers stronger verification | `docs/RELIABILITY.md`, `tests/structure/repo/test_runtime_verification_lane.py` | runtime lane remains explicit and testable |
| Live tests remain explicit-only | live-test policy docs/tests | live-test policy remains outside the default lane |
| Perf checks remain explicit-only | `uv run poe perf-check`, perf tests | perf lane remains outside the default lane |
| Coverage expectations stay intentional | `scripts/coverage_check.py`, coverage harness tests | no silent removal without an approved narrower replacement |
| Canonical product behavior stays anchored in tests | integration/perf tests under `tests/integration/research/` and `tests/perf/` | canonical tests remain authoritative during workflow migration |

## Trial Design

Before any authority rewrite or destructive cleanup:

- use the current self-contained repo contract
- keep current hard gates active
- compare candidate workflow behavior on real `quantcraft` tasks

### Candidate workflow under test

The candidate workflow is CE-inspired behavior, not a required command name:

1. planner artifact first
2. execution against repo-local hard gates
3. evaluator review against plan plus fresh verification evidence

### Comparator set

Compare the candidate workflow against:

- baseline current local flow
- slim-local comparator with low-signal bureaucracy suppressed

### Task selection rules

Use at least three tasks from different risk profiles:

1. one current implemented-scope or approved next-slice research task
2. one runtime-sensitive or architecture-sensitive task from a current product
   contract
3. one onboarding, discoverability, or approval-sensitive task

At least one task must exercise a canonical user journey covered by
`backtest-mvp` or `research-ergonomics`.

### Required measures

For each task, record:

- time to reach an implementation-ready plan
- number of clarifying loops before execution
- review findings count and quality
- whether runtime, live, perf, and architecture gates were invoked correctly
- ambiguity about source of truth or required hard gates

### Trial record types

Two record types are valid:

- `authority-trial`: a scored comparison that can count toward the evidence gate
- `exception-record`: a blocked or host-unavailable run that records why a
  scored trial did not happen

Exception records are useful but do **not** satisfy the evidence gate.

## Evidence Gate

The migration may advance only if all of the following are true:

1. at least three real `quantcraft` tasks were compared
2. no task bypassed Tier A, runtime, live, perf, or architecture controls
3. candidate workflow planning/review produced equal or better reviewer signal
   than both comparators
4. at least one task showed materially lower workflow friction than both
   comparators
5. no evaluator concluded that workflow authority remained ambiguous
6. the trial artifact is signed off by a named human reviewer

If any one of those is false:

- authority rewrite is blocked
- cleanup is blocked
- CE remains an experiment, not repo authority

## Migration Phases

### Phase 0. Corrective Reset

Tasks:

- restore `AGENTS.md` to a self-contained repo entry contract
- restore `docs/DESIGN.md` and `docs/PLANS.md` to pointer docs
- ensure indexes remain routing aids rather than workflow manuals
- mark any blocked or host-unavailable trial record as `fail`, not `pass`

Success criteria:

- a newcomer can understand the repo workflow from repo-local docs only
- the current trial state is represented honestly

### Phase 1. Trial Contract

Tasks:

- define the active plan template for planner artifacts
- define the trial/exception template for evaluator evidence
- lock the comparison rubric before running scored trials
- keep hard gates unchanged while the candidate workflow is being evaluated

Success criteria:

- the planner, generator, and evaluator artifacts are all explicit
- the trial template distinguishes scored trials from exception records

### Phase 1.5. Evidence Gate

Do not rewrite authority or delete legacy controls until the evidence gate is
actually satisfied.

If the evidence is mixed, incomplete, or blocked:

- stop after the corrective reset and trial contract
- keep the repaired self-contained repo contract in place

### Phase 2. Authority Rewrite

Only after a passing evidence gate:

- rewrite any remaining workflow docs around the proven workflow behavior
- keep the repo contract self-contained even if operators use CE-capable hosts
- preserve explicit routing to governing design docs and product specs

Success criteria:

- one short repo read explains how to work here
- one active plan artifact explains what the current task is doing
- one evaluator artifact explains whether the work met the plan

### Phase 3. Hard-Gate Rebuild

Tasks:

- decide which existing gates remain untouched
- rewrite only the gates whose current implementation is coupled to old
  bureaucracy
- verify every retained invariant still has a mechanical owner

### Phase 4. Delete Proven Non-Load-Bearing Controls

Only after evidence and invariant mapping are complete:

- remove quality score scaffolding if it protects no retained invariant
- remove status-map bookkeeping if routing still works without it
- remove execution-plan lifecycle bookkeeping if active-plan routing remains
  clear
- simplify repo-check logic that exists only to police obsolete workflow
  metadata

## Stop Conditions

Stop the migration if any of these become true:

- the repo contract cannot stay self-contained
- a hard gate would be demoted into prose-only guidance
- the candidate workflow cannot beat both comparators on the documented
  evidence gate
- cleanup requires deleting controls that still protect a live failure mode

## Verification Plan

The corrective slice and any later migration work must keep proving:

- architecture boundaries mechanically
- runtime verification trigger paths mechanically
- live/perf policy mechanically
- canonical backtest and research behavior through tests

Minimum commands for this corrective docs slice:

- `uv run pytest tests/structure/docs/test_plan_indexes.py -q`
- `uv run pytest tests/structure/docs/test_system_of_record_docs.py -q`
- `uv run python scripts/check_docs.py`
- `uv run python scripts/repo_check.py`
