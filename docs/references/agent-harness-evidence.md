# Agent Harness Evidence

This note records the evidence gathered on 2026-04-04 while re-evaluating `quantcraft`'s test and harness strategy against:

- OpenAI's harness-engineering reference already checked into this repo
- Anthropic's harness-design article
- maintained open-source projects with strong testing and contributor workflows

It exists so the reasoning behind current harness judgments does not depend on chat history.

## Primary Questions

The investigation focused on four questions:

1. Are exact-value tests inherently low-value or fake rigor?
2. Are `quantcraft`'s current tests meaningfully protecting behavior?
3. Is the current command and harness surface abnormally large?
4. Is the repository improving through meaningful stabilization, or mostly accreting more surface area?

## Local Protocol References

- [openai-harness-engineering.md](openai-harness-engineering.md)
- Anthropic article: `https://www.anthropic.com/engineering/harness-design-long-running-apps`

Key points taken from the OpenAI reference:

- engineering work shifts toward scaffolding, systems, and leverage rather than hand-writing code
- repository-local docs become the system of record and should be mechanically enforced
- agents benefit from strict architecture and predictable structure
- tests, tooling, docs, and internal utilities are all part of the agent operating environment
- full agent autonomy creates drift, so repositories need recurring cleanup and "golden principles"

Key points taken from the Anthropic article:

- evaluator work should be separate from generation
- criteria should be concrete and gradable
- important checks should validate what a real user journey experiences
- explicit "done" contracts improve reliability
- hard thresholds are useful when tied to specific protected behaviors

## Confirmed Findings

### 1. Exact-value tests are not inherently bad practice

This claim does **not** hold up.

Maintained open-source projects regularly use exact-value assertions, snapshots, and golden-style tests when the protected contract is deterministic.

Confirmed examples:

- `pytest`
  - exact CLI-output checks in `testing/test_helpconfig.py`
  - exact stdout line checks in `testing/test_pytester.py`
- `pydantic`
  - exact `ValidationError.errors()` payload checks in `tests/test_aliases.py`
- `ruff`
  - contributor workflow explicitly includes snapshot review via `cargo insta review`
  - snapshot assertions in `crates/ruff_python_importer/src/insertion.rs`
- `backtesting.py`
  - exact order and trade-state assertions in `backtesting/test/_test.py`
- `vectorbt`
  - exact `DataFrame` and `Series` equality assertions in `tests/test_data.py`

Conclusion:

- exact expected values are normal when they encode a deterministic contract
- they become weak only when the asserted value is arbitrary, implementation-shaped, or disconnected from user-visible behavior

## `quantcraft` Test Assessment

### 2. Some current tests are clearly meaningful

Important examples:

- [tests/integration/research/test_backtest_runner.py](../../tests/integration/research/test_backtest_runner.py)
  - exact `BacktestResult`, `trade_log`, `equity_curve`, and `summary` checks
  - these protect the public backtest contract, not just internal implementation details
- [tests/unit/trading/test_matching_and_state.py](../../tests/unit/trading/test_matching_and_state.py)
  - exact buy/sell fill prices, fee calculation, slippage behavior, and state transitions
  - these are deterministic domain rules for the current long-only backtest scope

These are meaningful because:

- the runtime is intentionally deterministic
- the expected outputs are domain contracts
- regressions in matching, fee, fill, or accounting semantics would be caught immediately

### 3. Some earlier tests really were too weak

This concern was valid.

Examples identified in the repo:

- source-tree import smoke relied on [tests/conftest.py](../../tests/conftest.py) placing the repo root on `sys.path`
- the old `sell`-surface check validated API shape more than actual long-only exit semantics
- a few harness tests were checking source text where logic checks were stronger and available

This is why the stabilization work added:

- artifact-backed import validation in [tests/integration/commands/test_built_artifact_imports.py](../../tests/integration/commands/test_built_artifact_imports.py)
- a behavioral long-only `sell` test in [tests/unit/research/application/test_strategy_surface.py](../../tests/unit/research/application/test_strategy_surface.py)
- logic-first harness tests such as [tests/structure/repo/test_coverage_harness.py](../../tests/structure/repo/test_coverage_harness.py)

Conclusion:

- the repo did have a few weak proxy tests
- that did **not** imply that the whole suite was fake
- the right fix was targeted replacement of weak proxies, not rejection of deterministic assertions as a category

### 4. Artifact-backed validation was a real missing user-journey check

This finding remains valid under both local protocol docs and external comparison.

Why:

- [tests/smoke/local/test_public_imports.py](../../tests/smoke/local/test_public_imports.py) exercises a fast local import path
- [tests/conftest.py](../../tests/conftest.py) makes source-tree imports easier by design
- that is useful for local DX, but it is not equivalent to clean-install artifact validation

The added built-wheel import test is therefore evidence-oriented rather than ceremonial.

## Command Surface Assessment

### 5. A larger command surface is normal in maintained projects

`quantcraft` currently defines 17 `poe` tasks in [pyproject.toml](../../pyproject.toml).

That is not unusual when compared with other active repositories:

- `pydantic` Makefile currently defines 29 `.PHONY` targets
- `pytest` `tox.ini` exposes 14 major env entries before variant expansion
- `ruff` contributor documentation lists many distinct validation and snapshot commands

Conclusion:

- multiple explicit commands for lint, typecheck, tests, perf, docs, notebooks, or packaging are normal
- "too many commands" is not supported by the external evidence by itself

### 6. `quantcraft` does have notable command-doc duplication

This concern is partially valid.

The same `uv run poe ...` entries are repeated across:

- [AGENTS.md](../../AGENTS.md)
- [README.md](../../README.md)
- [docs/RELIABILITY.md](../RELIABILITY.md)
- [docs/references/tooling.md](tooling.md)
- [docs/references/developer-tasks.md](developer-tasks.md)

This increases discoverability for agents, but it also raises drift cost.

Evidence from the OpenAI article suggests the ideal pattern is:

- a short map document
- deeper system-of-record docs behind it
- mechanical checks that keep those records aligned

So the current pattern is not clearly wrong, but it is more duplicated than the OpenAI article's preferred shape.

## Repository Direction Assessment

### 7. The user's sense that the repo is mostly adding, not simplifying, is evidence-backed

Recent local history supports this concern.

Across the most recent 8 commits inspected locally:

- insertions: `18,364`
- deletions: `1,035`

Recent commit subjects are also predominantly `Add ...` style changes.

This does not prove the added work was wrong.
It does show that:

- expansion is dominating subtraction
- stabilization through cleanup/refactoring is not yet occurring at the same rate

This matters because the OpenAI reference explicitly describes drift and recommends recurring cleanup, golden-principle enforcement, and targeted refactoring pull requests.

Conclusion:

- the repo is following agent-first scaffolding patterns
- but it is weaker on ongoing garbage-collection and simplification cadence than the OpenAI article describes

## Bottom Line

The strongest evidence-supported synthesis is:

- `quantcraft` is **not** using a fake testing style simply because many tests have exact expected values
- parts of the suite are meaningful and protect deterministic public contracts
- some weak proxy tests did exist and were valid targets for replacement
- the repository's command surface is not abnormal by comparison with maintained OSS projects
- the user's concern about accretion over simplification is real and supported by local history
- relative to the OpenAI and Anthropic references, the repository is stronger on scaffolding and explicit checks than on continuous cleanup and surface-area reduction

## External Evidence Used

### OpenAI / Anthropic

- local reference: [openai-harness-engineering.md](openai-harness-engineering.md)
- Anthropic article: `https://www.anthropic.com/engineering/harness-design-long-running-apps`

### Maintained OSS repos inspected locally on 2026-04-04

- `pytest` at commit `f93656d611f3c9cd22f346dfeda52cddb778c589`
  - `https://github.com/pytest-dev/pytest/blob/f93656d611f3c9cd22f346dfeda52cddb778c589/testing/test_helpconfig.py`
  - `https://github.com/pytest-dev/pytest/blob/f93656d611f3c9cd22f346dfeda52cddb778c589/testing/test_pytester.py`
  - `https://github.com/pytest-dev/pytest/blob/f93656d611f3c9cd22f346dfeda52cddb778c589/tox.ini`
  - `https://docs.pytest.org/en/stable/explanation/goodpractices.html`
- `pydantic` at commit `46dea928844edfdbee5ca1f36cbc3b042e2a8abd`
  - `https://github.com/pydantic/pydantic/blob/46dea928844edfdbee5ca1f36cbc3b042e2a8abd/tests/test_aliases.py`
  - `https://github.com/pydantic/pydantic/blob/46dea928844edfdbee5ca1f36cbc3b042e2a8abd/Makefile`
- `ruff` at commit `af9ae49e84daf09f74e654ba3e6d87fe94f6d1ca`
  - `https://github.com/astral-sh/ruff/blob/af9ae49e84daf09f74e654ba3e6d87fe94f6d1ca/CONTRIBUTING.md`
  - `https://github.com/astral-sh/ruff/blob/af9ae49e84daf09f74e654ba3e6d87fe94f6d1ca/crates/ruff_python_importer/src/insertion.rs`
- `backtesting.py` at commit `6e9016c7b30d985137cde3fe24e1d39785c5e3a7`
  - `https://github.com/kernc/backtesting.py/blob/6e9016c7b30d985137cde3fe24e1d39785c5e3a7/backtesting/test/_test.py`
- `vectorbt` at commit `993ceca7116fc8e55f4cd3a36fe43d83dab62b27`
  - `https://github.com/polakowo/vectorbt/blob/993ceca7116fc8e55f4cd3a36fe43d83dab62b27/tests/test_data.py`
