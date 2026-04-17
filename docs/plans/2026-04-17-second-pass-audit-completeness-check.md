# Active Plan

- Date: 2026-04-17
- Task: Second-pass completeness check on the post-migration audit findings
- Status: `complete`
- Risk class: `Tier A`
- Requestor: `Naki`
- Owner: Codex

## Planner Contract

- Goal:
  - challenge the previous full-codebase audit and determine whether it missed
    any material findings before implementation work starts
  - focus on omission risk rather than re-litigating already established issues
- Governing docs:
  - [`AGENTS.md`](../../AGENTS.md)
  - [`README.md`](../../README.md)
  - [`ARCHITECTURE.md`](../../ARCHITECTURE.md)
  - [`docs/product-specs/index.md`](../product-specs/index.md)
  - [`docs/design-docs/index.md`](../design-docs/index.md)
  - [`docs/design-docs/package-topology-and-naming.md`](../design-docs/package-topology-and-naming.md)
  - [`docs/RELIABILITY.md`](../RELIABILITY.md)
  - [`docs/SECURITY.md`](../SECURITY.md)
  - [`docs/DESIGN.md`](../DESIGN.md)
  - [`docs/PLANS.md`](../PLANS.md)
  - [`docs/plans/2026-04-17-full-codebase-post-migration-audit.md`](2026-04-17-full-codebase-post-migration-audit.md)
- Why these are governing:
  - they define the final topology, audit rules, Tier A boundary, and the
    first-pass audit conclusions that this second pass must challenge
- In-repo scope:
  - read-only audit of likely blind spots:
    - implicit validation gaps
    - stale or contradictory tests/docs not caught in first pass
    - fallback/facade behavior still masquerading as intentional surface
    - dead or misleading control-plane/tooling residue
  - update this plan with any newly discovered material findings and the final
    verdict on whether the first pass missed anything important
- Out-of-repo scope:
  - implementation or fixes
  - external-system validation
- Tier A progression requested: `yes`
- Approval record, if required:
  - requestor: `Naki`
  - human approver: `Naki`
  - countersignature or equivalent verification marker:
    - explicit user instruction in the current chat on 2026-04-17 to verify
      again, using subagent orchestration, whether the previous audit missed
      anything material
  - scope granted:
    - repository-local second-pass Tier A audit with read-only subagents and
      repository verification where needed
  - expiration:
    - end of this second-pass audit slice
  - audit reference or sanitized audit link:
    - current chat transcript for 2026-04-17
- Verification commands:
  - targeted blind-spot search:
    - `rg -n "TODO|FIXME|XXX|deprecated|compat|compatibility|shim|fallback|transitional|legacy" src tests docs scripts`
    - `rg -n "raise ValueError|ZeroDivisionError|fee_rate|slippage_ticks|initial_cash|__getattr__|import_module\\(" src tests`
    - `find src tests -type d -name __pycache__ | sort`
  - optional fresh proof if a new claim depends on runtime behavior:
    - `uv run python - <<'PY' ...`
- Success criteria:
  - explicitly state whether the first-pass audit missed any new material
    issue
  - if yes, identify the issue with exact file references and reasoning
  - if no, state that no additional material issue was found after the second
    pass and name any remaining non-material residue
  - subagent research split and review fan-out both complete with
    evidence-bearing returns
- Out of scope:
  - changing code to fix anything found

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice:
  - do not repeat the first-pass findings unless needed as comparison context
  - only report newly discovered omissions or confirm that none material were
    missed
  - reviewer fan-out must explicitly challenge the completeness of the first
    audit, not merely summarize it
- Acceptance artifact location:
  - this active plan plus the final user-facing report
- How the generator and evaluator agreed on done before execution:
  - done means a defensible answer to “did we miss anything material?”
- Checks the evaluator will use:
  - targeted search commands
  - read-only subagent findings
  - reviewer fan-out
- Auto-fail conditions:
  - summary-only reviewer output
  - no explicit omission verdict
  - findings that merely restate the first-pass audit without adding confidence

## Generator Work Log

- Planned slice order:
  1. target likely blind-spot searches and residue inventory
  2. run read-only research split with disjoint “missed issue” scopes
  3. synthesize candidate omissions
  4. run review fan-out to challenge whether those are truly material
  5. record final omission verdict here
- Notes:
  - no code edits except this audit artifact
  - no `git add`; staging remains human-only
- Blockers or scope changes:
  - 2026-04-17: second-pass synthesis accepted one newly omitted material
    finding around the breadth of the `quantcraft.integrations.venues.ccxt`
    public surface.
  - 2026-04-17: no additional new critical correctness hole was found beyond
    the two already recorded in the first-pass audit.

## Evaluator Review

- Findings:
  - New medium-severity omitted finding:
    - [src/quantcraft/integrations/venues/ccxt/__init__.py](../../src/quantcraft/integrations/venues/ccxt/__init__.py)
      currently exports a wider surface than the intended stable facade.
    - It re-exports private helpers and raw third-party dependency symbols in
      `__all__`, including:
      - `_fetch_ohlcv_range`
      - `_make_ccxt_exchange`
      - `_validate_symbol_contract`
      - `_DEFAULT_PAGINATION_LIMIT`
      - `ccxt`
    - Current smoke/build proofs only assert the presence of `Exchange` and
      `MarketType`, not the absence of these helper leaks:
      - [tests/smoke/local/test_public_imports.py](../../tests/smoke/local/test_public_imports.py)
      - [tests/integration/commands/test_built_artifact_imports.py](../../tests/integration/commands/test_built_artifact_imports.py)
    - Why this matters:
      - it is not a legacy shim leak, but it is still an accidental-looking
        public API expansion and a built/smoke test blind spot
      - it weakens refactor freedom around the integration boundary
  - No other new material finding was discovered beyond the previously known
    set:
    - `initial_cash=0` zero-division hole
    - negative `CostConfig` semantics hole
    - transitional governing-doc wording
    - migration-history / legacy-control-plane residue in active checks
  - Explicit non-finding from second pass:
    - no additional legacy public shim surface was found beyond what the first
      audit already covered
    - no new critical runtime bug was discovered beyond the two already logged
- Verification evidence:
  - Targeted second-pass searches:
    - `rg -n "TODO|FIXME|XXX|deprecated|compat|compatibility|shim|fallback|transitional|legacy" src tests docs scripts`
    - `rg -n "raise ValueError|ZeroDivisionError|fee_rate|slippage_ticks|tick_size|initial_cash|__getattr__|import_module\\(" src tests`
    - `find src tests -type d -name __pycache__ | sort`
    - `find src tests -type f | sed 's#^#/#' | rg '/(test_stage|test_.*slice|_repo_tools|_notebook_tools|__init__\\.py$)'`
  - Read-only subagent second-pass research split:
    - `Einstein`: topology residue and extra omitted findings
    - `Bernoulli`: public/import-surface blind spots
    - `Carson`: guardrail/runtime-verification blind spots
  - Research split returns:
    - `Bernoulli`: no new material findings beyond known set
    - `Carson`: no new material findings beyond known set
    - `Einstein`: one new material finding on `integrations.venues.ccxt.__all__`
  - Review fan-out on the new candidate omission:
    - `Hegel`: material omitted finding, medium severity
    - `Anscombe`: material omitted finding, medium severity
    - `Epicurus`: material omitted finding, medium severity, not a blocker for
      the prior runtime verdict
- Final disposition:
  - `The first-pass audit was not fully complete.`
  - It missed one additional medium-severity issue:
    - the `quantcraft.integrations.venues.ccxt` package currently exports a
      broader public surface than intended, and current smoke/build tests do
      not constrain that leak
  - Updated honest status:
    - the known material set is now:
      1. `initial_cash <= 0` zero-division bug
      2. negative `CostConfig` semantic-validation bug
      3. transitional governing-doc incompleteness
      4. migration-history / legacy-control-plane residue in active checks
      5. overly broad `quantcraft.integrations.venues.ccxt` public facade
  - Beyond that updated set, the second pass did not find another material
    omission.
