# jscpd Duplicate Code Gate

- Date: 2026-05-29
- Task: Add a jscpd duplicate-code check and measure the current repository state.
- Status: `complete`
- Risk class: `Tier B`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal: Configure jscpd for Python duplicate-code detection through the repository's Poe command surface, then run it once to report the current duplication failures.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/DESIGN.md`
  - `docs/PLANS.md`
  - `docs/design-docs/architecture-governance.md`
- Why these are governing: This is harness work, so the repo-local command surface, check promotion policy, and safety boundaries govern the change.
- In-repo scope:
  - Add jscpd configuration for Python source, tests, and scripts.
  - Add a Poe task that runs jscpd.
  - Run the new task and record current failure evidence.
- Out-of-repo scope:
  - No CI workflow change.
  - No default `uv run poe check` promotion.
  - No duplicate-code remediation.
- Tier A progression requested: `no`
- Approval record, if required: Not required; this does not modify `trading` or `execution` behavior.
- Verification commands:
  - `uv run poe duplicate-code`
  - `uv run poe repo-check`
- Success criteria:
  - A reproducible `duplicate-code` task exists.
  - jscpd uses conservative duplicate-size defaults and a 3% advisory threshold.
  - Current pass/fail evidence is reported without changing production code.
- Out of scope:
  - Fixing duplicate blocks.
  - Adding Node package management files.
  - Enforcing jscpd in CI or the default local check lane.

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice: Confirm the new jscpd task is present, scoped to Python project paths, and not silently added to the default check lane.
- Acceptance artifact location: This plan's Evaluator Review section.
- How the generator and evaluator agreed on done before execution: Done means setup plus current-state measurement, not remediation.
- Checks the evaluator will use:
  - `uv run poe duplicate-code`
  - `uv run poe repo-check`
- Auto-fail conditions:
  - The default `check` task is changed to require jscpd before baseline decisions are made.
  - The config scans generated/build artifacts instead of repository source paths.
  - The setup requires committing unrelated package-manager metadata.

## Generator Work Log

- Planned slice order:
  - Add plan.
  - Add `.jscpd.json`.
  - Add `duplicate-code` Poe task.
  - Run the new task and repo-check.
- Notes:
  - jscpd is Node-based; this slice uses `npx --yes jscpd` through Poe to avoid introducing a JavaScript package-management surface before the team decides to keep the gate.
  - Added `.jscpd.json` with Python-only scanning for `src`, `tests`, and `scripts`, minimum duplicate size of 10 lines and 100 tokens, and a 0.5% threshold.
  - Added `uv run poe duplicate-code` as a standalone task. It is not part of the default `check` lane.
  - The initial 5-line/50-token setting matched jscpd defaults but was too sensitive for this repository's test suite. SonarQube's non-Java duplication definition and PMD CPD examples both point to 100 tokens, and SonarQube uses 10 lines for non-Java languages other than COBOL/ABAP.
- Blockers or scope changes:
  - None.

## Evaluator Review

- Findings:
  - No setup blocker findings.
  - The new task is standalone and does not change production code, CI, or the default `check` lane.
  - Current duplicate-code signal is concentrated in test/support code. Production `src` alone is below the 3% threshold.
  - The final 10-line/100-token setting avoids the small symmetrical false-positive class while still failing on larger duplicated blocks. The 0.5% threshold is intentionally stricter than broad industry new-code defaults because this repository is small enough that nine large clones should not pass as acceptable noise.
- Verification evidence:
  - Initial diagnostic with 5 lines and 50 tokens failed for the full configured scope: 182 Python files, 27,098 total lines, 127 clones, 1,441 duplicated lines, 5.32% duplicated lines, threshold 3%.
  - Source-only diagnostic with 5 lines and 50 tokens passed: 54 Python files, 7,803 total lines, 12 clones, 121 duplicated lines, 1.55% duplicated lines.
  - Diagnostic `uv run poe duplicate-code` with 10 lines, 100 tokens, and 3% threshold passed: 180 Python files, 27,090 total lines, 9 clones, 183 duplicated lines, 0.68% duplicated lines.
  - Final `uv run poe duplicate-code` with 10 lines, 100 tokens, and 0.5% threshold failed as intended: 180 Python files, 27,090 total lines, 9 clones, 183 duplicated lines, 0.68% duplicated lines.
  - `uv run poe repo-check` passed: `repository checks passed`.
- Final disposition:
  - Complete. jscpd is configured and current-state evidence is recorded; remediation and default-lane promotion remain separate future work.
