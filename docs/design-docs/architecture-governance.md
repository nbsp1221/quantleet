# Architecture Governance

## Status

- Status: `approved`
- Scope: document roles, promotion rules, and the boundary between mechanical enforcement and prompt guidance
- Basis: [../references/openai-harness-engineering.md](../references/openai-harness-engineering.md)

This document defines the approved governance model for the repository's agent-first harness.

## Why This Document Exists

`quantcraft` is being built in an agent-first workflow.

That means:

- humans define boundaries, standards, and scarce judgment calls
- agents implement within those constraints
- repeated failure modes are promoted from prose into checks

The OpenAI harness pattern is not “mechanize everything immediately.” It is to encode the important boundaries and invariants early, then promote repeated drift into mechanical enforcement.

## Document Roles

The repository uses these governing documents for this area:

1. [quantcraft-architecture.md](quantcraft-architecture.md)
   - approved top-level architecture
2. [package-topology-and-naming.md](package-topology-and-naming.md)
   - approved package topology, naming, and public-facade rules
3. [trading-kernel-contract-draft-ko.md](trading-kernel-contract-draft-ko.md)
   - future-only long-lived trading-kernel contract draft
4. [architecture-governance.md](architecture-governance.md)
   - approved governance and promotion policy
5. [../product-specs/backtest-mvp.md](../product-specs/backtest-mvp.md)
   - canonical current implemented-scope backtest baseline
6. [../product-specs/research-ergonomics.md](../product-specs/research-ergonomics.md)
   - canonical current implemented-scope research usability surface

This split prevents agents from conflating:

- structural architecture
- package topology and naming
- trading semantics
- harness policy
- current implemented scope
- approved expansion scope

The draft trading-kernel document must not override the current implemented-scope product specs. Agents should read it only when planning future shared trading semantics beyond the shipped baseline.

## What We Enforce Mechanically Now

At this stage, only rules that are objective, cheap to check, and likely to create repository drift are enforced mechanically.

Current enforced or intended-to-enforce-now rules include:

- long-lived architecture and contract documents live under `docs/design-docs/`
- `ARCHITECTURE.md` and the design-doc index point to the approved architecture documents
- flat `tests/test_*.py` files are disallowed
- the repo-local harness remains `scripts/ + poe`
- live tests stay out of the default lane
- context dependency rules should be promoted into structure tests as packages materialize

## Evaluation Taxonomy

The repository uses three distinct evaluation modes.

They answer different questions and must not be conflated:

1. `mechanical checks`
   - answer whether an objective documented contract still holds
2. `LLM-assisted critique`
   - surfaces likely confusion, suspicious proxies, missing failure modes, and prompt-shaped local optimization risk
3. `human judgment`
   - closes questions about product direction, value, taste, and whether a proposed proxy is worth institutionalizing

Current rule:

- do not replace a human judgment question with a fake objective score
- do not let an LLM critic act like a final approver
- do not promote a first-draft critique directly into a repository check

## Promotion Ladder

The approved promotion order is:

1. critique
2. documented policy
3. repeated manual use
4. narrow mechanical enforcement

This order exists to prevent the repository from turning first-draft heuristics into fake rigor.

If a proposed metric, evaluator output, or benchmark cannot survive repeated manual use with a clear decision impact, it should remain a doc or review prompt artifact rather than becoming a hard check.

## Metric And Check Admission Rule

Before a new metric, benchmark, or repository check is promoted into the harness, it must document:

1. the protected behavior
2. the measured proxy
3. the likely gaming vector
4. the decision the artifact is expected to change
5. the revalidation or removal condition

If any of those fields are weak or missing:

- the artifact must remain in docs or review prompts
- it must not be promoted into a repository check yet

This rule exists because a measurable target without decision impact is fake rigor, and a proxy without a revalidation path will eventually become stale.

## What Stays In Documents And Prompts For Now

The following areas are still intentionally document-led:

- detailed `trading` package layout
- the full long-term schemas for `OrderIntent`, `OrderEvent`, and `FillEvent`
- detailed synthetic tick generation algorithms
- generalized order-effect timing beyond the current MVP default
- the final placement and role of `ml`

These topics are too likely to evolve to justify early hard-coding into rigid checks.

## Retired Control-Plane Artifacts

Older workflow-control artifacts such as scorecards, promotion logs, and legacy
execution-plan archives may remain in the repository for audit continuity, but
they are not part of the active workflow surface.

When one of those artifacts is retired:

- keep only the minimal rationale needed for future operators in the surviving
  governing docs
- route current work through `AGENTS.md`, the active plan under `docs/plans/`,
  and the governing design or product docs instead
- do not preserve retired artifacts as a second workflow authority

## Slice-Specific Defaults

Product specs are allowed to narrow open global questions for a specific implementation slice.

When this happens:

- the design docs describe the long-lived global direction
- the product spec defines the current slice's narrower contract
- repeated or stabilized slice rules may later be promoted back into long-lived docs and checks

## Promotion Criteria

Promote a rule from prose into a check when one or more of these are true:

1. the same drift happens twice
2. the same review comment repeats
3. agents repeatedly misunderstand the same boundary
4. a single mistake can damage financial semantics
5. the rule is objective and cheap to evaluate

Additional requirement:

6. the rule protects a declared contract or canonical user journey strongly enough to justify the maintenance cost

## Open Questions And Blockers

Not every open question is an implementation blocker.

Each implementation slice should explicitly separate:

1. questions that block starting implementation
2. questions that may stay deferred

For the current implemented backtest baseline, [../product-specs/backtest-mvp.md](../product-specs/backtest-mvp.md) is the authority on that distinction. For the shipped `research` usability layer built on top of it, [../product-specs/research-ergonomics.md](../product-specs/research-ergonomics.md) is the authority.

## Current Governance Priority

Before new code work begins, the harness should ensure:

- agents can find the right documents quickly
- top-level architecture and trading-kernel contracts remain distinct
- the repository catches the most obvious structural drift
- current implemented-scope docs and any active expansion slice do not erode the long-lived architecture

## Summary

The current governance model is to keep architecture, trading semantics, and slice scope in separate documents, enforce only the highest-signal boundaries mechanically, and promote repeated drift into checks over time.
