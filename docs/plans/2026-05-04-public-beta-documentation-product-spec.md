# Public Beta Documentation Product Spec Plan

- Date: `2026-05-04`
- Task: Define the product contract for the first public beta documentation
  surface.
- Status: `complete`
- Risk class: `Tier B`
- Requestor: `User`
- Owner: `Codex`

## Planner Contract

- Goal:
  - Create a product spec that defines what public beta documentation must
    provide, why it exists, how it should coexist with the existing
    agent-internal docs, and which decisions remain open.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/research-ergonomics.md`
  - `docs/product-specs/parameter-exploration.md`
  - `docs/design-docs/index.md`
  - `docs/design-docs/package-topology-and-naming.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/DESIGN.md`
  - `docs/PLANS.md`
- Why these are governing:
  - The work defines user-facing beta documentation for the existing
    research/backtest product surface while preserving the repository's
    existing agent-first documentation authority and workflow contract.
- In-repo scope:
  - Add one product spec under `docs/product-specs/`.
  - Route that spec from `docs/product-specs/index.md`.
  - Record decided scope and unresolved product questions.
- Out-of-repo scope:
  - No package publishing.
  - No GitHub Pages or Read the Docs setup.
  - No generated docs build.
  - No runtime code changes.
- Tier A progression requested: `no`
- Approval record, if required:
  - Not required. This documentation product spec concerns Tier B
    research/backtest public documentation and does not change `trading` or
    `execution` behavior.
- Verification commands:
  - `uv run poe repo-check`
  - `uv run pytest tests/structure/docs tests/structure/repo -q`
- Success criteria:
  - The product spec covers background/problem, goals, non-goals, user intent,
    requirements, scenarios, edge cases, external contracts, success conditions,
    and open questions.
  - The spec preserves `docs/product-specs`, `docs/design-docs`, and
    `docs/plans` as internal authority and defines `docs/site` as the proposed
    public documentation boundary.
  - The spec avoids over-deciding implementation details such as final hosting,
    license, versioning, and language policy.
  - Product-spec routing points future public beta documentation work to the
    new spec.
- Out of scope:
  - Writing the actual public documentation pages.
  - Creating `mkdocs.yml`.
  - Adding `LICENSE`, `CONTRIBUTING.md`, `SECURITY.md`, or `CHANGELOG.md`.
  - Moving existing internal documents.

## Evaluator Acceptance Contract

- Evaluator owner: `Codex`
- Evaluator-owned done contract for this slice:
  - Review the new spec against the requested section list, existing governing
    docs, and the prior research conclusions from financial and agent-native
    open-source projects.
- Acceptance artifact location:
  - This plan's `Evaluator Review` section plus the final user report.
- How the generator and evaluator agreed on done before execution:
  - The planner contract above fixes scope, required sections, open-question
    handling, and verification commands before edits.
- Checks the evaluator will use:
  - Manual spec review.
  - `uv run poe repo-check`.
  - `uv run pytest tests/structure/docs tests/structure/repo -q`.
- Auto-fail conditions:
  - The spec treats internal planning docs as public user docs.
  - The spec claims unresolved choices are decided.
  - The spec changes runtime product behavior.
  - Documentation structure checks fail.

## Generator Work Log

- Planned slice order:
  1. Add the public beta documentation product spec. `complete`
  2. Add routing to the product spec index. `complete`
  3. Review the spec for required sections and unresolved questions. `complete`
  4. Run documentation verification. `complete`
- Notes:
  - The user wants the product spec first, then follow-up discussion on open
    decisions.
  - Added `docs/product-specs/public-beta-documentation.md`.
  - Added product-spec routing from `docs/product-specs/index.md`.
  - Updated the product spec after follow-up decisions on MIT licensing,
    `docs/site`, Astro Starlight, GitHub Pages direction, English-only docs,
    AI-assisted contribution disclosure, `0.1.0b1`, canonical examples,
    curated API reference, public roadmap limits, financial disclaimers,
    release-facing docs, PR template scope, issue template exclusion, and
    public/internal docs linking boundaries.
- Blockers or scope changes:
  - None.

## Evaluator Review

- Findings:
  - No blocking findings. The updated product spec covers the requested
    product sections, preserves internal docs as agent/workflow authority,
    defines `docs/site` as the public documentation boundary, and moves
    human-confirmed decisions from open questions into the governing
    requirements.
  - The spec now treats MIT licensing, `0.1.0b1`, Astro Starlight, GitHub
    Pages direction, English-only public docs, curated API reference, three
    canonical examples, concise financial disclaimers, contributor-facing
    AI-assisted disclosure, PR template inclusion, and issue template exclusion
    as decided product constraints.
  - The spec keeps deployment automation, generated API reference tooling,
    multilingual docs, issue templates, detailed public roadmap, and direct
    public nav links to internal AI-agent workflow docs out of scope for this
    slice.
- Verification evidence:
  - `git diff --check` passed with no output.
  - `uv run poe repo-check` passed with output `repository checks passed`.
  - `uv run pytest tests/structure/docs tests/structure/repo -q` passed with
    output `70 passed in 0.17s`.
- Final disposition:
  - Accepted for this product-spec slice.
