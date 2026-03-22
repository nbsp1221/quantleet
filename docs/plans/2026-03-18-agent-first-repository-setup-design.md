# Agent-First Repository Setup Design

## Goal

Set up `quantcraft` so it can be developed in an agent-first way without requiring the repository owner to continuously read and supervise raw code, while still keeping financial-domain risk under tight control.

This design is grounded in the OpenAI article "Harness engineering: leveraging Codex in an agent-first world" from 2026-02-11. The design only adopts principles stated in that article and maps them to this repository's current Python-library shape.

## Repository Context

Current repository state:

- Python 3.13 library managed with `uv`
- one package: `src/quantcraft`
- current implemented scope is small market-data access through `Exchange`
- local verification already exists:
  - `pytest`
  - `ruff`
  - `mypy`
  - `uv build`
- notebooks are already part of the repository
- there is no `AGENTS.md`
- `README.md` is empty
- `docs/` contains planning documents, but not a structured knowledge base
- the repository is local-first and not yet organized around remote PR workflows

## Design Principles

These principles come directly from the OpenAI article and are treated as requirements for this setup:

1. `AGENTS.md` is a short map, not a monolithic manual.
2. Repository-local docs are the system of record.
3. Agent legibility is the goal: if knowledge is not in the repo, it effectively does not exist.
4. Architecture and taste must be enforced mechanically, not only described in prose.
5. Plans are first-class artifacts and remain versioned in the repository.
6. High autonomy should not be assumed to generalize without similar investment in structure, tooling, and validation.
7. Drift must be managed continuously through quality tracking and cleanup.

## Product and Safety Constraints

`quantcraft` is expected to grow into a quant library and framework that eventually covers:

- crypto and stock data collection
- research utilities
- backtesting
- paper trading
- live trading
- quant-related ML tooling

Because this is financial software, autonomy is not uniform across the repository.

For the initial agent-first setup:

- `execution`, `risk`, and `portfolio` are high-scrutiny domains
- these domains must remain under strong human gate
- `market data`, research utilities, notebooks, and backtest infrastructure can be more agent-autonomous once repository checks are in place

This is intentionally more conservative than the OpenAI repository in the article because the article itself states that end-to-end autonomy should not be generalized without equivalent repository investment.

## Proposed Repository Knowledge System

The repository should move from "a few plans in `docs/`" to "a structured, indexed knowledge base".

Top-level documents:

- `AGENTS.md`
- `ARCHITECTURE.md`
- `README.md`

Structured knowledge under `docs/`:

- `docs/design-docs/`
- `docs/exec-plans/active/`
- `docs/exec-plans/completed/`
- `docs/product-specs/`
- `docs/references/`
- `docs/generated/`
- `docs/QUALITY_SCORE.md`
- `docs/RELIABILITY.md`
- `docs/SECURITY.md`
- `docs/PLANS.md`
- `docs/DESIGN.md`

### Role of Each Document

`AGENTS.md`

- around 100 lines, intentionally short
- entrypoint for agent work
- points to the real sources of truth
- defines standard commands and mandatory pre-merge checks
- states autonomy boundaries and "human gate" domains

`ARCHITECTURE.md`

- top-level map of repository domains
- layer model and allowed dependency directions
- explicit high-scrutiny domains
- guidance for future package extraction

`docs/design-docs/`

- long-lived design rationale
- golden principles
- core beliefs about agent-first development in this repository

`docs/exec-plans/`

- active and completed execution plans
- decision logs and progress notes live with the plan
- existing `docs/plans/` material should be migrated or indexed rather than left as an unstructured archive

`docs/product-specs/`

- product/domain specs for market data, backtesting, paper trading, live trading, ML tools
- each spec defines scope, non-goals, constraints, failure behavior, and verification expectations

`docs/references/`

- repository-local reference material that agents should use often
- examples: CCXT conventions, market symbol rules, exchange-specific caveats, local tooling references

`docs/generated/`

- generated artifacts such as package maps, schema summaries, or automated quality reports

`docs/QUALITY_SCORE.md`

- per-domain quality grades
- tracks where the repository is structurally weak

`docs/RELIABILITY.md`

- operational rules for reproducibility, test gates, smoke validation, and live-vs-sim boundaries

`docs/SECURITY.md`

- secrets handling
- credential policy
- live-trading safety requirements
- rules for any code that can move funds or create exposure

## Domain and Architecture Design

The repository should remain a single Python package for now, but it should be organized as if later extraction into subpackages is expected.

This means using a hybrid structure:

- keep `src/quantcraft/...`
- define domain boundaries now
- enforce import and layer rules now
- leave room for later package extraction without rewriting the architecture

### Initial Domain Map

The domain map should be documented even if many domains are not implemented yet.

Proposed top-level domains:

- `market_data`
- `research`
- `backtest`
- `paper`
- `execution`
- `risk`
- `portfolio`
- `ml`
- `common`

### Safety Classes

The setup should classify domains into safety tiers:

- Tier A: `execution`, `risk`, `portfolio`
- Tier B: `market_data`, `paper`, `backtest`
- Tier C: `research`, `ml`, notebooks, generated docs

Tier A rules are stricter:

- stronger review requirements
- stronger structural checks
- stronger documentation requirements
- mandatory scenario and invariant coverage

### Layering Model

Following the article's emphasis on strict boundaries and predictable structure, each implemented domain should eventually follow a fixed internal layering model. For this Python repository, the initial model should be:

- `types`
- `config`
- `adapters`
- `services`
- `runtime`
- `interfaces`

Cross-cutting support enters through explicit shared modules only:

- `common`
- `telemetry`
- `validation`

Allowed dependencies should move forward only. Backward or lateral dependencies should be forbidden unless explicitly allowed in the architecture document.

## Mechanical Enforcement

The setup should not stop at prose. It needs local checks that agents can run and must satisfy.

### Required Standard Commands

The repository should expose a stable set of commands that agents use instead of inventing ad-hoc command sequences:

- `repo-check`
- `test`
- `lint`
- `typecheck`
- `build`
- `notebook-validate`
- `live-smoke`

These can be implemented through `scripts/` or another local command wrapper, but the important design requirement is one stable interface.

### Required Mechanical Checks

1. Repository structure checks

- required docs exist
- required directories exist
- required indexes and cross-links exist

2. Plan/document checks

- execution plans have status and verification sections
- design docs are discoverable from indexes
- stale placeholder docs are rejected

3. Structural architecture checks

- forbidden domain imports fail
- safety-tier boundaries fail if crossed
- new Tier A modules require corresponding spec and reliability references

4. Taste and reliability checks

- structured logging conventions
- naming conventions for types and schemas
- file size limits or module complexity limits
- boundary validation requirements where external shapes enter the system

These checks should be introduced conservatively at first. The goal is not to overfit the repository to imagined future complexity, but to encode the invariants that will matter most once agent throughput increases.

## Local-First Operating Model

Because the repository is local-first and solo-maintained, the operating loop should mirror the article's agent workflow without depending on remote PR infrastructure.

Local loop:

1. human writes or approves a plan/spec
2. agent implements against the plan
3. agent runs standard checks locally
4. agent performs self-review against architecture and safety documents
5. agent updates docs if behavior or policy changed
6. agent reports verification results and remaining risk
7. human only needs to intervene when work touches Tier A domains or when checks fail in ways that require judgment

This preserves the article's "humans steer, agents execute" model while adapting it to a local-first repository.

## Quality Tracking and Cleanup

The repository should adopt the article's "garbage collection" idea in a lightweight local form.

That means:

- keeping `docs/QUALITY_SCORE.md`
- tracking quality by domain and by infrastructure layer
- maintaining a `tech-debt-tracker`
- adding recurring local cleanup tasks that scan for:
  - stale docs
  - placeholder text
  - architecture violations
  - duplicated helper patterns
  - missing plan/spec links

At this stage, cleanup can remain manual-triggered rather than scheduled. The important part is that drift management becomes an explicit repository function, not an occasional intuition.

## Rollout Strategy

The first rollout should be staged.

Stage 1: Knowledge system

- add `AGENTS.md`
- add `ARCHITECTURE.md`
- populate top-level quality, reliability, and security docs
- create structured `docs/` layout
- write indexes and migration notes for current planning docs

Stage 2: Standard operating surface

- add standard local command entrypoints
- document local agent workflow
- add document and structure checks

Stage 3: Mechanical architecture enforcement

- add structural tests
- add safety-tier boundary checks
- add plan/document validation

Stage 4: Cleanup and quality operations

- add quality score updates
- add debt tracker
- add recurring cleanup workflow documentation

## Non-Goals

This setup does not attempt to:

- automate remote PR review infrastructure
- build browser-based QA tooling
- introduce production observability stacks
- make live trading fully autonomous
- finalize every future domain implementation detail now

The purpose of this batch is repository harnessing, not product feature expansion.

## Success Criteria

This design is successful when:

- the repository has a short, working `AGENTS.md`
- repository knowledge is structured and indexed
- architecture boundaries are documented and mechanically testable
- agents have one standard set of local commands
- high-scrutiny financial domains are explicitly gated
- quality, reliability, and security rules are visible in-repo
- drift management becomes an explicit recurring repository concern

## Recommended Decision

Adopt the "document + mechanical guardrails" approach as the first implementation batch.

This is the smallest setup that still matches the actual lessons from the OpenAI article:

- system-of-record docs
- short `AGENTS.md`
- strict and legible boundaries
- mechanical enforcement
- plans as first-class artifacts
- explicit drift control

It avoids the two main failure modes:

- doing too little and leaving quality up to ad-hoc prompting
- doing too much and building a heavyweight automation system before the repository has earned it
