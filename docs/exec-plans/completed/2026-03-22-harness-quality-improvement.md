# Harness Quality Improvement Plan

> **For Codex:** REQUIRED SUB-SKILLS: use `subagent-driven-development` to execute this plan slice-by-slice, and require every worker/reviewer subagent to read `docs/references/openai-harness-engineering.md` plus the slice-relevant architecture/spec docs before touching code.

**Goal:** Upgrade the repository from a good agent-workable harness to a more self-correcting OpenAI-style harness by fixing the highest-signal drift, status, and feedback-loop weaknesses discovered after the Backtest MVP implementation batch.

**Architecture:** This batch does not expand product scope. It strengthens the repository control plane: canonical docs, plan lifecycle, quality-state tracking, golden-principles capture, and mechanical checks. The implementation should prefer narrow doc contracts plus structure/repo tests over broad refactors.

**Tech Stack:** Python 3.12+, `uv`, `pytest`, `ruff`, `mypy`, repo-local `scripts/` harness

## Lifecycle

- status: completed

## Current Status

- Slice 1: complete
- Slice 2: complete
- Slice 3: complete
- Slice 4: complete
- Slice 5: complete

## Why This Batch Exists

The repository already has:

- approved architecture and governance docs
- an approved Backtest MVP spec
- a completed first MVP implementation batch

But the current harness still has several high-value weaknesses:

- a spec vs enforcement contradiction around deferred event types
- stale and weakly enforced quality-state tracking
- execution-plan lifecycle ambiguity
- design/spec indexes that are not yet true status maps
- missing canonical golden-principles and feedback-promotion artifacts

This batch addresses those harness-quality issues before more feature work expands the codebase.

## Success Conditions

This batch is complete only when all of the following are true:

1. the approved Backtest MVP spec and mechanical enforcement agree about deferred event types
2. `docs/QUALITY_SCORE.md` becomes a freshness-aware, evidence-backed artifact rather than a stale static table
3. `repo_check` fails when the quality score is missing required metadata, required areas, or freshness fields
4. execution plans carry explicit lifecycle metadata, and the repository catches contradictions between `active/` and `completed/`
5. the completed Backtest MVP implementation plan is no longer ambiguously listed as active work
6. design-doc and product-spec indexes become real status maps with explicit status/canonical/applicability fields
7. the repository has a canonical `golden-principles` document and a canonical `feedback-promotion-log` artifact
8. doc-gardening/governance docs explicitly describe how repeated review feedback becomes docs or checks
9. structure/repo tests cover the new quality-score, plan-lifecycle, and index-status contracts
10. the full harness verification surface passes from the current repository state

## Explicit Non-Goals

This batch does not:

- change Backtest MVP runtime behavior
- introduce new trading semantics
- add live or paper trading functionality
- implement diff-aware Tier A gates
- enforce every intra-context layer edge mechanically
- rewrite the remaining draft `trading-kernel-contract-draft-ko.md`

Those may become later harness batches, but they are not required to close the current validated weaknesses.

## Required Reading Before Any Task

Every worker and reviewer must read:

- `AGENTS.md`
- `docs/references/openai-harness-engineering.md`
- `docs/design-docs/quantcraft-architecture.md`
- `docs/design-docs/architecture-governance.md`
- `docs/product-specs/backtest-mvp.md`
- `docs/QUALITY_SCORE.md`
- `docs/PLANS.md`

Additionally:

- tasks that touch quality scoring must read `scripts/update_quality_score.py`
- tasks that touch plan lifecycle must read `docs/exec-plans/active/index.md` and `docs/exec-plans/completed/index.md`
- tasks that touch repository checks must read `src/quantcraft/_repo_tools.py` and the relevant `tests/structure/repo/` files

## Non-Negotiable Guardrails

- Do not expand product scope.
- Do not change the approved top-level bounded contexts.
- Do not weaken repository checks in order to make docs “pass”.
- Do not encode speculative long-term trading semantics into this batch.
- Do not bypass the documented `scripts/ + poe` harness contract.
- Prefer making the system of record more truthful over making it more verbose.

## Slice Plan

### Slice 1: Converge Backtest MVP Spec And Enforced Contract

**Intent:** Remove the contradiction between the approved Backtest MVP spec and the mechanical enforcement around deferred event types.

**Ownership:**

- `docs/product-specs/`
- `tests/structure/architecture/`
- `tests/unit/trading/`

**Files:**

- Modify: `docs/product-specs/backtest-mvp.md`
- Modify: `tests/structure/architecture/test_backtest_mvp_slice1.py`
- Modify: `tests/unit/trading/test_contracts.py`

**Acceptance:**

- the approved MVP spec clearly marks `OrderEvent` and `TimerEvent` as deferred for the current slice
- structure/unit tests enforce the same contract
- no doc/test contradiction remains about the current slice event surface

### Slice 2: Make Quality Score A Trustworthy Harness Artifact

**Intent:** Replace the current stale static quality note with a freshness-aware, evidence-backed repository artifact and enforce that contract mechanically.

**Ownership:**

- `docs/`
- `scripts/`
- `src/quantcraft/`
- `tests/structure/repo/`

**Files:**

- Modify: `docs/QUALITY_SCORE.md`
- Modify: `scripts/update_quality_score.py`
- Modify: `src/quantcraft/_repo_tools.py`
- Modify/Create: relevant repo-structure tests under `tests/structure/repo/`

**Acceptance:**

- `QUALITY_SCORE.md` includes explicit metadata such as `as_of`, rubric/evidence expectations, and tracked areas
- the tracked areas match current implemented reality at least for `data`, `research`, `trading`, `execution`, `docs_system`, and `verification`
- `repo_check` fails if required metadata or required area rows are missing
- the update script produces output that is meaningfully tied to the score contract instead of just echoing generic issues

### Slice 3: Fix Execution-Plan Lifecycle Ambiguity

**Intent:** Make active/completed execution-plan state legible and mechanically enforceable.

**Ownership:**

- `docs/PLANS.md`
- `docs/exec-plans/active/`
- `docs/exec-plans/completed/`
- `src/quantcraft/`
- `tests/structure/repo/`

**Files:**

- Modify: `docs/PLANS.md`
- Modify: `docs/exec-plans/active/index.md`
- Modify: `docs/exec-plans/completed/index.md`
- Move or reclassify: `docs/exec-plans/active/2026-03-21-backtest-mvp-implementation.md`
- Modify: `src/quantcraft/_repo_tools.py`
- Modify/Create: relevant repo-structure tests under `tests/structure/repo/`

**Acceptance:**

- execution plans have explicit status metadata
- a plan whose slices are all complete is not left ambiguously active without an explicit reason
- the completed Backtest MVP implementation plan is indexed consistently with its actual lifecycle state
- `repo_check` catches obvious active/completed contradictions

### Slice 4: Upgrade Design/Product Indexes Into Real Status Maps

**Intent:** Turn the current flat index lists into actual status maps that autonomous agents can rely on.

**Ownership:**

- `docs/design-docs/`
- `docs/product-specs/`
- `AGENTS.md`
- `src/quantcraft/`
- `tests/structure/repo/`

**Files:**

- Modify: `docs/design-docs/index.md`
- Modify: `docs/product-specs/index.md`
- Modify: `AGENTS.md`
- Modify: `src/quantcraft/_repo_tools.py`
- Modify/Create: relevant repo-structure tests under `tests/structure/repo/`

**Acceptance:**

- both indexes expose explicit status metadata, canonical status, and applicability/read-when guidance
- `AGENTS.md` wording matches the actual index format
- `repo_check` validates the required headers/fields for those indexes

### Slice 5: Add Golden Principles And Feedback-Promotion Loop

**Intent:** Make the OpenAI-style garbage-collection loop explicit, durable, and discoverable in the repository itself.

**Ownership:**

- `docs/design-docs/`
- `docs/`
- `src/quantcraft/`
- `tests/structure/docs/`
- `tests/structure/repo/`

**Files:**

- Create: `docs/design-docs/golden-principles.md`
- Create: `docs/feedback-promotion-log.md`
- Modify: `docs/design-docs/doc-gardening.md`
- Modify: `docs/design-docs/core-beliefs.md`
- Modify: `docs/design-docs/index.md`
- Modify: `docs/QUALITY_SCORE.md`
- Modify: `src/quantcraft/_repo_tools.py`
- Modify/Create: relevant structure tests under `tests/structure/docs/` and `tests/structure/repo/`

**Acceptance:**

- the repository has a canonical golden-principles document
- the repository has a canonical feedback-promotion log artifact
- doc-gardening/governance docs describe how repeated review findings become docs or checks
- repository checks fail if the new canonical docs disappear or become unindexed

## Review Protocol Per Slice

For every slice, use this order:

1. worker subagent implements the slice
2. spec reviewer checks only against approved docs and this plan
3. code-quality reviewer checks maintainability, drift risk, and OpenAI-style harness alignment
4. only then move to the next slice

Do not let a later slice start while a prior slice still has open review findings.

## Verification Gates Per Slice

At the end of every slice:

- run the slice-relevant tests first
- run `uv run ruff check .`
- run `uv run mypy src`
- run `uv run python scripts/repo_check.py`

At the end of the batch:

- run `uv run pytest tests/structure -q`
- run `uv run pytest -q`
- run `uv build`

## Human-Gate Conditions

Stop and ask the human if any of the following occurs:

- an approved canonical doc must be materially re-scoped
- a proposed harness rule would block normal Tier B development without strong benefit
- a rule would force promotion of still-open trading-kernel draft semantics
- a reviewer finds a conflict between approved canonical docs

## Summary

This batch is successful when the repository is not just documented, but measurably more truthful about its own quality state, plan lifecycle, status maps, and feedback-promotion loop.
