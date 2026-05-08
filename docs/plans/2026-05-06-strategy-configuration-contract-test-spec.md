# Strategy Configuration Contract Test Spec Plan

- Date: 2026-05-06
- Task: Write the Strategy Configuration Contract test spec
- Status: `complete`
- Risk class: `Tier B`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal: Create a test-spec document that translates the Strategy Configuration
  Contract product spec into observable test scenarios without expanding product
  scope.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/strategy-configuration-contract.md`
  - `docs/product-specs/parameter-exploration-test-scenarios.md`
  - `docs/product-specs/parameter-exploration.md`
  - `docs/product-specs/wfa-prerequisite-roadmap.md`
  - `docs/product-specs/walk-forward-analysis-readiness.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/PLANS.md`
- Why these are governing:
  - The repo contract requires active planning, scoped changes, and verification.
  - The strategy configuration product spec is the source of truth for this test
    spec.
  - Existing parameter exploration test scenarios define the repository's
    current style for product-driven test documents.
  - Reliability and architecture docs define the test lane, safety tier, and
    package-boundary constraints.
- In-repo scope:
  - Create
    `docs/product-specs/strategy-configuration-contract-test-scenarios.md`.
  - Update `docs/product-specs/index.md` to route test work to the new test
    spec.
  - Optionally add the test spec to related documents in
    `docs/product-specs/strategy-configuration-contract.md`.
  - Record evaluator review and verification evidence in this plan.
- Out-of-repo scope:
  - No code changes, test implementation, connectors, secrets, or external
    files.
- Tier A progression requested: `no`
- Approval record, if required: Not required. This is Tier B documentation.
- Verification commands:
  - `uv run poe repo-check`
  - `git diff --check`
  - `git diff --check --no-index /dev/null docs/product-specs/strategy-configuration-contract-test-scenarios.md; test $? -le 1`
  - `git diff --check --no-index /dev/null docs/plans/2026-05-06-strategy-configuration-contract-test-spec.md; test $? -le 1`
- Success criteria:
  - The test spec covers intent/core contracts, scope/non-scope, unit scenarios,
    integration scenarios, contract/regression/doc scenarios as needed, normal
    flows, failure flows, edge cases, fixture strategy, fake/mock policy,
    what to verify/not verify, priorities, success conditions, and open
    questions.
  - The test spec stays within Stage 1 product scope and labels Stage 2/3 tests
    as downstream.
  - Testing principles are informed by fresh web research and cite the sources
    used in the final response.
  - Fresh verification passes.
- Out of scope:
  - Implementing tests.
  - Implementing `StrategyConfig`.
  - Changing product decisions or resolving Stage 2/3 open questions.
  - WFA implementation.

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice:
  - Review the new test spec against the product spec and active plan.
  - Confirm the document tests externally observable contracts rather than
    private implementation details.
  - Confirm Stage 2/3 tests are separated from Stage 1 required scope.
  - Confirm no source code was changed.
- Acceptance artifact location:
  - This plan's `Evaluator Review` section.
- How the generator and evaluator agreed on done before execution:
  - The planner contract above defines allowed files, required sections, and
    verification before edits.
- Checks the evaluator will use:
  - Manual diff review.
  - `uv run poe repo-check`
  - `git diff --check`
- Auto-fail conditions:
  - Any code/test implementation change.
  - Any new product requirement not present in the product spec.
  - Any Stage 2/3 scenario presented as Stage 1 required completion.
  - Any WFA implementation test requirement.

## Generator Work Log

- Planned slice order:
  1. Read product spec and current test-spec style.
  2. Review current test tree and relevant parameter-study tests for placement
     consistency.
  3. Incorporate external testing best-practice research.
  4. Create the test spec and routing updates.
  5. Review diff and run verification.
- Notes:
  - Existing untracked WFA/spec docs are prior session work and will not be
    reverted.
  - Web research used:
    - Google Testing Blog behavior-focused testing guidance.
    - Martin Fowler / Ham Vocke practical test pyramid guidance.
    - pytest good integration practices and fixture guidance.
  - Created
    `docs/product-specs/strategy-configuration-contract-test-scenarios.md`.
  - Updated `docs/product-specs/index.md` to route strategy configuration
    contract test work to the new test spec.
  - Updated `docs/product-specs/strategy-configuration-contract.md` related
    documents to link the new test spec.
- Blockers or scope changes:
  - None.

## Evaluator Review

- Findings:
  - No blocking findings.
  - The new test spec translates the Stage 1 product contract into observable
    test scenarios without adding new product requirements.
  - Stage 2 `ParameterStudy` migration and Stage 3 reporting scenarios are
    clearly labeled as downstream test hooks rather than Stage 1 completion
    gates.
  - The test spec emphasizes behavior/contract testing over private
    implementation details, uses the existing repo test taxonomy, and avoids WFA
    implementation scope.
  - No code or test implementation files were modified.
- Verification evidence:
  - `uv run poe repo-check` -> `repository checks passed`
  - `git diff --check` -> exit 0
  - `git diff --check --no-index /dev/null docs/product-specs/strategy-configuration-contract-test-scenarios.md; test $? -le 1` -> exit 0
  - `git diff --check --no-index /dev/null docs/product-specs/strategy-configuration-contract.md; test $? -le 1` -> exit 0
  - `git diff --check --no-index /dev/null docs/plans/2026-05-06-strategy-configuration-contract-test-spec.md; test $? -le 1` -> exit 0
- Final disposition:
  - Accepted for this documentation slice.
