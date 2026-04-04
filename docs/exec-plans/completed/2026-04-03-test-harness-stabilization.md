# Test Harness Stabilization Plan

**Goal:** Strengthen `quantcraft`'s test and verification harness so agent-caused regressions are caught more reliably at the artifact, behavior, and runtime-verification levels without broadening current product scope.

**Architecture:** Keep the current `unit / integration / structure / smoke / perf` taxonomy and the existing `scripts/ + poe` command contract. Improve the harness by adding stronger artifact-backed user-journey checks, replacing a few syntax-level checks with behavior-level checks where they are the only effective guard, and codifying a stricter explicit verification lane for runtime-sensitive work rather than weakening the current default-lane policy.

**Tech Stack:** Python 3.13, `pytest`, `coverage`, `poethepoet`, repo-local `scripts/`, package build artifacts

## Lifecycle

- status: completed
- completed_on: 2026-04-04
- created_on: 2026-04-03

## Current Status

- Slice 1: complete
- Slice 2: complete
- Slice 3: complete
- Slice 4: complete
- Slice 5: complete

## Context

This plan exists because `quantcraft` is intentionally agent-first and depends on a mechanical harness to keep the current implemented scope stable.

The current repository already has strong coverage and a meaningful default verification bundle:

- `uv run poe verify` passes
- `uv run poe perf-check` passes
- source coverage floor is enforced at `90%`
- `src/quantcraft/trading/domain/` is enforced at `100%` line coverage

That baseline is good, but harness quality depends on more than raw pass counts.
The remaining question is whether the current tests validate the behaviors that matter most when an agent makes a plausible mistake.

## External Validation Lens

This plan was re-validated against Anthropic's article:

- `https://www.anthropic.com/engineering/harness-design-long-running-apps`

The article's most relevant harness lessons for this repository are:

1. evaluator work should be separate from generation rather than trusting self-praise
2. quality criteria should be concrete and gradable
3. important checks should interact with the application the way a user would
4. each work slice should have an explicit contract for what "done" means
5. hard thresholds are useful when they protect a specific behavior rather than acting as fake rigor

For `quantcraft`, that implies the best stabilization work is not "add more tests everywhere."
It is to improve the places where current checks are too indirect, too source-tree-local, or too weakly tied to real user journeys.

## Revalidated Findings

### 1. Artifact-backed import validation is still a real gap

This remains a valid issue.

Current local smoke tests import from the repository checkout while `tests/conftest.py` explicitly inserts the repository root onto `sys.path`.
That is useful for local development, but it does not prove that the built wheel exposes the documented public import surface in a clean install environment.

Why this matters under the Anthropic lens:

- this is a canonical user journey
- it should be validated the way a user experiences it
- source-tree imports are not an adequate substitute for install-artifact validation

### 2. A small number of semantic contracts are under-tested even though nearby coverage is high

This also remains a valid issue.

The most obvious current example is the test named to cover the "sell is exit-only in the current long-only scope" rule.
That test currently checks signature shape rather than the behavioral contract that would catch a regression toward accidental short-entry semantics.

Why this matters:

- the repository has high line coverage, but some business-important semantics still need direct behavioral assertions
- agent regressions often preserve signatures and names while changing behavior

### 3. Some critical harness tests are still too syntax-oriented

This finding is partially valid and needs narrowing.

Not all string-based tests are bad.
Some are intentionally doc-discoverability tripwires and are acceptable in `tests/structure`.
The actual problem is narrower:

- a few tests that protect important harness behavior currently verify source text rather than importing and exercising the governing logic
- those checks are weaker when they are the only strong guard for a policy

The goal is therefore not to remove string-based checks wholesale.
The goal is to upgrade the highest-value ones to behavior-first checks and keep string-level checks only where discoverability is the actual contract being protected.

### 4. `perf-check` being excluded from default `verify` is not, by itself, a bug

This earlier concern does **not** survive re-validation as originally framed.

The repository explicitly documents that performance checks are:

- explicit-only
- excluded from the default `verify` lane

That policy is intentional and consistent with the current repository contract.

The real gap is different:

- runtime-sensitive work does not yet have a dedicated stricter explicit lane or an equally explicit trigger contract that is easy for agents to follow mechanically

The correct response is not "put perf in default verify."
The correct response is "make the stronger explicit lane and its trigger conditions clearer and easier to execute."

## Non-Goals

This plan does not:

- change live-test explicit-only policy
- put performance checks into the default `verify` lane
- broaden the current product scope beyond the implemented `data`, `research`, and Backtest MVP surfaces
- redesign the whole doc or repository-check system
- introduce CI-only workflows that bypass the documented local command surface

## Slice Plan

### Slice 1: Add Artifact-Backed Public Import Validation

**Intent:** Turn the "clean install to public imports" user journey into a real artifact-backed check rather than a source-tree-only smoke test.

**Target areas:**

- `tests/smoke/local/`
- `tests/integration/commands/`
- package-build verification docs if needed

**Likely work:**

- add a smoke/integration check that builds the wheel and validates documented public imports from an isolated install target
- ensure the check exercises:
  - `quantcraft`
  - `quantcraft.data`
  - `quantcraft.research`
- keep the existing fast source-tree smoke test if it still provides value, but stop treating it as sufficient evidence for clean-install behavior

**Acceptance:**

- a broken wheel-level public import surface is caught even if source-tree imports still work
- the test remains repo-local and uses the documented command surface
- the check is stable enough for repeated agent use

### Slice 2: Replace Weak Semantic Proxies With Behavioral Tests

**Intent:** Upgrade a small number of tests whose names claim business behavior but whose assertions currently only check shapes, signatures, or placeholders.

**Target areas:**

- `tests/unit/research/application/`
- `tests/integration/research/`
- any closely related strategy/backtest fixtures

**Likely work:**

- replace the current `sell`-surface proxy with a direct behavioral test that proves exit-only semantics in the current long-only slice
- review other narrow cases where the test title promises business behavior but the assertion only validates API shape
- prefer deterministic behavior assertions over reflection-based checks when the rule is user-visible

**Acceptance:**

- accidental short-entry behavior or similar semantic drift is caught by tests
- high-importance strategy/runtime semantics are protected by executable behavior checks rather than signatures alone

### Slice 3: Strengthen Critical Harness Tests From Text Checks To Logic Checks

**Intent:** Keep structure tests useful, but convert the highest-value harness checks to import-and-exercise behavior where that produces stronger protection.

**Target areas:**

- `tests/structure/repo/`
- `tests/unit/scripts/`
- `scripts/coverage_check.py`
- `tests/conftest.py`

**Likely work:**

- keep doc-discoverability checks where the contract is literally discoverability
- replace or supplement critical raw-string checks with tests that:
  - import the governing module
  - inspect structured values
  - execute policy logic directly
- prefer testing `coverage_check` constants and behavior over searching for string literals in source text
- prefer testing collection and skip behavior over searching for option names in text, except where discoverability itself is the protected behavior

**Acceptance:**

- important harness rules fail when logic changes, not only when strings change
- structure tests remain legible and cheap
- redundant low-signal checks are reduced where they do not protect real behavior

### Slice 4: Codify A Stronger Explicit Verification Lane For Runtime-Sensitive Changes

**Intent:** Preserve the current explicit-only performance policy while making it easier for agents to run the right extra checks when they touch runtime-sensitive areas.

**Target areas:**

- `pyproject.toml`
- `docs/RELIABILITY.md`
- `AGENTS.md`
- `docs/references/developer-tasks.md`
- `tests/structure/repo/`

**Likely work:**

- define a stricter explicit verification lane such as a dedicated research/runtime verification task
- document when agents must run it
- tie those trigger conditions to specific file areas such as:
  - `src/quantcraft/research/_indicator_runtime.py`
  - `src/quantcraft/research/_indicator_kernels.py`
  - `src/quantcraft/research/ta.py`
  - `src/quantcraft/research/application/backtest.py`
  - canonical perf fixtures
- add structure tests that keep the lane and its documentation aligned

**Acceptance:**

- default `verify` remains unchanged
- runtime-sensitive work has a clearly documented stronger explicit lane
- agents can discover the rule mechanically from repository docs and tests

### Slice 5: Increase Harness Self-Coverage Where Policy Logic Is Concentrated

**Intent:** Improve confidence in the repository's own evaluation machinery, especially where one module centralizes many repo-check rules.

**Target areas:**

- `src/quantcraft/_repo_tools.py`
- `tests/structure/repo/`
- `tests/unit/` where finer-grained helper coverage is appropriate

**Likely work:**

- identify the highest-risk uncovered branches in `_repo_tools.py`
- add focused tests for the branches that protect:
  - plan lifecycle enforcement
  - quality-score validation
  - system-of-record doc checks
  - architecture-rule enforcement
- avoid chasing coverage mechanically where no important branch or policy is protected

**Acceptance:**

- `_repo_tools.py` has better coverage in the logic paths that matter for agent feedback loops
- added tests are branch-motivated and policy-motivated, not coverage-padding

## Verification Strategy

During implementation, use the existing repository command surface.

Per slice, run the narrowest relevant checks first, then the broader bundle:

- `uv run pytest -q <targeted tests>`
- `uv run ruff check .`
- `uv run mypy src`
- `uv run python scripts/repo_check.py`

At milestone checkpoints:

- `uv run poe verify`

For Slice 4 or any runtime-sensitive change:

- `uv run poe perf-check`

If artifact-backed install validation is added:

- include the new artifact smoke test in the documented command surface and the corresponding structure checks

## Success Criteria

This plan is successful when all of the following are true:

1. the repository can catch a broken wheel-level import surface that source-tree tests would miss
2. important long-only strategy/backtest semantics are protected by behavioral tests
3. critical harness policies are validated through logic checks where behavior matters most
4. runtime-sensitive work has an explicit stronger verification path without changing the default-lane policy
5. the harness becomes more trustworthy for future agent work without becoming materially noisier or harder to run

## Human-Gate Conditions

Stop and ask the human if implementation pressure requires any of the following:

- changing the default explicit-only policy for live or performance tests
- broadening current backtest or research product scope
- introducing CI-only contracts that diverge from the repo-local command surface
- changing Tier A semantics under `trading` rather than only improving their verification
