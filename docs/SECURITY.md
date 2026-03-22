# Security

This document defines repository-level safety and secrets rules for financial software work.

## Secrets

- Do not store exchange credentials or broker credentials in the repository.
- Do not rely on undocumented local environment state as a test fixture.
- Any future secrets flow must be documented before live use.

## Financial Safety

- Tier A domains are `trading` and `execution`.
- Tier A changes require explicit human approval.
- Live trading is not agent-autonomous.
- Any code that can create exposure, move funds, or alter trading state must have matching documentation in reliability and product-spec docs.

## Current Scope

The current repository does not implement live trading, but the harness must define the safety boundary before those domains are added.
