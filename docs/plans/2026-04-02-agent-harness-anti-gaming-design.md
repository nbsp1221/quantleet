# Agent Harness Anti-Gaming Design

## Status

- Status: `approved baseline`
- Class: `design`
- Scope: next harness-review slice for agent-led development quality and anti-gaming controls

Related documents:

- [../../ARCHITECTURE.md](../../ARCHITECTURE.md)
- [../design-docs/architecture-governance.md](../design-docs/architecture-governance.md)
- [../design-docs/core-beliefs.md](../design-docs/core-beliefs.md)
- [../design-docs/golden-principles.md](../design-docs/golden-principles.md)
- [../product-specs/index.md](../product-specs/index.md)
- [../references/openai-harness-engineering.md](../references/openai-harness-engineering.md)
- [Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps)

## Goal

Review the current `quantcraft` harness with one explicit concern in mind:

- how to help AI agents solve the real product problem
- without rewarding proxy-metric gaming, empty checks, or locally optimized but strategically wrong changes

The immediate outcome of this slice is not a new feature. It is a clearer design for what this repository should evaluate mechanically, what it should evaluate with LLM assistance, and what must stay human-judged.

## Why This Slice Exists

The repository already has a strong agent-first control plane:

- short `AGENTS.md` map
- canonical architecture/spec indexes
- repo-local harness commands
- structure tests, repo checks, notebook validation, and coverage rules

Those are real strengths.

However, agent-first repositories still fail in a predictable way:

- the agent sees a measurable target
- the measurable target becomes the local objective
- the local objective diverges from the real product goal
- the agent then "wins" the metric while losing the actual user value

For `quantcraft`, this risk is especially important because the long-term goal is not merely "pass tests." It is to ship a public `pip` library that humans and AI agents can easily discover, understand, trust, and use for quant research and backtesting.

That means the harness must not accidentally teach agents that:

- a new score is equivalent to user value
- a new test is useful just because it is executable
- a new benchmark matters just because it is faster
- a change is good just because it closes the issue-shaped hole in the current prompt

## The Core Failure Mode

This slice treats the main failure mode as:

- solving the prompt-shaped problem instead of the product-shaped problem

Common examples:

- adding a synthetic metric that moves but does not correspond to real library usability
- adding trivial tests that only pin the implementation the agent already wrote
- introducing "quality scores" that feel rigorous but do not change decisions
- optimizing one benchmark path while damaging the canonical workflow

This is a Goodhart-style failure:

- once a proxy becomes the target, it stops being a trustworthy proxy

The harness should therefore prefer:

- cheap, objective checks for objective invariants
- skeptical critique for ambiguous quality questions
- explicit human judgment where value is real but not mechanically provable

## Canonical User Journeys Must Come First

The most important anti-gaming guardrail is not a clever evaluator.
It is a small, explicit set of workflows that the library actually exists to serve.

For `quantcraft`, future harness work should anchor itself to a few canonical journeys before inventing new metrics or benchmarks:

1. clean install -> canonical public imports -> smallest documented backtest
2. dataframe-backed quickstart -> `DataFrameDataSource` -> `BacktestEngine.run(source=...)`
3. materialized dataset flow -> `BarSeries` -> `BacktestEngine.run(bars=...)`
4. exchange-backed historical flow -> `CCXTDataSource` -> `source.load()` -> `engine.run(source=...)`

Why this ordering matters:

- if the harness starts from metrics first, the metrics become the product
- if the harness starts from workflows first, metrics stay subordinate to actual use

So future evaluation work should ask:

- which canonical journey is this protecting?

before it asks:

- how do we measure it?

## What The OpenAI And Anthropic References Help With

### OpenAI Harness Reference

`openai-harness-engineering.md` gives several strong lessons that are directly useful here:

- keep repository knowledge as the system of record
- enforce high-signal invariants mechanically
- do not overload `AGENTS.md`
- promote repeated drift into docs or checks
- optimize for agent legibility, not just human taste

Important nuance:

- it does not argue that everything should become a metric
- it argues for encoding important boundaries and making the environment legible

That matters because anti-gaming starts with choosing the right boundary, not with inventing more dashboards.

### Anthropic Harness Reference

The Anthropic article adds complementary lessons:

- separate planning, generation, and evaluation roles
- use structured artifacts between long-running phases
- make evaluators skeptical and independent from generators
- negotiate a sprint contract before implementation

Important nuance:

- evaluator separation improves judgment quality
- it does not magically make subjective value fully measurable

So the lesson is not "replace humans with evaluator agents."
The lesson is "use evaluator agents to surface critique, failure cases, and blind spots that a generator will not reliably catch on its own."

## Human-Closed Design Decisions

These items are explicitly decided for the next harness-improvement slice and should not be re-opened casually by implementation agents.

### 1. No Single "User Value Score"

The repository should not introduce one composite scalar such as:

- "library usability score"
- "agent quality score"
- "developer experience score"

for gating decisions.

Why:

- those scores look rigorous while hiding subjective weighting decisions
- they are easy to game
- they create false confidence

### 2. Evaluation Must Be Split By Judgment Type

The harness should separate three kinds of evaluation:

1. mechanical pass/fail checks
2. LLM-assisted critique
3. human judgment

These are not interchangeable.

### 3. Mechanical Checks Must Defend Invariants, Not Simulate Taste

Mechanical checks are appropriate when the rule is:

- objective
- cheap to evaluate
- clearly tied to repository drift or correctness risk

Examples that fit:

- import surface contracts
- doc/index presence and metadata
- quickstart snippet execution
- wheel build/install verification
- reproducible benchmark regression checks

Examples that do not fit well:

- "is this API elegant?"
- "is this public abstraction the right long-term one?"
- "does this library feel easy to learn?"

### 4. LLM Evaluators Are Critics, Not Oracles

LLM-based evaluators are useful for:

- finding mismatch between docs and likely user interpretation
- spotting suspicious complexity
- challenging whether a change addresses the stated goal
- proposing adversarial scenarios that current checks miss

LLM-based evaluators are not sufficient for:

- proving user value
- deciding long-term product direction alone
- justifying a new metric by themselves

### 5. Every New Metric Or Check Must Carry A "Gaming Note"

Any future harness rule should document:

1. the real behavior it is trying to protect
2. the proxy being measured
3. how an agent could make the proxy pass while missing the goal
4. why the repository still accepts that proxy

If that note cannot be written clearly, the metric is probably not ready.

Additionally, every proposed check should document:

5. which repository decision the check is expected to change
6. when the rule should be revalidated or removed if it stops carrying its weight

If a check does not change decisions, it is process theater.

### 6. `QUALITY_SCORE.md` Must Stay A Coarse Repository Artifact

`docs/QUALITY_SCORE.md` is still useful, but only as a conservative repository-health snapshot.

It must not become:

- a user-value score
- a DX score
- a merge-time judge of whether a slice was "valuable enough"

Otherwise it collapses into the exact fake rigor this design is trying to prevent.

### 7. Tests Must Defend Contracts, Not Merely Freeze Implementations

The repository should treat new tests skeptically when their main effect is:

- making the suite greener
- increasing coverage numerically
- pinning the exact implementation the agent just wrote

Acceptable reasons to add a new test:

- it protects a public contract
- it protects a canonical user journey
- it captures a previously observed regression
- it protects an architectural or repository boundary

If a new test cannot be justified by one of those four reasons, it is likely test theater.

## Recommended Evaluation Taxonomy

### Mechanical Layer

Use pass/fail automation for:

- packaging and installation
- public import surface
- canonical example execution
- doc/spec/index consistency
- deterministic correctness contracts
- performance regressions on clearly defined canonical paths

Rule:

- these checks should answer "did we preserve the declared contract?"
- they should not pretend to answer "did we maximize value?"

### LLM-Assisted Layer

Use LLM evaluators for:

- critique of whether the change solves the stated user problem
- critique of public API surprise and conceptual complexity
- adversarial reading of docs and examples from a fresh-agent perspective
- questioning suspicious metrics or suspiciously convenient success claims

Rule:

- evaluator output should be evidence-bearing critique, not a final scalar score
- evaluator output should name a concrete failure mode or confusion path, not generic style commentary
- evaluator prompts should forbid "overall approval" language

### Human Layer

Reserve human judgment for:

- whether a proposed metric is worth institutionalizing
- whether a public abstraction matches the long-term product direction
- whether a benchmark target represents meaningful speed for the real workflow
- when two plausible designs require product taste rather than bug-fix reasoning

Rule:

- if a decision changes the product's north star, public surface, or evaluation philosophy, it is not fully delegable

## What This Means For `quantcraft`

The library's actual north star is:

- a human or AI agent should be able to move from fresh install to a trustworthy first backtest with minimal confusion

That north star suggests a more grounded harness shape than a fake "usability score."

Good candidate artifacts:

- canonical user journeys
- executable quickstarts
- package-install verification
- benchmark paths tied to actual research workflows
- adversarial LLM critique of whether docs/examples would mislead a fresh user or fresh agent

Bad candidate artifacts:

- generic satisfaction scores
- arbitrary complexity points
- cosmetic metrics with no decision impact
- tests that only restate the implementation instead of protecting the contract

## Metric Admission Test

Before a new metric, benchmark, or repository check enters the harness, it should answer all of the following:

1. Which canonical user journey does it protect?
2. What concrete bad outcome would slip through if the metric did not exist?
3. How could an agent make the metric pass while still missing the real goal?
4. Why is this still the cheapest acceptable proxy?
5. Should this artifact stay:
   - mechanical
   - LLM-critique only
   - human-judged only

If those answers are weak, the repository should reject the metric rather than institutionalize a bad target.

## Initial Canonical User Journeys

The next harness batch should not leave the first user journeys for a future agent to choose ad hoc.

Freeze the initial set now:

### Journey A: Clean Install To Public Imports

- start: a fresh environment with the built package artifact
- intent: confirm the package installs cleanly and exposes the documented public import surface
- success artifact: importing `BacktestEngine`, `Strategy`, `ta`, `qc`, `BarSeries`, `TimeBar`, and the documented data sources works exactly as the docs imply
- superficially passing but still bad: the package builds, but the documented imports or import paths drift

### Journey B: DataFrame Quickstart To First Backtest

- start: the canonical quickstart path using dataframe-like input data
- intent: reach a first successful backtest with minimal setup
- success artifact: the documented quickstart flow runs and produces a `BacktestResult`
- superficially passing but still bad: a custom hidden setup or undocumented contract is needed to make the example work

### Journey C: Materialized Bars To Engine Run

- start: user-created `TimeBar` / `BarSeries`
- intent: run the engine from explicitly materialized historical bars
- success artifact: `BacktestEngine.run(bars=..., strategy=...)` works with the documented canonical types
- superficially passing but still bad: example code works only because the agent silently relied on lower-layer internals or undocumented metadata assumptions

### Journey D: Exchange-Backed Historical Research Flow

- start: the documented `CCXTDataSource` historical path
- intent: load historical bars and run a real research workflow through `engine.run(source=...)`
- success artifact: the documented flow remains coherent and reproducible enough for humans and agents to follow
- superficially passing but still bad: the path remains "documented" but becomes too flaky, too hidden, or too environment-dependent to serve as a trustworthy reference workflow

Not every journey should become a strict merge gate.
The point is to anchor future checks, benchmarks, docs, and critiques to real library use instead of arbitrary synthetic tasks.

## Evaluator Output Contract

Future LLM reviewers should not be allowed to emit generic approval language.

Preferred output shape:

1. important issue
2. why it matters
3. how the current proposal could be gamed or misread
4. concrete change to the plan
5. whether the issue should remain human-gated

This keeps evaluator output critical and evidence-bearing instead of score-shaped.

## Non-Goals

This slice does not:

- declare that subjective value can be fully mechanized
- remove humans from high-level product judgment
- require evaluator agents to become merge gates for every change
- justify adding broad automated DX scoring

## Success Criteria

This design is successful if the next harness-improvement batch preserves the following:

1. the repository clearly separates mechanical checks, LLM critique, and human judgment
2. new metrics require an explicit anti-gaming rationale
3. no composite "user value" score is introduced as a merge gate
4. future benchmark or DX work is tied to canonical user journeys rather than synthetic targets
5. agents are rewarded for preserving real contracts, not for inventing locally convenient proxies

## Design Summary

The right next move is not "measure everything."

The right next move is to make the harness more honest about what each evaluator can and cannot know:

- mechanical checks protect contracts
- LLM evaluators provide skeptical critique
- humans own the scarce judgment about value and direction

That split is the anti-gaming core.
