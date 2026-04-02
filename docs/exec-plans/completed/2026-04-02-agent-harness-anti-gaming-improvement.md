# Agent Harness Anti-Gaming Improvement Plan

> **For Codex:** REQUIRED SUB-SKILLS: read `docs/plans/2026-04-02-agent-harness-anti-gaming-design.md` before implementation, then use `subagent-driven-development` or `executing-plans` for any future execution batch.

**Goal:** Improve the `quantcraft` harness so AI agents are guided toward the real product goal of a public, usable quant/backtesting library, while reducing the risk of proxy-metric gaming, fake rigor, and issue-shaped local optimization.

**Architecture:** This batch should strengthen the harness control plane rather than expand product scope. The implementation should separate mechanical checks, LLM-assisted critique, and human judgment explicitly, and should only promote new enforcement where the protected behavior is objective, high-signal, and worth the complexity.

**Tech Stack:** Python 3.13, `uv`, repo-local `poe` harness, markdown system-of-record docs, structure/repo tests

## Lifecycle

- status: completed
- completed_on: 2026-04-02

## Current Status

- Slice 1: complete
- Slice 2: complete
- Slice 3: complete
- Slice 4: complete
- Slice 5: complete

## Why This Batch Exists

The repository already does many agent-first things correctly:

- short map-style `AGENTS.md`
- strong spec and design-doc indexes
- repo-local verification commands
- architecture/repo/doc drift checks

What is still weak is the policy layer for evaluation itself.

Today the repository is much better at answering:

- "is this contract preserved?"

than:

- "are we teaching agents to pursue the right goal?"

Without an explicit anti-gaming policy, future agents may add:

- low-value scores
- tests that only restate the current implementation
- benchmarks detached from canonical workflows
- evaluator loops that look rigorous but do not improve decisions

## Required Reading Before Any Task

Every worker and reviewer must read:

- `AGENTS.md`
- `ARCHITECTURE.md`
- `docs/design-docs/architecture-governance.md`
- `docs/references/openai-harness-engineering.md`
- `docs/plans/2026-04-02-agent-harness-anti-gaming-design.md`
- `docs/product-specs/index.md`
- `docs/QUALITY_SCORE.md`

Recommended external reference:

- `https://www.anthropic.com/engineering/harness-design-long-running-apps`

## Non-Negotiable Guardrails

- Do not introduce a composite "user value score" as a merge gate.
- Do not claim that subjective product value is fully mechanizable.
- Do not add evaluator agents that grade their own success with ungrounded scalar scores.
- Do not add synthetic benchmarks unless they represent a canonical library workflow.
- Do not expand product scope while doing harness-policy work.
- Do not turn `docs/QUALITY_SCORE.md` into a product-direction or DX scoreboard.

## Success Conditions

This batch is complete only when all of the following are true:

1. repository docs explicitly distinguish:
   - mechanical checks
   - LLM-assisted critique
   - human judgment
2. any newly proposed metric or check documents:
   - the real behavior being protected
   - the measured proxy
   - how it could be gamed
   - why the proxy is still acceptable
3. the repository defines a promotion ladder:
   - critique
   - documented policy
   - repeated manual use
   - narrow enforcement
4. the repository names a small set of canonical user journeys for library consumption
5. future evaluator work is framed as critique or adversarial review rather than fake objective scoring
6. structure/repo/docs checks cover only the objective parts of the new policy
7. the initial canonical user journeys are frozen in-repo before future automation work chooses proxies opportunistically
8. the repository defines how new tests and new checks justify themselves against contract protection rather than coverage theater
9. any newly promoted check includes a revalidation/removal rule so stale proxies do not accumulate indefinitely
10. `docs/QUALITY_SCORE.md` explicitly remains a coarse repository-health artifact rather than a value meter

## Explicit Non-Goals

This batch does not:

- build a full autonomous evaluator swarm
- replace human product judgment
- add broad UX scoring
- guarantee that all future agents will never game a metric
- lock every future harness choice into hard-coded checks

## Slice Plan

### Slice 1: Define Canonical Library User Journeys

**Intent:** Name a small set of real consumer workflows so every later evaluator, benchmark, and policy change is anchored to actual library use rather than arbitrary synthetic paths.

**Likely files:**

- `README.md`
- `docs/references/research-ergonomics-quickstart.md`
- `docs/product-specs/research-ergonomics.md`
- notebook/docs/structure tests as needed

**Freeze these first journeys at the start of the slice:**

- clean install to public imports
- dataframe-like quickstart to first backtest
- materialized `BarSeries` to `engine.run(bars=...)`
- exchange-backed historical research flow to `engine.run(source=...)`

**Required outcome:**

- for each journey, the repository records:
  - starting state
  - user intent
  - success artifact
  - superficially passing but still bad outcome

Do not let a future agent choose easier surrogate journeys after the slice begins.

### Slice 2: Encode The Evaluation Taxonomy

**Intent:** Make the repository explicit about which questions belong to mechanical enforcement, which belong to LLM critique, and which remain human-gated.

**Likely files:**

- `docs/design-docs/architecture-governance.md`
- `docs/RELIABILITY.md`
- `docs/QUALITY_SCORE.md`
- relevant docs tests under `tests/structure/docs/`

**Required outcome:**

- the taxonomy is tied to concrete failure modes, not just abstract labels
- the docs explain what decision each class of evaluation is supposed to inform
- `docs/QUALITY_SCORE.md` is explicitly scoped as coarse repository health rather than product value
- the docs define the promotion ladder from critique to enforcement so agents do not mechanize first-draft judgments prematurely

### Slice 3: Add Metric Admission Rules

**Intent:** Require future harness metrics to justify their value and describe their gaming risk before they become repository policy.

**Likely files:**

- `docs/design-docs/architecture-governance.md`
- `docs/design-docs/doc-gardening.md`
- `docs/feedback-promotion-log.md`
- relevant repo/docs tests

**Required outcome:**

- every proposed metric/check must document:
  - protected behavior
  - measured proxy
  - gaming vector
  - decision changed
  - revalidation or removal condition
- proposals that cannot answer those fields stay in docs/review prompts rather than becoming checks

### Slice 4: Add LLM-Critique Guidance Without Fake Objectivity

**Intent:** Introduce repository guidance for evaluator-style agent critique that produces evidence-bearing review comments instead of scalar quality theater.

**Likely files:**

- `AGENTS.md`
- `docs/design-docs/core-beliefs.md`
- `docs/design-docs/golden-principles.md`
- docs tests as needed

**Required outcome:**

- evaluator prompts and docs forbid:
  - scalar approval scores
  - generic approval language
  - critique without a concrete failure mode
- evaluator outputs must be findings-first and adversarial
- evaluator outputs must not act as merge gates on their own

### Slice 5: Promote Only The Objective Residue Into Checks

**Intent:** After the policy is clear, add or refine only the narrow mechanical checks that protect objective high-signal boundaries.

**Likely files:**

- `src/quantcraft/_repo_tools.py`
- `scripts/repo_check.py`
- `tests/structure/repo/`

**Required outcome:**

- only objective, high-signal residue becomes a check
- no check is added solely to raise coverage, count more tests, or create a new aggregate score
- newly added checks prove they protect contracts or frozen user journeys rather than current implementation details

**Good check candidates:**

- canonical doc/index metadata presence
- public import/install smoke for named user journeys
- executable quickstart/example paths tied to frozen workflows
- labeling of explicit-only versus default-lane external workflows

**Must stay non-mechanical:**

- whether the chosen journeys are the right product bet
- whether docs feel persuasive or elegant
- whether an evaluator critique is strategically compelling
- whether a benchmark target is meaningful enough to matter

## Review Protocol

For each future slice:

1. implementation agent proposes the protected behavior and the proxy
2. implementation agent states which canonical user journey is being protected
3. evaluator/reviewer agent attacks the proposal for gaming risk and false confidence
4. human decides whether the rule is worth institutionalizing
5. only then is the objective residue promoted into checks

Reviewers must not act as approvers.
They exist to surface failure modes, gaming vectors, and open tradeoffs.
Their output is critique input for humans and planners, not a final verdict.

## Verification Gates

At the end of each future slice, run the narrowest relevant checks first, then at least:

- `uv run ruff check .`
- `uv run mypy src`
- `uv run python scripts/repo_check.py`

At batch completion, run:

- `uv run pytest tests/structure -q`
- `uv run poe verify`

## Human-Gate Conditions

Stop and ask the human if any of the following occurs:

- a proposed harness rule changes the library's public product direction
- a metric seems easy to pass while still obviously missing the real goal
- a proposed evaluator looks authoritative but cannot explain its evidence
- a new benchmark is not tied to a canonical user journey
