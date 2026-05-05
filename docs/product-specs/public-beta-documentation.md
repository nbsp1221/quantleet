# Public Beta Documentation Spec

## Status

- Status: `draft`
- Class: `product-spec`
- Scope: first public beta documentation, release-facing repository documents,
  and the separation between public user docs and agent-internal docs

Related documents:

- [research-ergonomics.md](research-ergonomics.md)
- [parameter-exploration.md](parameter-exploration.md)
- [backtest-mvp.md](backtest-mvp.md)
- [backtest-plotting.md](backtest-plotting.md)
- [data-ingestion.md](data-ingestion.md)
- [../design-docs/package-topology-and-naming.md](../design-docs/package-topology-and-naming.md)
- [../design-docs/quantleet-architecture.md](../design-docs/quantleet-architecture.md)
- [../../AGENTS.md](../../AGENTS.md)
- [../../README.md](../../README.md)

This document defines what must be true of the first public beta
documentation surface. It is a product spec, not an implementation plan. It
describes the user-facing documentation contract and the repository-level
separation needed to keep public docs from conflicting with the existing
agent-driven development system of record.

## Background And Problem Definition

`quantleet` is close to its first public beta target: a polished single-symbol
Python backtesting experience for users who want to test a strategy on
historical OHLCV data. The implemented beta surface already includes strategy
authoring ergonomics, data sources, market/limit/stop-family order behavior,
explicit quantity and percent sizing, typed result reporting, result plotting,
and constrained parameter exploration.

The remaining beta gap is no longer primarily runtime functionality. It is
public comprehension and trust:

- a new user needs to understand what the project does in the first minute
- a Python user needs a fresh install path and a first backtest path
- a quant user needs examples that show reporting, plotting, sizing, stop
  orders, and parameter exploration without implying unsupported scope
- a contributor needs contribution, security, and release-facing documents
- an agent needs the existing internal workflow authority to remain intact

The repository already has a large `docs/` tree because development is
agent-driven. Existing directories such as `docs/product-specs`,
`docs/design-docs`, `docs/plans`, `docs/research`, and `docs/references` are
part of the internal product, architecture, planning, and review system. If
public beta pages are added directly beside those directories without a clear
boundary, users and agents will both face an ambiguous documentation model:
public quickstarts, internal plans, historical research, and current product
contracts would all appear to be peer documentation.

The public beta documentation feature exists to solve that boundary problem.
It must make the beta product understandable to external users while preserving
the internal docs as the system of record for agent work.

## Goals

- Provide a public documentation surface for first-beta users.
- Make the first beta workflow discoverable from GitHub and, later, a docs
  website.
- Give users a clean path from installation to a first backtest, then to
  report, plot, and parameter exploration inspection.
- Clearly state what the beta supports and what it does not support.
- Keep public docs separate from agent-internal authority documents.
- Add release-facing repository documents that users and contributors expect
  from an open-source Python financial library.
- Preserve the current agent-first planner/generator/evaluator workflow.
- Make future test specs and implementation plans able to validate the public
  docs without re-deciding scope.

## Non-Goals

- Do not add new trading, backtest, research, paper-trading, or live-trading
  runtime functionality.
- Do not make paper trading, live trading, shorting, leverage, multi-symbol, or
  multi-timeframe workflows part of the first public beta.
- Do not expose `docs/plans` or other internal workflow records as the public
  user documentation experience.
- Do not move or rewrite the existing internal documentation system as part of
  the product contract.
- Do not create or modify `LICENSE`; the license is MIT, and the root
  `LICENSE` file is assumed to be created separately by the project owner.
- Do not add GitHub Pages deployment automation in this documentation cleanup
  slice.
- Do not add multilingual documentation or localization infrastructure for the
  first beta.
- Do not require generated API reference tooling before the first beta.
- Do not publish a detailed public roadmap as a beta commitment.
- Do not make the internal AI-agent-led development process the public product
  positioning.
- Do not add GitHub issue templates in this slice.
- Do not treat README badges, docs themes, or visual branding as the product
  requirement itself.

## User Intent

### Python Quant User

The user wants to install the package, copy a small example, run a backtest on
historical OHLCV data, and understand the result without learning the internal
architecture first.

### Research User

The user wants to compare a small finite parameter grid, inspect the best or
selected run, and understand that grid results are research diagnostics rather
than trading recommendations.

### GitHub Visitor

The visitor wants to know whether the project is alive, what is implemented,
how to install it, where the official docs live, what the risks are, and how
the project handles issues and contributions.

### Contributor

The contributor wants to know how to set up the repo, run verification, update
docs, file issues, submit PRs, and understand which docs are public user docs
versus internal product and agent workflow docs.

### AI Coding Agent

The agent needs public docs to remain distinguishable from internal authority.
It should continue to follow `AGENTS.md`, governing docs, and active plans for
implementation work, not infer workflow rules from public quickstart pages.

## Core Requirements

1. Public beta documentation must have a distinct boundary from internal
   agent/workflow documentation.
2. The public beta docs must describe the current implemented beta scope, not a
   future roadmap as if it were already shipped.
3. The public beta docs must route users toward canonical public imports and
   away from deep internals.
4. The public beta docs must include executable or verification-backed examples
   for the canonical first-run workflows.
5. The public beta docs must include explicit unsupported-scope notes for
   multi-symbol, shorting, leverage, paper trading, live trading, and broad
   optimization claims.
6. Release-facing repository documents must support public trust and
   contribution hygiene.
7. Internal product specs, design docs, plans, and research records must remain
   available for agents and maintainers without becoming the public docs
   navigation.

## Functional Requirements

### Public Documentation Boundary

- The public documentation source must live under a dedicated boundary, with
  `docs/site/` as the current product target.
- The first public docs site must use Astro Starlight as the documentation
  framework.
- The first public docs site must be structured so it can later be deployed to
  GitHub Pages, but GitHub Pages automation is out of scope for this slice.
- Public documentation navigation must include only public user and
  contributor-facing pages.
- Internal directories such as `docs/product-specs`, `docs/design-docs`,
  `docs/plans`, `docs/research`, `docs/references`, `docs/reviews`, and
  `docs/exec-plans` must not be treated as the default public docs site.
- Public documentation navigation must not link directly to internal AI-agent
  workflow documents such as `docs/plans`, `docs/product-specs`,
  `docs/design-docs`, `docs/research`, or `AGENTS.md`.
- Contributor-facing documents may mention internal workflow requirements only
  when needed for contribution safety and review.
- First-beta public docs must be English-only. Multilingual documentation and
  i18n structure are out of scope for this slice.

### Required Public Docs Areas

The first beta public docs must cover:

- project overview
- installation
- quickstart
- examples
- getting started paths
- backtesting guide
- strategy authoring guide
- data source guide
- result reporting guide
- plotting guide
- parameter exploration guide
- order sizing guide
- stop-order guide
- beta safety/scope notes
- public import reference

The target structure is:

```text
docs/site/
  index.md
  installation.md
  quickstart.md
  examples.md
  getting-started/
  guides/
  concepts/
  reference/
```

This tree is a product boundary, not a mandate that every page must be created
in one slice.

Public beta documentation must describe the current beta scope and known
limitations, but must not present a detailed public roadmap as a commitment.
Future work may be tracked internally, while public docs focus on what users
can rely on today.

Public beta documentation must include a concise financial disclaimer in:

- `README.md`
- `docs/site/index.md`
- `docs/site/quickstart.md`

The disclaimer must state that Quantleet is research/software tooling, not
financial advice; that backtest results do not guarantee future performance;
and that users are responsible for data quality, assumptions, execution risk,
and trading decisions.

### Release-Facing Repository Documents

The documentation cleanup scope includes these release-facing repository
documents:

- `README.md`
- `CONTRIBUTING.md`
- `SECURITY.md`
- `CHANGELOG.md`
- `.github/PULL_REQUEST_TEMPLATE.md`

The repository also depends on these existing or separately managed documents:

- `LICENSE`
- `AGENTS.md`
- `ARCHITECTURE.md`

Their expected roles are:

- `README.md`: public first impression, install path, minimal example, result
  preview, official docs link, beta scope, disclaimer, and contribution links
- `LICENSE`: legal use terms. The license is MIT. This file is assumed to
  exist but must not be created or modified by this work.
- `CONTRIBUTING.md`: human and agent contribution workflow, setup, tests,
  docs update expectations, issue/PR norms
- `SECURITY.md`: vulnerability reporting, secrets policy, and financial
  safety boundaries
- `CHANGELOG.md`: release history and user-visible changes
- `.github/PULL_REQUEST_TEMPLATE.md`: PR summary, linked issue when
  applicable, change type, docs impact, verification evidence, changelog impact
  when applicable, and AI-assisted contribution ownership disclosure
- `AGENTS.md`: agent workflow contract and internal authority routing
- `ARCHITECTURE.md`: concise public architecture map and safety tier summary

The first public beta version is `0.1.0b1`. Public beta documentation,
release-facing repository docs, and package metadata must use that version
when they need to refer to the first beta release.

`README.md` must act as a landing page, quick judgment surface, and official
docs entry point. It should include project positioning, beta scope,
installation, a minimal quickstart, a compact result/report/plot example,
links to public docs and examples, contribution and security links, and the
MIT license. It should not include the full tutorial, full API reference,
internal architecture history, internal agent workflow details, long research
notes, or a detailed roadmap.

### Canonical Public Examples

The first public beta must include exactly three canonical examples:

1. SMA crossover quickstart
   - strategy authoring
   - `BacktestEngine` execution
   - `result.report` inspection
   - `result.plot()` inspection

2. Orders and sizing
   - fixed `qty`
   - `qty_percent`
   - market, limit, stop-market, and stop-limit order families
   - reservation, fills, and positions inspection

3. Parameter exploration
   - `ParameterStudy(...).grid_search(...)`
   - small SMA grid
   - `fast < slow` style constraint
   - parameter result comparison
   - selected or best run inspection

Examples must not imply support for unsupported beta scope. Examples must
prefer documented public imports.

Reporting and plotting belong inside the quickstart flow rather than as a
separate canonical example.

### GitHub Contribution Surface

The public beta repository should provide a GitHub pull request template.
GitHub issue templates are out of scope for this documentation cleanup slice.
`CONTRIBUTING.md` and `SECURITY.md` must still provide enough guidance for bug
reports, feature requests, documentation issues, and security reports until
issue templates are added in a later slice.

The PR template should ask for:

- summary
- linked issue when applicable
- change type
- docs impact
- test/verification evidence
- release note or changelog impact when applicable
- whether any AI-generated or AI-assisted code was reviewed line-by-line by the
  human PR author
- confirmation that the human PR author understands and stands behind the
  change

AI-assisted and agent-led development may be disclosed in contributor-facing
surfaces. Any AI-generated or AI-assisted contribution must be reviewed,
understood, owned, and verified by a human contributor before acceptance.
Public-facing product documentation must present Quantleet primarily as a
trustworthy Python quant/backtesting library, not as an AI-development
experiment.

### Public Package Metadata

Public package metadata should identify:

- project description
- supported Python versions
- license: MIT
- homepage
- documentation URL
- repository URL
- issue tracker URL
- changelog URL
- relevant keywords
- relevant classifiers

The first public beta package version should be `0.1.0b1`. The documentation
URL may point to the later GitHub Pages site once deployment is implemented;
deployment itself is out of scope for this documentation cleanup slice.

### Curated Public API Reference

The first beta must include a curated public API reference rather than a
generated API reference. The reference must focus on the public objects users
are expected to import or interact with directly, including:

- `BacktestEngine`
- `Strategy`
- `Bar`
- `Order`
- `OrderType`
- `OrderSide`
- `TimeInForce`
- `BacktestResult`
- `result.report`
- `result.plot()`
- `ParameterStudy`
- `ParameterStudy.grid_search`
- public data loading helpers or built-in data source entry points
- public `ta` helpers
- public `qc` helpers

Generated API reference tooling may be considered in a later technical plan,
after the public API boundary and docstring expectations are mature enough to
support it.

## Nonfunctional Requirements

- **Clarity:** A new user should not need to read internal plans or product
  specs before running the quickstart.
- **Truthfulness:** Docs must describe shipped behavior and clearly label beta
  limitations.
- **Agent compatibility:** Public docs must not weaken or override the
  repository workflow contract in `AGENTS.md`.
- **Maintainability:** Each public topic should have one canonical page. Other
  pages should link rather than duplicate long explanations.
- **Testability:** Core examples should be executable through the repo-local
  verification surface, notebook validation, docs snippet tests, or another
  explicit check chosen by a later implementation plan.
- **Financial safety:** Public docs must include a plain risk disclaimer and
  must not present backtest or parameter study output as trading advice.
- **Install realism:** Installation docs must distinguish package-user setup
  from contributor setup.
- **Release readiness:** Release-facing docs and metadata must be accurate
  before broad public beta positioning.
- **Minimal disruption:** Existing internal docs should not be moved unless a
  later implementation plan proves the move is necessary.
- **Public positioning:** Public user docs must prioritize trust, correctness,
  installation, examples, API usage, and beta limitations over the internal
  AI-agent-led development process.
- **Static deployment readiness:** Public docs must be compatible with Astro
  Starlight and future GitHub Pages deployment, even though deployment
  automation is out of scope for this slice.

## Major Scenarios

### 1. GitHub Visitor To First Backtest

A visitor opens GitHub, reads the README, sees what the beta supports, installs
the package, copies the quickstart, runs a single-symbol backtest, and inspects
`result.report` and `result.plot()`.

### 2. Documentation Site Quickstart

A user opens the public docs site, follows installation and quickstart pages,
understands the public imports, runs the `DataFrameDataSource` path, and reaches
a readable backtest result without reading internal architecture docs.

### 3. Parameter Exploration Example

A research user opens the parameter exploration guide, materializes one
`BarSeries`, runs `ParameterStudy(...).grid_search(...)` over a small SMA grid,
filters invalid combinations with a constraint, reads structured records, and
inspects the selected run's report and plot.

### 4. Orders And Sizing Example

A user opens the orders-and-sizing example, compares fixed quantity and
percentage sizing, sees market, limit, stop-market, and stop-limit order
families in a single-symbol historical backtest, and inspects reservations,
fills, and positions without assuming live execution support.

### 5. Contributor Updates Public Docs

A contributor changes a public API or example. They read `CONTRIBUTING.md`,
update the relevant `docs/site` page, avoid editing internal authority docs
unless required, run the documented verification commands, and submit a PR with
docs and test evidence. If AI assistance was used, the human PR author
discloses it, reviews the output line-by-line, and stands behind the change.

### 6. Agent Performs Internal Work

An AI coding agent receives a runtime change request. It reads `AGENTS.md` and
governing docs, creates an active plan under `docs/plans`, and treats
`docs/site` as user documentation rather than workflow authority.

### 7. User Checks Unsupported Scope

A user asks whether the beta supports live trading, paper trading, shorting,
leverage, or multi-symbol portfolios. Public docs provide a clear unsupported
scope note and route future planning to the appropriate product specs without
implying current support.

### 8. User Looks For Roadmap

A user looks for planned future features. Public docs explain current beta
capabilities and known limitations, but do not present a detailed roadmap as a
commitment.

## Edge Cases And Failure Scenarios

- A public docs page contradicts a product spec.
- A README example uses a deep internal import that later changes.
- The public docs nav accidentally exposes `docs/plans` as user-facing
  documentation.
- A public docs page links to internal AI-agent workflow records and causes
  users to treat internal plans as public user guidance.
- A user installs the package but `result.plot()` fails because dependency
  metadata is incomplete.
- A parameter exploration example implies optimizer or trading recommendation
  semantics.
- A quickstart requires hidden local files, network credentials, or live
  exchange access.
- A docs example uses unsupported multi-symbol, shorting, leverage, paper, or
  live behavior.
- Internal docs are renamed or moved, breaking existing agent workflow routing.
- A translated or generated docs page is edited manually after localization is
  introduced.
- A package metadata field points to a docs URL that is not yet published.
- A changelog entry claims release readiness before install and example checks
  pass.
- A public page presents a detailed roadmap as a commitment rather than current
  beta scope.
- Public docs make AI-agent-led development the main product pitch and weaken
  trust in the financial research tooling.
- A PR includes AI-generated code without human review, ownership, and
  verification evidence.
- Missing issue templates leave users unsure how to file reports; the fallback
  guidance in `CONTRIBUTING.md` and `SECURITY.md` must cover this until issue
  templates are added.
- A contributor updates implementation behavior but misses public docs.
- An issue report lacks a minimal reproduction or environment details.
- A security-sensitive report is filed as a public issue instead of through the
  security reporting path.

## External Contracts

- `AGENTS.md` remains the repository entry contract for agent work.
- `docs/product-specs/index.md` remains the routing index for product behavior
  specs.
- `docs/design-docs/index.md` remains the routing index for design authority.
- `docs/plans/` remains the active planning and evaluator artifact location for
  non-trivial work.
- Public beta behavior remains governed by the existing product specs for
  data ingestion, backtesting, research ergonomics, result plotting, parameter
  exploration, order sizing, order reservation, and stop-limit behavior.
- The public beta scope remains single-symbol, single-timeframe, historical,
  long-or-flat, and non-live unless later product specs explicitly expand it.
- Tier A `trading` and `execution` work still requires explicit human approval
  before implementation can be treated as approved.
- Public docs must use documented package surfaces such as `quantleet.data`,
  `quantleet.backtest`, and `quantleet.research` rather than relying on deep
  internal modules.
- GitHub PR and release-facing docs must not require external
  connectors or private systems for ordinary open-source participation.
- The first public beta release identifier is `0.1.0b1`.
- The license is MIT. A root `LICENSE` file is assumed to exist, but this
  documentation cleanup work must not create or modify it.
- The public docs framework is Astro Starlight.
- The first hosting target is GitHub Pages, but deployment automation is out
  of scope for this slice.
- Public docs are English-only for the first beta. Multilingual support is out
  of scope.

## Success Conditions

The public beta documentation product is ready when:

- README presents the beta product clearly and routes to public docs.
- README presents Quantleet as a trustworthy Python quant/backtesting library,
  not as an AI-development experiment.
- A clean install path is documented and verified.
- A user can copy a quickstart and produce a `BacktestResult`.
- Public docs show `result.report` and `result.plot()` as normal inspection
  paths.
- Public docs include exactly three canonical examples: SMA crossover
  quickstart, orders and sizing, and parameter exploration.
- Public docs include a canonical constrained-grid `ParameterStudy` example.
- Public docs include explicit fixed `qty`, `qty_percent`, reservation, fills,
  positions, and stop-family examples.
- Public docs state unsupported beta scope plainly.
- Root `CONTRIBUTING.md`, `SECURITY.md`, and `CHANGELOG.md` exist and are
  accurate.
- Root `LICENSE` exists, identifies MIT licensing, and was not created or
  modified by this documentation cleanup work.
- `.github/PULL_REQUEST_TEMPLATE.md` exists and asks for verification evidence
  and AI-assisted contribution ownership disclosure.
- Public package metadata includes license, project URLs, keywords, and
  classifiers appropriate for the chosen release posture.
- Public package and documentation references use `0.1.0b1` when referring to
  the first public beta.
- Public docs are compatible with Astro Starlight and future GitHub Pages
  deployment without requiring deployment automation in this slice.
- Public docs are English-only and do not introduce i18n requirements.
- Public docs include the concise financial disclaimer in README, docs home,
  and quickstart.
- Public docs do not present a detailed public roadmap as a commitment.
- Public docs are separated from internal product specs, design docs, plans,
  research, and workflow records.
- Public docs navigation does not link directly to internal AI-agent workflow
  documents.
- Documentation verification catches broken links, missing public docs, and
  stale canonical examples according to the chosen implementation plan.
- Internal agent workflow checks still pass.

## Open Questions

1. Should internal docs remain under `docs/` forever, or should a later cleanup
   move agent-only material into `agent_docs/`?
   - Default assumption if unanswered: keep existing internal docs in place and
     add only `docs/site` for public docs.

2. What exact GitHub Pages URL or custom domain should package metadata and
   README use once deployment is implemented?
   - Default assumption if unanswered: avoid claiming a hosted docs URL until
     the GitHub Pages deployment exists.

3. Should GitHub issue templates be added in a later slice?
   - Default assumption if unanswered: keep issue template creation out of this
     slice and rely on `CONTRIBUTING.md` plus `SECURITY.md` for report
     guidance.

4. Which curated public API objects are release blockers if the implementation
   plan finds that some names are not stable enough to document?
   - Default assumption if unanswered: document only stable public imports and
     leave unstable helpers out of the first beta reference.
