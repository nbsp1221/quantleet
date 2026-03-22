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

The repository uses four distinct document classes for this area:

1. [quantcraft-architecture.md](quantcraft-architecture.md)
   - approved top-level architecture
2. [trading-kernel-contract-draft-ko.md](trading-kernel-contract-draft-ko.md)
   - long-lived trading-kernel contract draft
3. [architecture-governance.md](architecture-governance.md)
   - approved governance and promotion policy
4. [../product-specs/backtest-mvp.md](../product-specs/backtest-mvp.md)
   - approved slice-specific product spec for the first implementation slice

This split prevents agents from conflating:

- structural architecture
- trading semantics
- harness policy
- current implementation-slice scope

## What We Enforce Mechanically Now

At this stage, only rules that are objective, cheap to check, and likely to create repository drift are enforced mechanically.

Current enforced or intended-to-enforce-now rules include:

- long-lived architecture and contract documents live under `docs/design-docs/`
- `ARCHITECTURE.md` and the design-doc index point to the approved architecture documents
- flat `tests/test_*.py` files are disallowed
- the repo-local harness remains `scripts/ + poe`
- live tests stay out of the default lane
- context dependency rules should be promoted into structure tests as packages materialize

## What Stays In Documents And Prompts For Now

The following areas are still intentionally document-led:

- detailed `trading` package layout
- the full long-term schemas for `OrderIntent`, `OrderEvent`, and `FillEvent`
- detailed synthetic tick generation algorithms
- generalized order-effect timing beyond the current MVP default
- the final placement and role of `ml`

These topics are too likely to evolve to justify early hard-coding into rigid checks.

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

## Open Questions And Blockers

Not every open question is an implementation blocker.

Each implementation slice should explicitly separate:

1. questions that block starting implementation
2. questions that may stay deferred

For the current first slice, [../product-specs/backtest-mvp.md](../product-specs/backtest-mvp.md) is the authority on that distinction.

## Current Governance Priority

Before new code work begins, the harness should ensure:

- agents can find the right documents quickly
- top-level architecture and trading-kernel contracts remain distinct
- the repository catches the most obvious structural drift
- the active implementation slice does not erode the long-lived architecture

## Summary

The current governance model is to keep architecture, trading semantics, and slice scope in separate documents, enforce only the highest-signal boundaries mechanically, and promote repeated drift into checks over time.
