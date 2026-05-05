# Public Beta Documentation Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build the first public-beta documentation surface and release-facing repository documents defined by `docs/product-specs/public-beta-documentation.md`.

**Architecture:** Keep the existing agent/internal documentation system under `docs/` intact, and add a dedicated public documentation boundary under `docs/site/`. Treat root release-facing files as public GitHub entry points, while `AGENTS.md`, `docs/product-specs/`, `docs/design-docs/`, `docs/plans/`, `docs/research/`, and `docs/references/` remain internal authority or maintainer context.

**Tech Stack:** Python 3.13, `uv`, Poe, pytest, Ruff, mypy, Matplotlib-backed plotting, Markdown docs, Astro Starlight-compatible `docs/site/` content. Astro/Starlight package installation and GitHub Pages deployment are not part of this slice.

---

- Date: 2026-05-04
- Task: Public beta documentation implementation planning
- Status: `active`
- Risk class: `Tier B`
- Requestor: User
- Owner: Codex

## Planner Contract

- Goal: Define the exact implementation steps for the public beta documentation cleanup without changing runtime trading, execution, backtest, or research behavior.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/public-beta-documentation.md`
  - `docs/product-specs/research-ergonomics.md`
  - `docs/product-specs/backtest-mvp.md`
  - `docs/product-specs/backtest-plotting.md`
  - `docs/product-specs/parameter-exploration.md`
  - `docs/product-specs/order-sizing.md`
  - `docs/product-specs/order-reservation.md`
  - `docs/product-specs/stop-limit.md`
  - `docs/product-specs/data-ingestion.md`
  - `docs/design-docs/index.md`
  - `docs/design-docs/package-topology-and-naming.md`
  - `docs/design-docs/quantleet-architecture.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/DESIGN.md`
  - `docs/PLANS.md`
- Why these are governing:
  - `AGENTS.md` defines the planner/generator/evaluator loop and Tier A approval rule.
  - `public-beta-documentation.md` defines the user-facing documentation product contract.
  - Existing product specs define the shipped behavior that public docs must describe.
  - Design docs define the package topology and the boundary between public capability imports and internal implementation modules.
  - Repo docs and structure tests define the current verification surface.
- In-repo scope:
  - Create and update public documentation under `docs/site/`.
  - Update root release-facing docs: `README.md`, `CONTRIBUTING.md`, `SECURITY.md`, `CHANGELOG.md`, and `.github/PULL_REQUEST_TEMPLATE.md`.
  - Update `pyproject.toml` release metadata for the first beta posture.
  - Add focused structure/smoke tests that lock the public docs boundary, release-facing documents, metadata, and canonical examples.
  - Update existing tests only where they assert old README or metadata text that intentionally changes.
- Out-of-repo scope:
  - No external deployment, GitHub Pages setup, custom domain, package publishing, connector use, or `/tmp` clone changes.
- Tier A progression requested: `no`
- Approval record, if required: Not required. This slice changes docs, metadata, and tests only. It must not change `src/quantleet/trading`, `src/quantleet/execution`, or runtime behavior.
- Verification commands:
  - `git diff --check`
  - `uv run poe repo-check`
  - `uv run pytest tests/structure/docs tests/structure/repo tests/smoke/local -q`
  - `uv run poe verify` before final completion if the implementation also changes `pyproject.toml` metadata or docs examples in a way that can affect build/import behavior
- Success criteria:
  - Root release-facing docs exist and match the product spec roles.
  - `LICENSE` is neither created nor modified by this work.
  - `docs/site/` exists and contains the first public beta docs boundary.
  - Public docs do not link directly to internal workflow documents such as `AGENTS.md`, `docs/plans/`, `docs/product-specs/`, `docs/design-docs/`, or `docs/research/`.
  - README and public docs describe shipped behavior only.
  - README, `docs/site/index.md`, and `docs/site/quickstart.md` include the concise financial disclaimer.
  - Public docs include exactly three canonical examples: SMA crossover quickstart, orders and sizing, and parameter exploration.
  - Public docs use current public imports from `quantleet.data`, `quantleet.backtest`, and `quantleet.research`.
  - Public docs do not document nonexistent public symbols such as root-level `quantleet.BacktestEngine`, public `Bar`, or `TimeInForce` unless code first ships those symbols in a separate approved runtime/API slice.
  - Package metadata uses `0.1.0b1` and MIT license metadata while still leaving `LICENSE` untouched.
- Out of scope:
  - Runtime feature work.
  - Generated API reference tooling.
  - Astro package installation, Starlight config, build scripts, and GitHub Pages deployment.
  - GitHub issue templates.
  - i18n or multilingual docs.
  - Detailed public roadmap.
  - Moving internal docs out of `docs/`.

## Current Codebase Audit

### Repository Shape

- Root files currently present: `AGENTS.md`, `ARCHITECTURE.md`, `README.md`, `pyproject.toml`, `uv.lock`, `notebooks/`, `scripts/`, `src/`, `tests/`, and `docs/`.
- Root release-facing files currently absent: `CONTRIBUTING.md`, `SECURITY.md`, `CHANGELOG.md`, `.github/PULL_REQUEST_TEMPLATE.md`, and `LICENSE`.
- `LICENSE` is intentionally absent from the current worktree and must not be created by this slice.
- Existing internal docs directories under `docs/` include:
  - `docs/product-specs/`
  - `docs/design-docs/`
  - `docs/plans/`
  - `docs/research/`
  - `docs/references/`
  - `docs/exec-plans/`
  - `docs/generated/`
  - `docs/reviews/`
- `docs/site/` does not currently exist.

### Package And Tooling

- `pyproject.toml` currently declares:
  - `name = "quantleet"`
  - `version = "0.1.0"`
  - `description = "Quant research and trading infrastructure toolkit"`
  - `requires-python = ">=3.13"`
  - runtime dependencies: `ccxt`, `matplotlib`, `ta-lib`
  - dev tooling: `coverage`, `ipykernel`, `mypy`, `nbclient`, `nbformat`, `poethepoet`, `pytest`, `pytest-benchmark`, `ruff`
- Poe is the repo command surface. Required task names are enforced by `src/quantleet/_repo_tools.py` and tests under `tests/structure/repo/`.
- No Node, Astro, or Starlight package manifest currently exists. This plan therefore creates Starlight-compatible Markdown source structure only; it does not introduce a docs build.

### Current Public Import Truth

- Root package `quantleet` intentionally exports no public symbols.
- Public data imports:
  - `from quantleet.data import TimeBar, BarSeries`
  - `from quantleet.data import HistoricalDataSource`
  - `from quantleet.data import CCXTDataSource, CSVDataSource, DataFrameDataSource`
- Public backtest imports:
  - `from quantleet.backtest import BacktestEngine, CostConfig`
  - `from quantleet.backtest import BacktestResult, BacktestSummary, ExposureSummary`
  - reporting objects such as `BacktestReport`, `RunManifest`, `ExecutionAssumptions`, `ReturnMetrics`, `RiskMetrics`, `TradeMetrics`, `CostMetrics`, `ExposureMetrics`, `EquityPoint`, `ReportingFill`, and `ClosedTrade`
- Public research imports:
  - `from quantleet.research import Strategy, ParameterStudy, GridSearchResult, GridSearchRow, ta, qc`
- Current strategy order intake:
  - `Strategy.buy(...)` and `Strategy.sell(...)` accept `quantity`, `qty_percent`, `order_type`, `limit_price`, `stop_price`, and `tag`.
  - Supported `order_type` values are `market`, `limit`, `stop_market`, and `stop_limit`.
  - The current single-symbol workflow may omit `symbol`; explicit symbols must match the active series symbol.
- Current trading-domain internals:
  - `OrderSide` and `OrderType` are defined under `quantleet.trading.domain.intents`.
  - `Order` is defined under `quantleet.trading.domain.orders`.
  - No `TimeInForce` symbol exists anywhere in `src/quantleet`.
  - No public `Bar` class exists; the public historical bar type is `TimeBar`.
- Documentation implication:
  - The curated public API reference should document current public imports first.
  - Public examples need cost configuration; this slice exposes `CostConfig`
    through `quantleet.backtest` so public docs do not teach
    `quantleet.trading.domain` imports.
  - `Bar` and `TimeInForce` from the product spec are not documentable as current public API without a separate API/runtime change. This implementation slice must either omit them from user docs and record the spec/code mismatch, or first get a separate approved API-surface plan.

### Existing Test And Docs Constraints

- `scripts/check_docs.py` delegates to `quantleet._repo_tools.collect_doc_issues`.
- Required docs currently enforced by repo checks are:
  - `README.md`
  - `AGENTS.md`
  - `ARCHITECTURE.md`
  - `docs/DESIGN.md`
  - `docs/PLANS.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/design-docs/index.md`
  - `docs/product-specs/index.md`
- Existing structure tests assert current README text and will need intentional updates when README becomes public-facing.
- Existing smoke tests assert public imports and intentionally reject root-level `quantleet.BacktestEngine`.
- Existing quickstart reference at `docs/references/research-ergonomics-quickstart.md` contains reusable current examples for `BacktestEngine`, `Strategy`, `DataFrameDataSource`, `BarSeries`, `TimeBar`, `ta`, `qc`, `result.report`, and `result.plot()`.
- `.github/` currently has no checked-in files.

### Worktree State At Planning Time

- Branch: `dev`, tracking `origin/dev`.
- Existing uncommitted changes before this implementation plan:
  - modified: `docs/product-specs/index.md`
  - untracked: `docs/plans/2026-05-04-public-beta-documentation-product-spec.md`
  - untracked: `docs/product-specs/public-beta-documentation.md`
- This plan file is additive and must not revert those changes.

## Evaluator Acceptance Contract

- Evaluator owner: Codex evaluator pass
- Evaluator-owned done contract for this slice:
  - Confirm the implementation follows this plan and `docs/product-specs/public-beta-documentation.md`.
  - Confirm no runtime code behavior changed.
  - Confirm no Tier A source files changed.
  - Confirm `LICENSE` was not created or modified.
  - Confirm public docs do not expose internal workflow docs as public navigation.
  - Confirm examples use current public imports and do not rely on live exchange credentials or hidden local files.
  - Confirm package metadata and public docs do not claim a docs URL that is not available in this slice.
- Acceptance artifact location:
  - This plan's `## Evaluator Review` section.
- How the generator and evaluator agreed on done before execution:
  - The generator implements only the file changes and tests listed in this plan.
  - The evaluator checks the final diff against the task list, product spec, and verification output.
- Checks the evaluator will use:
  - Review `git diff --stat` and `git diff --name-only`.
  - Search for forbidden direct public links with `rg -n "AGENTS\\.md|docs/plans|docs/product-specs|docs/design-docs|docs/research" docs/site README.md`.
  - Search for unsupported public API claims with `rg -n "\\bTimeInForce\\b|from quantleet import BacktestEngine|\\bBar\\b" docs/site README.md`.
  - Run the verification commands listed in the Planner Contract.
- Auto-fail conditions:
  - `LICENSE` appears in the diff.
  - Any file under `src/quantleet/trading/` or `src/quantleet/execution/` changes.
  - Public docs link directly to internal workflow docs.
  - Public docs require live exchange access for quickstart success.
  - Public docs present live trading, paper trading, shorting, leverage, multi-symbol, or multi-timeframe as first-beta supported behavior.
  - Public docs make AI-led development the primary public product pitch.
  - Verification commands fail without a documented blocker.

## Generator Work Log

- Planned slice order:
  1. Add release-facing structure tests.
  2. Add public docs boundary tests.
  3. Add canonical example smoke tests.
  4. Update package metadata tests.
  5. Update `pyproject.toml` metadata.
  6. Rewrite `README.md` for public beta.
  7. Add root release-facing docs and PR template.
  8. Add `docs/site/` public docs.
  9. Update existing tests whose assertions intentionally changed.
  10. Run verification and evaluator review.
- Notes:
  - Use current smoke/integration examples as the source for executable snippets.
  - Keep public docs concise and avoid duplicating long internal product-spec detail.
  - Prefer links between public pages over repeated long explanations.
- Blockers or scope changes:
  - Product spec mentions `Bar` and `TimeInForce`, but the current codebase does not expose those symbols. The implementation should document `TimeBar` and omit `TimeInForce` as current public API unless the product spec is amended or a separate API slice is approved.

## Implementation Tasks

### Task 1: Add Release-Facing Document Structure Tests

**Files:**

- Modify: `tests/structure/repo/test_repository_entrypoint_docs.py`
- Modify: `tests/structure/repo/test_repo_check_contracts.py`

**Step 1: Add failing tests for root public docs**

Add tests that require:

- `CONTRIBUTING.md` exists and mentions setup, `uv run poe verify`, docs impact, public docs, AI-assisted contribution review, and human ownership.
- `SECURITY.md` exists and mentions vulnerability reporting, secrets, financial safety, and not using public issues for sensitive vulnerabilities.
- `CHANGELOG.md` exists and contains an unreleased section and `0.1.0b1`.
- `.github/PULL_REQUEST_TEMPLATE.md` exists and asks for summary, change type, docs impact, verification evidence, changelog/release impact, AI-assisted review, and human ownership.
- `LICENSE` is not required by the test because the user owns its creation.

Example test shape:

```python
def test_release_facing_repository_docs_exist() -> None:
    required = [
        "CONTRIBUTING.md",
        "SECURITY.md",
        "CHANGELOG.md",
        ".github/PULL_REQUEST_TEMPLATE.md",
    ]
    for relative_path in required:
        path = ROOT / relative_path
        assert path.exists(), f"missing {relative_path}"
        assert path.read_text(encoding="utf-8").strip()
```

**Step 2: Run tests and verify failure**

Run:

```bash
uv run pytest tests/structure/repo/test_repository_entrypoint_docs.py -q
```

Expected:

- Fails because the release-facing files do not exist yet.

### Task 2: Add Public Docs Boundary Tests

**Files:**

- Create: `tests/structure/docs/test_public_beta_docs.py`

**Step 1: Add failing tests for `docs/site/`**

Require these public docs files:

```text
docs/site/index.md
docs/site/installation.md
docs/site/quickstart.md
docs/site/examples.md
docs/site/getting-started/index.md
docs/site/guides/backtesting.md
docs/site/guides/strategy-authoring.md
docs/site/guides/data-sources.md
docs/site/guides/orders-and-sizing.md
docs/site/guides/parameter-exploration.md
docs/site/concepts/beta-scope.md
docs/site/reference/public-api.md
```

Require public docs to:

- include the three-part financial disclaimer in `index.md` and `quickstart.md`
- mention English-only public docs implicitly by only creating English pages
- include no direct links to internal workflow documents
- not mention unsupported scope as supported behavior
- not claim a live docs URL or GitHub Pages deployment

Forbidden public docs link/text patterns:

```python
FORBIDDEN_INTERNAL_PUBLIC_LINKS = (
    "AGENTS.md",
    "docs/plans",
    "docs/product-specs",
    "docs/design-docs",
    "docs/research",
    "../plans",
    "../product-specs",
    "../design-docs",
    "../research",
)
```

**Step 2: Run tests and verify failure**

Run:

```bash
uv run pytest tests/structure/docs/test_public_beta_docs.py -q
```

Expected:

- Fails because `docs/site/` does not exist yet.

### Task 3: Add Canonical Example Smoke Tests

**Files:**

- Create: `tests/smoke/local/test_public_beta_examples.py`

**Step 1: Write executable tests for the three public examples**

Use code that mirrors the docs and only imports public capability surfaces:

```python
from quantleet.backtest import BacktestEngine, CostConfig
from quantleet.data import BarSeries, DataFrameDataSource, TimeBar
from quantleet.research import ParameterStudy, Strategy, qc, ta
```

Test 1: SMA crossover quickstart.

- Use in-memory `DataFrameDataSource`.
- Run `BacktestEngine(...).run(source=..., strategy=...)`.
- Assert `result.report.run.run_label == "sma-cross"`.
- Assert `result.plot()` returns a Matplotlib `Figure`.

Test 2: orders and sizing.

- Use `BarSeries` with deterministic bars.
- Include strategies or one combined strategy that exercises:
  - `quantity=...`
  - `qty_percent=...`
  - `order_type="market"`
  - `order_type="limit"`
  - `order_type="stop_market"`
  - `order_type="stop_limit"`
- Assert fills or order events exist and final position state is inspectable.

Test 3: parameter exploration.

- Use `ParameterStudy(...).grid_search(...)`.
- Use parameters `{"fast": [2, 3], "slow": [3, 4]}` or another tiny deterministic grid.
- Use `constraint=lambda parameters: parameters["fast"] < parameters["slow"]`.
- Use `objective=("returns.total_return", "max")`.
- Assert `candidate_count`, `rejected_count`, `successful_count`, `best().backtest`, and `to_records()`.

**Step 2: Run tests and verify failure/pass state**

Run:

```bash
uv run pytest tests/smoke/local/test_public_beta_examples.py -q
```

Expected:

- Tests may pass immediately if written against current APIs. If they fail, adjust only the tests or docs example code to match shipped behavior; do not change runtime code in this slice.

### Task 4: Update Package Metadata Tests

**Files:**

- Modify: `tests/structure/repo/test_poe_task_contracts.py`
- Modify: `tests/structure/repo/test_repo_check_contracts.py`
- Create or modify: `tests/structure/repo/test_public_package_metadata.py`

**Step 1: Add metadata assertions**

Assert `pyproject.toml` contains:

- version `0.1.0b1`
- MIT license metadata
- Python 3.13 support
- project URLs for homepage, repository, issues, and changelog
- no documentation URL until GitHub Pages deployment exists, or a clearly local/non-published docs pointer if the final implementation chooses one
- keywords including quant, backtesting, research, trading, finance
- classifiers for Python 3, Python 3.13, MIT license, typed package, beta/development status, and financial/scientific topic if appropriate

**Step 2: Run metadata tests and verify failure**

Run:

```bash
uv run pytest tests/structure/repo/test_public_package_metadata.py tests/structure/repo/test_poe_task_contracts.py tests/structure/repo/test_repo_check_contracts.py -q
```

Expected:

- Fails until `pyproject.toml` is updated from `0.1.0` to `0.1.0b1` and metadata fields are added.

### Task 5: Update `pyproject.toml` Public Metadata

**Files:**

- Modify: `pyproject.toml`

**Step 1: Update project metadata**

Change:

```toml
version = "0.1.0"
description = "Quant research and trading infrastructure toolkit"
```

To:

```toml
version = "0.1.0b1"
description = "Single-symbol Python backtesting and quant research tooling"
license = "MIT"
keywords = ["quant", "backtesting", "research", "trading", "finance"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Intended Audience :: Financial and Insurance Industry",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.13",
    "Typing :: Typed",
]

[project.urls]
Homepage = "https://github.com/nbsp1221/quantleet"
Repository = "https://github.com/nbsp1221/quantleet"
Issues = "https://github.com/nbsp1221/quantleet/issues"
Changelog = "https://github.com/nbsp1221/quantleet/blob/dev/CHANGELOG.md"
```

Do not add a hosted documentation URL in this slice unless the actual deployment exists.

**Step 2: Run metadata tests**

Run:

```bash
uv run pytest tests/structure/repo/test_public_package_metadata.py tests/structure/repo/test_poe_task_contracts.py tests/structure/repo/test_repo_check_contracts.py -q
```

Expected:

- Pass after updating fixtures that intentionally expected `0.1.0`.

### Task 6: Rewrite `README.md` For Public Beta

**Files:**

- Modify: `README.md`
- Modify: `tests/structure/repo/test_repository_entrypoint_docs.py`

**Step 1: Replace internal-heavy README with public landing README**

Use this structure:

```markdown
# Quantleet

Quantleet is a Python backtesting and quant research toolkit focused on a
polished first-beta single-symbol historical backtesting workflow.

## Beta Scope

## Installation

## Quickstart

## Result Inspection

## Examples

## Documentation

## Contributing

## Security

## Financial Disclaimer

## License
```

The README must:

- keep `## Setup` or update tests/repo checks if the canonical public heading becomes `## Installation`
- mention Python 3.13
- show `uv` install/setup for local repo use and package-user installation guidance
- include a compact SMA crossover example with `BacktestEngine`, `DataFrameDataSource`, `Strategy`, `ta`, `qc`, `result.report`, and `result.plot()`
- include the financial disclaimer
- link to `docs/site/` pages, not internal product specs/plans
- mention MIT license while not creating `LICENSE`
- mention contribution and security docs
- avoid internal agent workflow details

**Step 2: Update README tests**

Existing `test_readme_current_scope_mentions_implemented_backtest_research_and_data_surfaces` is tied to the old internal README. Replace it with public README expectations:

- public positioning
- beta scope
- installation/setup
- quickstart
- three canonical examples
- disclaimer
- docs/contributing/security/changelog links
- no direct internal workflow docs links
- no root-level public import claims

**Step 3: Run README tests**

Run:

```bash
uv run pytest tests/structure/repo/test_repository_entrypoint_docs.py -q
```

Expected:

- Pass after README and tests are aligned.

### Task 7: Add Release-Facing Repository Docs

**Files:**

- Create: `CONTRIBUTING.md`
- Create: `SECURITY.md`
- Create: `CHANGELOG.md`
- Create: `.github/PULL_REQUEST_TEMPLATE.md`

**Step 1: Create `CONTRIBUTING.md`**

Include:

- project scope and beta posture
- contributor setup with `uv sync`
- verification commands:
  - `uv run poe verify`
  - `uv run poe repo-check`
  - targeted pytest examples
- docs contribution rule:
  - public user docs live under `docs/site/`
  - internal planning/product/design docs stay under their existing directories
- issue guidance until issue templates are added:
  - bugs need environment, reproduction, expected/actual behavior
  - feature requests need user problem and scope
  - docs issues need page path and proposed correction
- PR guidance:
  - summary
  - tests
  - docs impact
  - changelog impact
  - AI-assisted output must be reviewed line by line by the human contributor
  - human contributor owns and stands behind the change
- Tier A note:
  - trading/execution changes require stricter review and approval per repo policy

**Step 2: Create `SECURITY.md`**

Include:

- report suspected vulnerabilities privately through GitHub Security Advisories or maintainer contact once configured
- do not file secrets, credentials, exploit details, or fund-moving risks in public issues
- never commit API keys or exchange credentials
- financial safety boundary:
  - Quantleet is research/software tooling
  - backtests are not execution guarantees
  - users own data assumptions and trading decisions
- supported version initially `0.1.0b1`

**Step 3: Create `CHANGELOG.md`**

Use Keep a Changelog style:

```markdown
# Changelog

## Unreleased

## 0.1.0b1 - 2026-05-04

### Added

### Changed

### Documentation
```

Do not claim publication has happened unless the release actually exists.

**Step 4: Create PR template**

The PR template must include checkboxes for:

- summary
- change type
- linked issue when applicable
- docs impact
- verification evidence
- release/changelog impact
- AI-assisted contribution disclosure
- human ownership confirmation

**Step 5: Run release-doc tests**

Run:

```bash
uv run pytest tests/structure/repo/test_repository_entrypoint_docs.py -q
```

Expected:

- Pass.

### Task 8: Add `docs/site/` Public Docs

**Files:**

- Create: `docs/site/index.md`
- Create: `docs/site/installation.md`
- Create: `docs/site/quickstart.md`
- Create: `docs/site/examples.md`
- Create: `docs/site/getting-started/index.md`
- Create: `docs/site/guides/backtesting.md`
- Create: `docs/site/guides/strategy-authoring.md`
- Create: `docs/site/guides/data-sources.md`
- Create: `docs/site/guides/orders-and-sizing.md`
- Create: `docs/site/guides/parameter-exploration.md`
- Create: `docs/site/concepts/beta-scope.md`
- Create: `docs/site/reference/public-api.md`

**Step 1: Write `docs/site/index.md`**

Include:

- public product overview
- first beta scope
- links to installation, quickstart, examples, guides, beta scope, and API reference
- concise financial disclaimer
- no direct links to internal workflow docs

**Step 2: Write `docs/site/installation.md`**

Include:

- Python 3.13 requirement
- package-user install guidance for first beta
- local contributor setup pointer to `CONTRIBUTING.md`
- note that live exchange credentials are not required for quickstart

**Step 3: Write `docs/site/quickstart.md`**

Include:

- executable in-memory SMA crossover quickstart
- current public imports only:

```python
from quantleet.backtest import BacktestEngine, CostConfig
from quantleet.data import DataFrameDataSource
from quantleet.research import Strategy, qc, ta
```

- `result.report`
- `result.plot()`
- concise financial disclaimer

**Step 4: Write `docs/site/examples.md`**

List exactly three canonical examples:

1. SMA crossover quickstart
2. Orders and sizing
3. Parameter exploration

Do not add reporting/plotting as a fourth canonical example.

**Step 5: Write guides**

Create focused pages:

- `guides/backtesting.md`: `BacktestEngine.run(source=...)` and `BacktestEngine.run(bars=...)`
- `guides/strategy-authoring.md`: `Strategy.init`, `Strategy.on_bar`, `self.data`, `self.position`, `buy`, `sell`, indicator warmup, `qc.is_na`
- `guides/data-sources.md`: `DataFrameDataSource`, `CSVDataSource`, `CCXTDataSource`, `BarSeries`, `TimeBar`; keep CCXT historical flow optional and not required for quickstart
- `guides/orders-and-sizing.md`: fixed quantity, `qty_percent`, market, limit, stop-market, stop-limit, reservation/fills/positions inspection
- `guides/parameter-exploration.md`: `ParameterStudy(...).grid_search(...)`, small SMA grid, `fast < slow` constraint, objective, records, selected/best run

**Step 6: Write `concepts/beta-scope.md`**

State supported first beta:

- single-symbol
- single-timeframe
- historical OHLCV backtesting
- long-or-flat current research/backtest flow
- market, limit, stop-market, stop-limit orders
- fixed quantity and `qty_percent`
- report, plot, and finite grid parameter exploration

State unsupported:

- live trading
- paper trading
- shorting
- leverage/margin
- multi-symbol portfolios
- multi-timeframe strategies
- optimizer/trading recommendation claims

**Step 7: Write `reference/public-api.md`**

Document current public surfaces only:

- `quantleet.data.TimeBar`
- `quantleet.data.BarSeries`
- `quantleet.data.DataFrameDataSource`
- `quantleet.data.CSVDataSource`
- `quantleet.data.CCXTDataSource`
- `quantleet.backtest.BacktestEngine`
- `quantleet.backtest.BacktestResult`
- `BacktestResult.report`
- `BacktestResult.plot()`
- `quantleet.research.Strategy`
- `Strategy.buy(...)`
- `Strategy.sell(...)`
- `quantleet.research.ParameterStudy`
- `ParameterStudy.grid_search(...)`
- `quantleet.research.ta`
- `quantleet.research.qc`

Record that lower-level trading-domain objects are not the primary beta import surface. Do not document `TimeInForce` as public API.

**Step 8: Run public docs tests**

Run:

```bash
uv run pytest tests/structure/docs/test_public_beta_docs.py -q
```

Expected:

- Pass.

### Task 9: Add Public Docs Repo-Check Coverage

**Files:**

- Modify: `src/quantleet/_repo_tools.py`
- Modify: `tests/structure/repo/test_repo_check_contracts.py`

**Step 1: Extend doc checks narrowly**

Add repo-check validation for:

- required release-facing docs except `LICENSE`
- required `docs/site/` entry docs
- forbidden public-doc internal links
- financial disclaimer presence in README, `docs/site/index.md`, and `docs/site/quickstart.md`

Keep checks narrow and string-based. Do not add a full Markdown parser or docs build requirement in this slice.

**Step 2: Update minimal repo fixtures**

Update `write_minimal_repo_docs(...)` in `tests/structure/repo/test_poe_task_contracts.py` so repo-check contract tests still represent the minimum accepted repository shape.

**Step 3: Run repo-check tests**

Run:

```bash
uv run pytest tests/structure/repo/test_repo_check_contracts.py tests/structure/repo/test_poe_task_contracts.py -q
```

Expected:

- Pass.

### Task 10: Update Existing Reference Docs Only Where Needed

**Files:**

- Optional modify: `docs/references/index.md`
- Optional modify: `docs/references/research-ergonomics-quickstart.md`
- Optional modify: `docs/RELIABILITY.md`

**Step 1: Avoid broad internal rewrite**

Do not move internal docs. Only update internal reference docs if:

- they contradict the new public docs
- existing structure tests require wording updates after README changes
- they need to point maintainers to `docs/site/` as the public docs boundary

**Step 2: Run existing docs tests**

Run:

```bash
uv run pytest tests/structure/docs -q
```

Expected:

- Pass.

### Task 11: Full Verification And Evaluator Review

**Files:**

- Modify: this plan's `## Evaluator Review` section

**Step 1: Run formatting and targeted verification**

Run:

```bash
git diff --check
uv run poe repo-check
uv run pytest tests/structure/docs tests/structure/repo tests/smoke/local -q
```

Expected:

- `git diff --check` emits no output.
- `repo-check` prints `repository checks passed`.
- Targeted pytest passes.

**Step 2: Run full verification**

Run:

```bash
uv run poe verify
```

Expected:

- Full default verification passes.

If `uv run poe verify` fails because notebooks or environment dependencies unrelated to this docs slice are unavailable, record the exact failure and keep targeted verification as the hard evidence for this slice.

**Step 3: Evaluator review**

Update `## Evaluator Review` with:

- findings first
- verification evidence
- final disposition
- any residual risk

## Evaluator Review

- Findings:
  - GPT-5.5 medium third-party review found a blocking public-docs API issue:
    README and `docs/site` initially taught users to import `CostConfig` from
    `quantleet.trading.domain.costs`. Fixed by exposing `CostConfig` from
    `quantleet.backtest`, updating README, `docs/site`, smoke tests, and built
    artifact import tests to use `from quantleet.backtest import BacktestEngine,
    CostConfig`.
  - GPT-5.5 medium third-party review found installation docs lacked a concrete
    package install command. Fixed by adding `uv add quantleet==0.1.0b1` and
    `python -m pip install quantleet==0.1.0b1` guidance.
  - GPT-5.5 medium third-party review found this evaluator artifact was still
    pending. Fixed by recording review findings and verification evidence here.
  - GPT-5.5 medium second-pass review found no remaining blocking issues.
  - Residual risk: Astro Starlight package setup and GitHub Pages deployment
    remain out of scope for this slice. This implementation creates
    Starlight-compatible Markdown source under `docs/site/`, not a built docs
    site.
  - No `LICENSE` file was created or modified.
  - No files under `src/quantleet/trading/` or `src/quantleet/execution/`
    were changed.
- Verification evidence:
  - `git diff --check` passed with no output before third-party review.
  - `uv run poe repo-check` passed with `repository checks passed` before
    third-party review.
  - `uv run pytest tests/structure/docs tests/structure/repo tests/smoke/local
    -q` passed with `89 passed in 0.65s` before third-party review.
  - `uv run poe verify` passed before third-party review: Ruff passed, mypy
    passed, pytest reported `625 passed, 4 skipped`, coverage policy passed,
    build produced `quantleet-0.1.0b1`, repo-check passed, and all tracked
    notebooks validated.
  - Post-review targeted check `uv run pytest
    tests/smoke/local/test_public_imports.py
    tests/integration/commands/test_built_artifact_imports.py
    tests/smoke/local/test_public_beta_examples.py
    tests/smoke/local/test_backtest_result_reporting_quickstart.py
    tests/structure/docs/test_public_beta_docs.py
    tests/structure/repo/test_repository_entrypoint_docs.py -q` passed with
    `23 passed in 1.08s`.
  - Post-review `uv run ruff check .` passed with `All checks passed!`.
  - Final post-review `git diff --check` passed with no output.
  - Final post-review `uv run poe repo-check` passed with `repository checks
    passed`.
  - Final post-review targeted check `uv run pytest tests/structure/docs
    tests/structure/repo tests/smoke/local
    tests/integration/commands/test_built_artifact_imports.py -q` passed with
    `90 passed in 1.19s`.
  - Final post-review `uv run poe verify` passed: Ruff passed, mypy passed,
    pytest reported `625 passed, 4 skipped`, coverage policy passed, build
    produced `quantleet-0.1.0b1`, repo-check passed, and all tracked notebooks
    validated.
  - GPT-5.5 medium second-pass review also ran `git diff --check`, targeted
    docs/smoke/metadata tests, `uv build`, README quickstart execution,
    repo-check, Ruff, mypy, and `uv run poe verify`; all passed.
- Final disposition: Complete for this documentation implementation slice.
