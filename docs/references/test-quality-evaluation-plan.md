# Test Quality Evaluation Plan

Use this plan when evaluating whether the `quantleet` test suite is strong
enough to support new feature work. The output of this plan is a test quality
report with concrete numbers, qualitative LLM findings, and recommended gate
changes.

This is an evaluation plan, not a CI implementation plan. It defines what to
measure, how to review the tests, and how to turn the results into a report.

## Purpose

The goal is to evaluate test-code quality before increasing future feature
velocity. A good test suite should make failures clear, deterministic, and
useful. It should verify the external contracts that `quantleet` promises to
users, not merely execute implementation details.

The evaluation must keep three evidence types separate:

- mechanical checks: objective pass/fail or numeric measurements
- LLM-assisted critique: structured qualitative review of test design
- human judgment: product and risk decisions about which gates are worth
  enforcing

Do not collapse these into one score. A high coverage number does not prove
that the tests assert meaningful behavior, and an LLM review is evidence rather
than final authority.

## Source References

This plan is based on the repository reliability model plus common industry
testing guidance:

- Google Testing Blog, "Code Coverage Best Practices"
- Google Testing Blog, "Mutation Testing"
- Google Testing Blog, "Flaky Tests at Google and How We Mitigate Them"
- Google Testing Blog, "Where do our flaky tests come from?"
- pytest documentation, "Flaky tests"
- Martin Fowler / Thoughtworks, "The Practical Test Pyramid"

## Evaluation Output

Each evaluation run should produce a report with these sections:

1. Executive summary
2. Scope and commands
3. Quantitative metrics
4. Qualitative LLM review
5. Test portfolio assessment
6. Risk findings
7. Recommended gate changes
8. Open human decisions

The report should include concrete values, not only prose. Examples:

- total tests: `739`
- skipped tests: `4`
- xfailed tests: `0`
- line coverage: `92.4%`
- branch coverage: `88.1%`
- slowest test duration: `2.31s`
- top 10 slow tests
- flaky reproduction result: `0 failures across 5 repeated runs`
- mutation score: `76%` on the selected target
- survived mutants: `18`
- killed mutants: `57`
- equivalent or ignored mutants: `5`
- LLM review result: `2 blocker`, `5 important`, `9 minor`

## Quantitative Evaluation

### Baseline Test Inventory

Collect:

- total number of tests
- number of tests by directory:
  - `tests/unit`
  - `tests/integration`
  - `tests/perf`
  - `tests/structure`
  - `tests/smoke`
- number of skipped tests
- number of xfail tests
- number of tests using network, filesystem, randomness, time, or external
  services
- number of tests marked as live or performance-only

Purpose:

- detect hidden test debt
- make the test portfolio visible
- identify areas where too many guarantees depend on one test level

### Pass/Fail Reliability

Collect:

- default test command result
- full verification command result
- failed test count
- error count
- skipped count
- elapsed runtime

Recommended command surface:

```bash
uv run poe verify
uv run poe verify-runtime
```

Use `verify-runtime` when the evaluation touches runtime-sensitive backtest or
research behavior.

### Coverage

Collect:

- global line coverage
- branch coverage, if available
- file-level coverage for low-coverage files
- coverage for Tier A domain paths, if applicable
- uncovered lines for user-facing or contract-heavy modules

Coverage is a minimum reliability floor. It answers whether code was executed;
it does not prove the assertions are strong.

Recommended interpretation:

- below the repository floor: blocker
- above the repository floor but missing critical contract paths: important
- high coverage with weak assertions: qualitative finding, not a pass

### Assertion Strength

Collect:

- tests with no meaningful assertions
- tests that only assert object existence
- tests that only assert no exception
- tests with broad or vague assertions
- tests that check exact internal representation instead of public behavior

This can be measured partly with static search and partly with LLM review.

Example weak patterns to inspect:

- `assert result is not None`
- `assert len(items) > 0`
- `with pytest.raises(Exception)`
- excessive snapshot or exact-string assertions for non-contract text

### Mutation Testing

Mutation testing evaluates whether tests detect small injected defects. It is
the strongest quantitative signal for assertion quality, but it can be
expensive. Use it first as a targeted audit, not as a default full-suite gate.

Candidate Python tools:

- `mutmut`
- `cosmic-ray`
- `pytest-gremlins`
- `mutatest`

Recommended first use:

- target one high-value module or feature slice
- prefer public contract paths over internal helper-only paths
- record killed, survived, timeout, and ignored mutants
- inspect survived mutants before turning the score into a gate

Report fields:

- tool used
- target path
- command
- elapsed time
- total mutants
- killed mutants
- survived mutants
- timeout mutants
- ignored or equivalent mutants
- mutation score
- top survived mutant examples

### Flakiness And Determinism

Collect:

- repeated-run result for selected tests
- randomized-order result, if a tool is available
- failures that disappear without code changes
- tests that depend on time, randomness, external services, global state, or
  ordering
- tests that require retries to pass

Recommended starting approach:

- repeat the full default test suite a small number of times before release
- repeat targeted integration tests that touch data, backtest, or research
  flows
- randomize order in a separate audit lane rather than silently retrying
  failures

Retries may reduce CI noise, but they should not hide unreliable tests from the
quality report.

### Runtime Cost

Collect:

- total test runtime
- runtime by test category
- slowest 10 tests
- tests over the agreed slow-test threshold
- runtime change from the previous evaluation

Interpretation:

- slow tests are not automatically bad
- expensive tests must justify their contract value
- release-only or explicit lanes are acceptable for valuable expensive tests

## Qualitative LLM Review

LLM review should inspect test design and explain findings in human-readable
terms. The LLM should review tests against external contracts, product specs,
and public APIs rather than implementation preferences.

### Review Inputs

Provide the reviewer:

- relevant product or design spec
- relevant source files
- relevant test files
- current test taxonomy from `docs/references/testing.md`
- latest quantitative report, if available

Avoid overloading the reviewer with unrelated repository history.

### Review Rubric

Score each reviewed test or test group on these dimensions:

- Contract focus: does the test verify externally observable behavior?
- Failure usefulness: would a failure point to a clear problem?
- Scenario coverage: are normal, failure, edge, and boundary cases represented?
- Assertion quality: are assertions specific and meaningful?
- Fixture clarity: are fixtures small, local, deterministic, and readable?
- Mock discipline: are mocks used only where they preserve the contract being
  tested?
- Refactor resilience: would the test survive internal refactoring that keeps
  behavior unchanged?
- Domain relevance: does the test protect behavior that matters to users?
- Maintainability: is the test easy for humans and agents to update safely?
- Duplication control: does repeated setup or assertion logic obscure intent?

### Finding Severity

Use these categories:

- blocker: the test gives false confidence, hides a real contract gap, or makes
  the suite unreliable
- important: the test covers useful behavior but is brittle, incomplete, or too
  implementation-coupled
- minor: readability, naming, structure, or local cleanup issue
- note: useful observation that does not require action

### LLM Review Output

The review should produce:

- reviewed files
- reviewed contracts
- findings by severity
- examples with file paths and line references
- suggested fixes
- tests that should remain unchanged
- open questions requiring human judgment

The reviewer should not change product scope. If the test review reveals a
missing product decision, record it as an open human decision.

## Test Portfolio Assessment

Assess whether the suite has the right mix of test levels:

- unit tests for isolated deterministic behavior
- integration tests for cross-module data and control flow
- structure tests for repository rules and architecture contracts
- smoke tests for quick installed-package or public API sanity checks
- explicit performance tests for runtime-sensitive paths
- explicit live tests for network-backed behavior

The goal is not to force every feature into every level. The goal is to match
test level to risk:

- pure calculations: mostly unit tests with edge cases
- public APIs: unit plus integration or smoke coverage
- backtest/research flows: integration and deterministic regression coverage
- packaging/release: smoke and build checks
- live or external behavior: explicit-only live checks

## Report Template

Use this template for an actual evaluation report.

```markdown
# Test Quality Evaluation Report

- Date:
- Evaluator:
- Commit:
- Scope:
- Compared baseline:

## Executive Summary

- Overall disposition:
- Main strengths:
- Main risks:
- Recommended next gate:

## Commands

| Command | Result | Runtime | Notes |
| --- | --- | ---: | --- |
| `uv run poe verify` |  |  |  |

## Quantitative Metrics

| Metric | Value | Threshold | Disposition |
| --- | ---: | ---: | --- |
| Total tests |  | n/a |  |
| Skipped tests |  |  |  |
| Xfail tests |  |  |  |
| Line coverage |  | 90% |  |
| Branch coverage |  | TBD |  |
| Full suite runtime |  | TBD |  |
| Slowest test runtime |  | TBD |  |
| Repeated-run failures |  | 0 |  |
| Mutation score |  | TBD |  |

## Test Portfolio

| Area | Test count | Main coverage | Gaps |
| --- | ---: | --- | --- |
| Unit |  |  |  |
| Integration |  |  |  |
| Structure |  |  |  |
| Smoke |  |  |  |
| Performance |  |  |  |

## Mutation Testing

- Tool:
- Target:
- Command:
- Runtime:
- Killed mutants:
- Survived mutants:
- Timeout mutants:
- Ignored/equivalent mutants:
- Mutation score:
- Key survived mutants:

## Flakiness

- Repeat strategy:
- Randomization strategy:
- Failures observed:
- Suspect tests:

## LLM Review

| Severity | Count |
| --- | ---: |
| Blocker |  |
| Important |  |
| Minor |  |
| Note |  |

### Findings

1. 

## Recommended Gate Changes

- Immediate:
- Next:
- Later:

## Open Human Decisions

1. 
```

## Recommended Adoption Path

Adopt the evaluation in stages.

### Stage 1: Baseline Report

Run the evaluation once without adding new hard gates. Capture current metrics,
LLM findings, and high-value test gaps.

Output:

- one test quality evaluation report
- no CI changes
- no new pass/fail threshold except existing repository gates

### Stage 2: Low-Risk Mechanical Gates

Add or strengthen gates that are cheap and objective:

- no new skipped tests without explanation
- no permanent non-strict flaky retries in the default lane
- coverage must not fall below the existing repository floor
- slow-test report must be visible in evaluation output

### Stage 3: Targeted Mutation Audits

Run mutation testing on selected high-value slices:

- public API behavior
- backtest/research contract paths
- bug-prone regressions
- recently changed modules

Do not make mutation score a full-repository hard gate until runtime cost and
false positives are understood.

### Stage 4: LLM Review Gate For Major Feature Work

For substantial feature work, require an LLM-assisted test review before final
acceptance. The review should focus on whether tests prove the product contract
from the relevant spec.

## Initial Gate Recommendations

For the next feature cycle, use these as recommendations rather than permanent
thresholds:

- default verification must pass
- repository coverage floor must hold
- no unexplained new skipped or xfailed tests
- no known flaky tests in the default lane
- LLM review must find zero blocker test-quality issues
- targeted mutation testing should be run only when it is cheap enough for the
  affected module or when the feature is high-risk

Human judgment is required before converting any advisory recommendation into a
hard gate.
