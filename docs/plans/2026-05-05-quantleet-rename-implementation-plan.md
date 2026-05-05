# Quantleet Rename Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to
> implement this plan task-by-task.

**Goal:** Rename the public project, installable distribution, import package,
and GitHub repository to Quantleet/`quantleet` before the first public beta
release.

**Architecture:** Treat this as a pre-release hard rename, not a compatibility
migration. Move the single installable engine package to `src/quantleet`, update
all in-repo imports and docs to the new package name, and do not add any old-name
compatibility shim. All in-repo tracked text, docs, tests, notebooks, and tooling
must teach and verify Quantleet only. Do not preserve a rename narrative or
compatibility story.

**Tech Stack:** Python 3.13, uv, uv-build, poe, pytest, Ruff, mypy, nbclient,
repo-local verification scripts.

---

- Date: 2026-05-05
- Task: Quantleet rename
- Status: `active`
- Risk class: `Tier B`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal:
  - Rename the package and public project surface to Quantleet before any public
    PyPI release depends on the old name.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/public-beta-documentation.md`
  - `docs/design-docs/index.md`
  - `docs/design-docs/quantleet-architecture.md`
  - `docs/design-docs/package-topology-and-naming.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/DESIGN.md`
  - `docs/PLANS.md`
- Why these are governing:
  - The change affects package topology, public imports, package metadata,
    release-facing docs, public beta docs, and repo-local verification.
  - `docs/design-docs/package-topology-and-naming.md` defines the installable
    engine package root; this plan changes that standing topology to
    `src/quantleet`.
  - `docs/product-specs/public-beta-documentation.md` controls the public docs
    and public import examples that must teach `quantleet`.
- In-repo scope:
  - Rename the source package directory to `src/quantleet`.
  - Update Python imports in `src/`, `tests/`, `scripts/`, and notebooks.
  - Update package metadata in `pyproject.toml` and `uv.lock`.
  - Update repo-local checks and structure tests that hard-code the old package
    root.
  - Update current governing docs, release-facing docs, public docs, and active
    product specs to use Quantleet.
  - Update notebook source cells so `uv run poe notebook-validate` executes
    against `quantleet`.
  - Remove stale build artifacts before rebuilding.
  - Rename the GitHub repository to `nbsp1221/quantleet` at the final step.
  - Update the local `origin` URL after the GitHub repository rename.
- Out-of-repo scope:
  - DNS or docs hosting changes for `quantleet.com`.
  - Any external branding assets.
  - PyPI/TestPyPI upload, name reservation, or release publication.
- Tier A progression requested: `no`
- Approval record, if required:
  - Not required for this plan because runtime semantics under `trading` and
    `execution` are not allowed to change.
  - Mechanical import-path edits may touch files under `src/quantleet/trading`
    after the directory move, but the generator must not alter order,
    execution, sizing, matching, or state behavior.
- Verification commands:
  - `git status -sb`
  - Run a stale-name sweep across tracked repository surfaces.
  - `uv run ruff check .`
  - `uv run mypy src`
  - `uv run pytest tests/structure -q`
  - `uv run pytest tests/smoke/local -q`
  - `uv run pytest tests/integration/commands -q`
  - `uv run poe repo-check`
  - `uv run poe verify`
- Success criteria:
  - `import quantleet` works from the source checkout and from the built wheel.
  - Documented public imports use `quantleet.data`, `quantleet.backtest`, and
    `quantleet.research`.
  - The built wheel is named `quantleet-0.1.0b1-...whl`.
  - Tracked repository files no longer contain old-name text.
  - No compatibility shim or transition narrative is added.
  - GitHub repository name is `nbsp1221/quantleet`, and local `origin` points at
    it.
  - `uv run poe verify` passes.
- Out of scope:
  - Behavioral changes to backtest, research, trading, execution, data
    ingestion, integrations, plotting, or parameter exploration.
  - Creating or modifying `LICENSE`; the user will create it.

## Current Codebase Findings

- The current branch is `main` and the tracked worktree was clean before this
  plan was added.
- `pyproject.toml` must declare:
  - `[project].name = "quantleet"`
  - `packages = ["quantleet"]`
  - `tool.mypy.packages = ["quantleet"]`
  - `tool.coverage.report.include = ["src/quantleet/*"]`
  - project URLs under `https://github.com/nbsp1221/quantleet`
  - changelog URL pointing at `blob/main/CHANGELOG.md`
- The installable package root must be `src/quantleet`.
- Current hard-coded reference counts found during planning:
  - `src`: 30 files, 109 occurrences
  - `tests`: 93 files, 459 occurrences
  - `docs/site`: 8 files, 28 occurrences
  - `docs/product-specs`: 13 files, 112 occurrences
  - `docs/design-docs`: 11 files, 87 occurrences
  - `docs/references`: 3 files, 9 occurrences
  - `docs/research`: 13 files, 115 occurrences
  - `docs/plans`: 110 files, 1301 occurrences
  - `docs/exec-plans`: 10 files, 142 occurrences
  - root/config docs: `README.md` 8, `ARCHITECTURE.md` 7, `AGENTS.md` 1,
    `CONTRIBUTING.md` 1, `SECURITY.md` 1, `pyproject.toml` 7, `uv.lock` 1
- Current structure and metadata tests contain package-name assumptions,
  including:
  - `tests/structure/architecture/test_capability_package_roots.py`
  - `tests/structure/architecture/test_backtest_mvp_slice1.py`
  - `tests/structure/architecture/test_backtest_plotting_boundaries.py`
  - `tests/structure/architecture/test_backtest_runtime_hardening_boundaries.py`
  - `tests/structure/architecture/test_ccxt_integration_ownership.py`
  - `tests/structure/architecture/test_domain_boundaries.py`
  - `tests/structure/architecture/test_local_package_topology.py`
  - `tests/structure/architecture/test_parameter_exploration_boundaries.py`
  - `tests/structure/docs/test_public_beta_docs.py`
  - `tests/structure/repo/test_indicator_refactor_contracts.py`
  - `tests/structure/repo/test_public_package_metadata.py`
  - `tests/structure/repo/test_repo_check_contracts.py`
  - `tests/structure/repo/test_coverage_harness.py`
  - `tests/structure/repo/test_runtime_verification_lane.py`
  - `tests/integration/commands/test_built_artifact_imports.py`
  - `tests/smoke/local/test_public_imports.py`
- Repo-local scripts import package internals:
  - `scripts/check_architecture.py`
  - `scripts/check_docs.py`
  - `scripts/live_smoke.py`
  - `scripts/notebook_validate.py`
  - `scripts/repo_check.py`
- `src/quantleet/_repo_tools.py` embeds package-root assumptions for:
  - import-boundary parsing
  - architecture checks
  - package topology checks
  - CCXT import checks
  - public docs checks
- All tracked notebooks must import `quantleet` in code cells after cleanup.
- `dist/` currently contains ignored old build artifacts and must be cleaned
  before validating wheel names.

## Rename Policy

- Use `Quantleet` for human-facing title case.
- Use `quantleet` for package, distribution, import path, directory name, and
  command/test strings.
- Do not use `QuantLeet` unless a future branding decision explicitly changes
  casing.
- Do not keep old-name compatibility aliases in source, wheel, docs, or tests.
- Remove old-name text from tracked repository files, including historical
  plans, exec plans, and research docs.
- Do not add text saying Quantleet was renamed from the old project name.

## Evaluator Acceptance Contract

- Evaluator owner:
  - Codex evaluator pass after implementation.
- Evaluator-owned done contract for this slice:
  - The diff is a mechanical rename plus docs/metadata alignment only.
  - No trading or execution behavior changes are present.
  - Public docs, examples, package metadata, and built artifacts consistently
    use Quantleet/`quantleet`.
  - GitHub repository and local `origin` use `nbsp1221/quantleet`.
  - Verification evidence is fresh and comes from the final workspace state.
- Acceptance artifact location:
  - This plan's `## Evaluator Review` section.
- How the generator and evaluator agreed on done before execution:
  - The generator must follow the task list below and record any scope change
    in `## Generator Work Log` before editing outside listed files or classes of
    files.
- Checks the evaluator will use:
  - Review `git diff --stat` and `git diff --name-status` for unexpected
    behavioral files.
  - Run the verification commands listed in the planner contract.
  - Inspect wheel metadata and installed package import behavior.
  - Search current public/governing surfaces for old active-name references.
- Auto-fail conditions:
  - Any `quantleet` compatibility package, shim, or transition narrative is added.
  - Any runtime logic changes beyond import paths are made under `trading` or
    `execution`.
  - `pyproject.toml` still names the distribution `quantleet`.
  - Built wheel fails to import `quantleet`.
  - Public docs still instruct users to install or import `quantleet`.
  - `uv run poe verify` is not run or does not pass.
  - A commit is created.

## Generator Work Log

- Planned slice order:
  1. Add failing/updated tests for package metadata and import surface.
  2. Move the source package root and update Python imports.
  3. Update packaging, lockfile, coverage, mypy, and repo tooling.
  4. Update current docs and notebooks.
  5. Clean build artifacts and verify wheel behavior.
  6. Run full verification.
  7. Rename the GitHub repository and update local `origin` URL.
  8. Record evaluator review.
- Notes:
  - Do not create `LICENSE`.
  - Do not commit this work.
  - Rename the GitHub repository at the final step and update local `origin` URL.
- Blockers or scope changes:
  - None yet.

## Implementation Tasks

### Task 1: Update Metadata And Import-Surface Tests First

**Files:**
- Modify: `tests/structure/repo/test_public_package_metadata.py`
- Modify: `tests/integration/commands/test_built_artifact_imports.py`
- Modify: `tests/smoke/local/test_public_imports.py`
- Modify: `tests/structure/architecture/test_capability_package_roots.py`

**Step 1: Update metadata expectations**

In `tests/structure/repo/test_public_package_metadata.py`, change assertions to:

```python
assert project["name"] == "quantleet"
assert urls["Homepage"] == "https://github.com/nbsp1221/quantleet"
assert urls["Repository"] == "https://github.com/nbsp1221/quantleet"
assert urls["Issues"] == "https://github.com/nbsp1221/quantleet/issues"
assert urls["Changelog"] == "https://github.com/nbsp1221/quantleet/blob/main/CHANGELOG.md"
```

Keep the version, Python, license, keywords, classifiers, and no-Documentation
URL assertions unless implementation changes require a deliberate plan update.

**Step 2: Update built wheel import contract**

In `tests/integration/commands/test_built_artifact_imports.py`:

- Change wheel glob from `quantleet-*.whl` to `quantleet-*.whl`.
- Change the assertion message to mention a `quantleet` wheel.
- Change `import quantleet` to `import quantleet`.
- Change all `quantleet.*` module strings to `quantleet.*`.

**Step 3: Update local public import smoke tests**

In `tests/smoke/local/test_public_imports.py`:

- Change `import quantleet` to `import quantleet`.
- Change all `importlib.import_module("quantleet...")` calls to
  `importlib.import_module("quantleet...")`.
- Change old forbidden module strings from `quantleet...` to `quantleet...`.

**Step 4: Update package root structure expectations**

In `tests/structure/architecture/test_capability_package_roots.py`, change:

```python
Path("src/quantleet/backtest/__init__.py")
```

to:

```python
Path("src/quantleet/backtest/__init__.py")
```

for each expected capability package root.

**Step 5: Run targeted tests to confirm failure before implementation**

Run:

```bash
uv run pytest \
  tests/structure/repo/test_public_package_metadata.py \
  tests/integration/commands/test_built_artifact_imports.py \
  tests/smoke/local/test_public_imports.py \
  tests/structure/architecture/test_capability_package_roots.py \
  -q
```

Expected before implementation:

- Failures because metadata, wheel names, package root, and imports have not all
  been aligned yet.

### Task 2: Move Source Package Root And Update Code Imports

**Files:**
- Move: existing source package root to `src/quantleet/`
- Modify: every moved Python file under `src/quantleet/`
- Modify: `scripts/check_architecture.py`
- Modify: `scripts/check_docs.py`
- Modify: `scripts/live_smoke.py`
- Modify: `scripts/notebook_validate.py`
- Modify: `scripts/repo_check.py`

**Step 1: Move the package directory**

Use `git mv` so the existing source package root becomes `src/quantleet`.
Do not leave an old-name package root behind.

**Step 2: Update source imports**

Replace imports in moved source files:

```python
from quantleet...
import quantleet...
```

with:

```python
from quantleet...
import quantleet...
```

This includes files under:

- `src/quantleet/backtest/`
- `src/quantleet/data/`
- `src/quantleet/integrations/`
- `src/quantleet/research/`
- `src/quantleet/trading/`
- `src/quantleet/_repo_tools.py`
- `src/quantleet/_notebook_tools.py`

Do not change business logic while editing imports.

**Step 3: Update repo-local scripts**

Change script imports from:

```python
from quantleet._repo_tools import ...
from quantleet._notebook_tools import ...
```

to:

```python
from quantleet._repo_tools import ...
from quantleet._notebook_tools import ...
```

**Step 4: Run formatter/linter import checks**

Run:

```bash
uv run ruff check src scripts --fix
uv run ruff format src scripts
uv run ruff check src scripts
```

Expected:

- Ruff reports no remaining import-order or lint issues in source/scripts.

### Task 3: Update Packaging, Lockfile, Coverage, Mypy, And Repo Tools

**Files:**
- Modify: `pyproject.toml`
- Modify: `uv.lock`
- Modify: `src/quantleet/_repo_tools.py`
- Modify: `scripts/coverage_check.py`
- Modify: `tests/structure/repo/test_coverage_harness.py`
- Modify: `tests/structure/repo/test_repo_check_contracts.py`
- Modify: `tests/structure/repo/test_runtime_verification_lane.py`
- Modify: `tests/structure/repo/test_poe_task_contracts.py` if it contains
  package-name assumptions

**Step 1: Update `pyproject.toml`**

Change:

```toml
name = "quantleet"
```

to:

```toml
name = "quantleet"
```

Change project URLs to:

```toml
Homepage = "https://github.com/nbsp1221/quantleet"
Repository = "https://github.com/nbsp1221/quantleet"
Issues = "https://github.com/nbsp1221/quantleet/issues"
Changelog = "https://github.com/nbsp1221/quantleet/blob/main/CHANGELOG.md"
```

Change mypy and coverage settings:

```toml
packages = ["quantleet"]
include = ["src/quantleet/*"]
```

The exact keys are:

- `[tool.mypy].packages`
- `[tool.coverage.report].include`

Preserve `version = "0.1.0b1"` and `license = "MIT"`.

**Step 2: Update `uv.lock`**

Run:

```bash
uv lock
```

Expected:

- The root package entry is `name = "quantleet"`.
- Dependency versions should not churn without reason.

**Step 3: Update repo tools**

In `src/quantleet/_repo_tools.py`, ensure all hard-coded package assumptions use
`quantleet`, `src/quantleet`, and `quantleet.*` sample imports.

**Step 4: Update coverage helper**

In `scripts/coverage_check.py`, change:

```python
INCLUDE_PATTERN = "src/quantleet/*"
TRADING_DOMAIN_PREFIX = "src/quantleet/trading/domain/"
```

to:

```python
INCLUDE_PATTERN = "src/quantleet/*"
TRADING_DOMAIN_PREFIX = "src/quantleet/trading/domain/"
```

**Step 5: Update structure tests for tooling contracts**

Update temp package roots and expected error messages in:

- `tests/structure/repo/test_coverage_harness.py`
- `tests/structure/repo/test_repo_check_contracts.py`
- `tests/structure/repo/test_runtime_verification_lane.py`

When tests create fake files under `tmp_path / "src" / "quantleet"`, move the
fixture path to `tmp_path / "src" / "quantleet"` and update embedded import
strings accordingly.

**Step 6: Run targeted repo tooling tests**

Run:

```bash
uv run pytest tests/structure/repo -q
uv run poe repo-check
```

Expected:

- Structure repo tests pass.
- Repo check passes with Quantleet package root and public docs.

### Task 4: Update Test Suite Imports And Architecture Fixtures

**Files:**
- Modify: all Python files under `tests/` that import or mention `quantleet`

**Step 1: Update Python imports**

Replace all test imports:

```python
from quantleet...
import quantleet...
```

with:

```python
from quantleet...
import quantleet...
```

**Step 2: Update architecture fixture strings**

Update embedded strings and path expectations in architecture tests so package
paths and forbidden legacy-module examples use `src/quantleet` and
`quantleet.*`. Keep the same boundary intent; this task is a rename, not a
behavior change.

**Step 3: Run architecture, unit, integration, and smoke tests**

Run:

```bash
uv run pytest tests/structure/architecture -q
uv run pytest tests/unit -q
uv run pytest tests/integration -q
uv run pytest tests/smoke/local -q
```

Expected:

- All selected lanes pass.
- No runtime behavior assertions change except import-path expectations.

### Task 5: Update Current Docs, Public Docs, And Notebooks

**Files:**
- Modify: `README.md`
- Modify: `ARCHITECTURE.md`
- Modify: `CONTRIBUTING.md`
- Modify: `SECURITY.md`
- Modify: `AGENTS.md`
- Modify: `docs/design-docs/quantleet-architecture.md`
- Move or replace: `docs/design-docs/quantleet-architecture.md` if the team
  chooses a filename-level rename
- Modify: `docs/design-docs/package-topology-and-naming.md`
- Modify: `docs/design-docs/index.md`
- Modify: `docs/product-specs/public-beta-documentation.md`
- Modify: other current product specs that present active imports
- Modify: `docs/site/**/*.md`
- Modify: `docs/references/research-ergonomics-quickstart.md`
- Modify: tracked notebooks under `notebooks/*.ipynb`

**Step 1: Update release-facing docs**

Change active product copy:

- `Quantleet` to `Quantleet`
- `quantleet` to `quantleet`
- `uv add quantleet==0.1.0b1` to `uv add quantleet==0.1.0b1`
- `python -m pip install quantleet==0.1.0b1` to
  `python -m pip install quantleet==0.1.0b1`
- public imports from `quantleet.*` to `quantleet.*`

Apply this to:

- `README.md`
- `CONTRIBUTING.md`
- `SECURITY.md`
- `AGENTS.md`

Do not create or modify `LICENSE`.

**Step 2: Update governing architecture docs**

Update the current architecture and topology docs so future agents see
`src/quantleet` as the installable engine package:

- `ARCHITECTURE.md`
- `docs/design-docs/package-topology-and-naming.md`
- `docs/design-docs/quantleet-architecture.md`
- `docs/design-docs/index.md`
- `docs/DESIGN.md` if it links by old filename or title

Preferred filename policy:

- Rename `docs/design-docs/quantleet-architecture.md` to
  `docs/design-docs/quantleet-architecture.md`.
- Update links in `ARCHITECTURE.md`, `docs/DESIGN.md`,
  `docs/design-docs/index.md`, `docs/design-docs/package-topology-and-naming.md`,
  and product specs.
- If this creates too much historical churn, keep the old filename for one
  commit but change the title/content to Quantleet and add a follow-up cleanup
  note. The evaluator should prefer the filename rename because this is
  pre-release.

**Step 3: Update public beta docs and examples**

Update all active user-facing docs under `docs/site/`:

- installation snippets
- quickstart imports
- examples
- public API reference
- strategy-authoring guide
- data-sources guide
- backtesting guide
- parameter-exploration guide
- beta-scope copy if it names Quantleet

Update `docs/product-specs/public-beta-documentation.md` so its external
contracts require `quantleet.data`, `quantleet.backtest`, and
`quantleet.research`.

**Step 4: Update current product specs and references**

Update current product specs when they teach active package imports or active
project identity. Prioritize:

- `docs/product-specs/backtest-mvp.md`
- `docs/product-specs/backtest-plotting.md`
- `docs/product-specs/data-ingestion.md`
- `docs/product-specs/market-data.md`
- `docs/product-specs/order-reservation.md`
- `docs/product-specs/order-sizing.md`
- `docs/product-specs/parameter-exploration.md`
- `docs/product-specs/research-ergonomics.md`
- `docs/product-specs/stop-limit.md`
- `docs/references/research-ergonomics-quickstart.md`

Bulk-edit old completed implementation records too; the repository should not keep tracked `quantleet` text.

**Step 5: Update notebooks**

Edit tracked notebook source cells to import `quantleet` instead of
`quantleet`:

- `notebooks/backtest-plotting-real-data-example.ipynb`
- `notebooks/binance-spot-usdm-validation.ipynb`
- `notebooks/binance-usdm-rsi-2024-ad-hoc.ipynb`
- `notebooks/research-ergonomics-quickstart.ipynb`
- `notebooks/spot-cross-exchange-price-comparison.ipynb`

Use a notebook-aware JSON edit or `nbformat` based rewrite. Do not rely on
string replacement that could corrupt notebook JSON.

**Step 6: Run docs and notebook checks**

Run:

```bash
uv run pytest tests/structure/docs -q
uv run poe repo-check
uv run poe notebook-validate
```

Expected:

- Public docs structure tests pass.
- Repo check does not find broken current links or stale public import examples.
- Notebook validation executes with `quantleet` imports.

### Task 6: Clean Build Artifacts And Verify Distribution Behavior

**Files:**
- Remove ignored artifacts under `dist/` before rebuilding.
- No tracked source file should be added under `dist/`.

**Step 1: Remove stale local build artifacts**

Run:

```bash
rm -rf dist
```

This is allowed because `dist/` is ignored build output. Do not remove tracked
files.

**Step 2: Build fresh artifacts**

Run:

```bash
uv build
```

Expected:

- `dist/quantleet-0.1.0b1.tar.gz`
- `dist/quantleet-0.1.0b1-py3-none-any.whl`
- No newly built `quantleet-*` artifacts.

**Step 3: Check wheel metadata**

Run:

```bash
uvx twine check dist/*
python - <<'PY'
from email.parser import Parser
from pathlib import Path
from zipfile import ZipFile

wheel = next(Path("dist").glob("quantleet-*.whl"))
with ZipFile(wheel) as zf:
    metadata_name = next(name for name in zf.namelist() if name.endswith(".dist-info/METADATA"))
    metadata = Parser().parsestr(zf.read(metadata_name).decode("utf-8"))
    names = zf.namelist()

print(metadata["Name"])
print(metadata["Version"])
print(any(name.startswith("quantleet/") for name in names))
print(any(name.startswith("quantleet/") for name in names))
PY
```

Expected output:

```text
quantleet
0.1.0b1
True
False
```

### Task 7: Final Stale-Name Sweep And Full Verification

**Files:**
- Modify any remaining current files found by the sweeps below.
- Leave historical-only references only when they are audit records and not
  current guidance.

**Step 1: Search current surfaces for old name**

Run:

```bash
rg -n "quantleet|Quantleet|QUANTLEET" . \
  --glob '!dist/**' \
  --glob '!.venv/**' \
  --glob '!.git/**' \
  --glob '!.mypy_cache/**' \
  --glob '!.pytest_cache/**' \
  --glob '!.ruff_cache/**'
```

Expected:

- No matches in tracked repository surfaces.
- If a match remains, it must be justified in this plan before final review.

**Step 2: Run full verification**

Run:

```bash
git diff --check
uv run poe verify
```

Expected:

- No whitespace errors.
- Full verification passes.

### Task 8: Rename GitHub Repository And Local Origin

**Files:**
- No tracked files.

**Step 1: Rename the GitHub repository**

After all in-repo verification passes, run:

```bash
gh api --method PATCH /repos/nbsp1221/quantleet -f name=quantleet
```

Expected:

- GitHub repository is renamed to `nbsp1221/quantleet`.

**Step 2: Update local origin**

Run:

```bash
git remote set-url origin https://github.com/nbsp1221/quantleet.git
git remote -v
gh repo view nbsp1221/quantleet --json nameWithOwner,defaultBranchRef,viewerPermission
```

Expected:

- `origin` points at `https://github.com/nbsp1221/quantleet.git`.
- `gh repo view` reports `nameWithOwner` as `nbsp1221/quantleet`.

**Step 3: Confirm no commit was created**

Run:

```bash
git status -sb
git log --oneline -1
```

Expected:

- Worktree contains uncommitted rename changes.
- Latest commit is unchanged from before implementation.

**Step 4: Evaluator review**

Update `## Evaluator Review` with:

- findings first, or `No blocking findings`
- verification commands and pass/fail summaries
- any historical `quantleet` references deliberately left behind
- final disposition

## Evaluator Review

- Findings:
  - No blocking findings.
- Verification evidence:
  - `uv run ruff check src scripts tests --fix` passed.
  - `uv run ruff format src scripts tests` passed with no remaining Python
    formatting changes.
  - Targeted structure, docs, smoke, and command tests passed:
    `145 passed in 1.80s`.
  - `uv run mypy src` passed with no issues in 55 source files.
  - `uv run poe repo-check` passed.
  - `uv build` produced `dist/quantleet-0.1.0b1.tar.gz` and
    `dist/quantleet-0.1.0b1-py3-none-any.whl`.
  - `uvx twine check dist/*` passed for the sdist and wheel.
  - Wheel metadata inspection reported package name `quantleet`, version
    `0.1.0b1`, package contents under `quantleet/`, and no package contents
    under the old package root.
  - Stale-name sweep across tracked repository surfaces returned no matches.
  - `git diff --check` passed.
  - `uv run poe verify` passed: Ruff, mypy, pytest `625 passed, 4 skipped`,
    coverage policy, build, repo-check, and notebook validation all completed
    successfully.
  - GitHub repository rename completed; `gh repo view nbsp1221/quantleet`
    reports `nameWithOwner` as `nbsp1221/quantleet`, default branch `main`, and
    viewer permission `ADMIN`.
  - Local `origin` now points at `https://github.com/nbsp1221/quantleet.git`.
  - Latest commit remains `8746daf`; no commit was created.
- Final disposition:
  - Complete. The repository is renamed in working tree and GitHub remote state,
    with uncommitted changes left for user review as requested.
