# Active Plan

- Date: 2026-05-16
- Task: Add the first PyPI release workflow
- Status: `complete`
- Risk class: `Tier C`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal: Add a tag-triggered GitHub Actions release workflow that builds the
  `quantleet` package, validates the release artifacts, and publishes to PyPI
  through Trusted Publishing from the `pypi` GitHub environment.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/index.md`
  - `docs/design-docs/index.md`
  - `docs/design-docs/package-topology-and-naming.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/DESIGN.md`
  - `docs/PLANS.md`
  - `docs/research/2026-05-16-github-actions-ci-cd-research.md`
  - `.github/workflows/ci.yaml`
- Why these are governing: They define the repository workflow contract,
  package identity, local verification command surface, safety rules for
  credentials and automation, and the researched CI/CD release shape for the
  first public beta.
- External research cross-check:
  - PyPI Trusted Publishing documentation confirms that GitHub Actions can
    publish with short-lived OIDC credentials instead of stored API tokens.
  - PyPI Trusted Publisher internals document that publisher matching may
    include repository, workflow, and environment claims; the user's configured
    pending publisher uses `nbsp1221/quantleet`, `release.yaml`, and `pypi`.
  - PyPI troubleshooting guidance says the GitHub Actions environment must
    match the configured publisher environment.
  - GitHub OIDC documentation says a job must grant `id-token: write` before
    GitHub can issue an OIDC token.
  - PyPA `gh-action-pypi-publish` documents Trusted Publishing through
    `pypa/gh-action-pypi-publish@release/v1`.
- Human setup already reported:
  - PyPI pending publisher exists for project `quantleet`.
  - Publisher owner/repository: `nbsp1221/quantleet`.
  - Publisher workflow: `release.yaml`.
  - Publisher environment: `pypi`.
  - GitHub environment `pypi` exists and has the user's reviewer gate.
- In-repo scope:
  - Add `.github/workflows/release.yaml`.
  - Keep the release workflow aligned with existing `uv` and `poe` command
    surfaces.
  - Add or update repo-local structure checks only if the existing
    `repo-check` requires recognizing the new workflow.
  - Record generator/evaluator evidence in this plan.
- Out-of-repo scope:
  - Do not create, edit, or remove PyPI settings.
  - Do not create, edit, or remove GitHub repository environment settings.
  - Do not tag, publish, or push a release in this implementation slice unless
    the user explicitly asks after review.
  - Do not add TestPyPI in this slice.
- Tier A progression requested: `no`
- Approval record, if required: Not required. This is repository automation for
  package publication and does not modify `trading` or `execution` behavior.
- Verification commands:
  - `git diff --check`
  - `actionlint .github/workflows/release.yaml`
  - `uv run poe format-check`
  - `uv run poe lint`
  - `uv run poe typecheck`
  - `uv run poe test`
  - `uv run poe build`
  - `uvx twine check --strict dist/*`
  - an isolated install/import smoke against the built wheel
  - `uv run poe repo-check`
  - `uvx zizmor --format plain .github/workflows/release.yaml` as advisory
- Success criteria:
  - `.github/workflows/release.yaml` exists and is the only release workflow
    added.
  - The workflow triggers on version tag pushes matching `v*`.
  - The workflow includes `workflow_dispatch` for controlled manual dry
    execution if practical, but production PyPI publish remains bound to
    release semantics and the `pypi` environment.
  - The workflow builds from the checked-out release commit using Python `3.12`,
    `uv`, and the locked environment.
  - Build validation runs `uv build` and `uvx twine check --strict dist/*`.
  - The release artifact path includes a minimal isolated wheel install/import
    smoke before publishing.
  - Build artifacts are uploaded from the build job and downloaded by the
    publish job; the publish job does not rebuild.
  - Only the PyPI publish job has `id-token: write`.
  - The publish job uses `environment: pypi` so it matches the configured PyPI
    Trusted Publisher and GitHub environment approval gate.
  - No long-lived PyPI token, password, repository secret, or environment
    secret is introduced.
  - The workflow uses the same conventional action-version style as the current
    CI workflow unless the user explicitly chooses SHA pinning later.
  - Fresh local verification passes before the workflow is considered ready.
- Out of scope:
  - TestPyPI publishing.
  - GitHub Release creation or generated release notes.
  - Package attestations as a blocking requirement.
  - Broad Python or OS release matrices.
  - Docker/container publishing.
  - Release branch management.
  - Actual `v0.1.0b1` tag creation or PyPI upload.

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice: The diff must add a minimal,
  auditable PyPI release workflow that matches the user's PyPI/GitHub
  environment setup, preserves the repository command surface, avoids secrets,
  and passes fresh local verification.
- Acceptance artifact location: This plan.
- How the generator and evaluator agreed on done before execution: Success
  criteria, out-of-scope boundaries, and auto-fail conditions were written
  before adding the release workflow.
- Checks the evaluator will use:
  - Inspect `.github/workflows/release.yaml`.
  - Inspect `git diff --stat`.
  - Confirm workflow file name is exactly `release.yaml`.
  - Confirm publish job environment is exactly `pypi`.
  - Confirm OIDC permission is scoped to the publish job only.
  - Run the verification commands listed in the planner contract.
- Auto-fail conditions:
  - The workflow publishes without `environment: pypi`.
  - Any PyPI API token, password, or repository secret is added.
  - `id-token: write` appears outside the publish job.
  - The publish job rebuilds artifacts instead of consuming build artifacts.
  - The workflow uses a CI-only command surface where an existing repo-local
    command exists.
  - The workflow creates a tag, pushes to the repository, or performs an actual
    release during verification.
  - Fresh verification fails.

## Generator Work Log

- Planned slice order:
  1. Inspect current CI workflow and package metadata.
  2. Draft `.github/workflows/release.yaml` with build and publish jobs.
  3. Add a minimal install/import smoke for the built wheel inside the workflow.
  4. Run static workflow validation.
  5. Run package and repo verification.
  6. Record evaluator findings and verification evidence.
- Notes:
  - The user configured PyPI pending publisher with `Environment name: pypi`;
    the release workflow must use exactly that environment.
  - The user configured GitHub environment approval; the workflow should allow
    GitHub to pause only the publishing job, not the build validation job.
  - The current CI workflow intentionally uses readable release tags rather
    than SHA-pinned actions. This release workflow should stay consistent with
    that choice for now.
  - Added `.github/workflows/release.yaml` with a build job and a publish job.
  - The workflow triggers on `v*` tag pushes and manual dispatch.
  - The publish job is additionally gated with
    `if: startsWith(github.ref, 'refs/tags/v')`, so manual branch dispatch
    can validate the build path without publishing.
  - Added a tag/package-version guard so `v0.1.0b1` must match
    `uv version --short` before release artifacts are built for a tag.
  - The build job uses Python `3.12`, `uv sync --locked --dev`,
    `uv run poe build`, `uvx twine check --strict dist/*`, and an isolated
    wheel install/import smoke.
  - The build job uploads `dist/*` as `release-distributions`.
  - The publish job downloads `release-distributions` into `dist/` and
    publishes with `pypa/gh-action-pypi-publish@release/v1`.
  - Only the publish job has `id-token: write`, and it uses
    `environment: pypi`.
  - Disabled `setup-uv` cache in the release workflow after `zizmor` reported
    cache-poisoning risk for runtime release artifacts.
  - No PyPI token, password, GitHub secret, tag creation, push, or actual
    release execution was added.
- Blockers or scope changes:
  - None.

## Evaluator Review

- Findings:
  - No blocker findings remain.
  - Subagent review found no workflow-semantic blocker.
  - Subagent review flagged the pending evaluator artifact in this plan; this
    section closes that requirement with fresh evidence.
  - Subagent review flagged missing tag/package-version consistency as a
    practical release-risk signal. The workflow now checks that `GITHUB_REF_NAME`
    equals `v$(uv version --short)` for tag runs before build/publish can
    proceed.
  - Human review flagged the inline `tomllib` heredoc and package-specific
    public-class import smoke as unusual-looking workflow logic. The workflow
    now uses the repo's existing `uv` surface for version discovery and a
    smaller wheel install/import smoke.
  - The release workflow follows common modern Python OSS release shape:
    tag-triggered release, build/publish job split, artifact handoff, Trusted
    Publishing through OIDC, PyPI environment approval, `twine check`, and
    isolated wheel install smoke.
  - The workflow intentionally stays consistent with the current CI workflow's
    readable action-version style instead of full SHA pinning.
  - Advisory: `zizmor` still reports `unpinned-uses` for release-tag/branch
    action references. This is expected under the current user-approved CI
    style. The release-specific cache-poisoning advisory was removed by setting
    `enable-cache: false` for `setup-uv`.
- Verification evidence:
  - `git diff --check` -> passed.
  - `/tmp/actionlint-release/actionlint .github/workflows/release.yaml` ->
    passed with no findings. The binary was downloaded to `/tmp` from
    `rhysd/actionlint` because `actionlint` and `go` were not installed on PATH.
  - `uv run poe format-check` -> `200 files already formatted`.
  - `uv run poe lint` -> `All checks passed!`.
  - `uv run poe typecheck` -> `Success: no issues found in 61 source files`.
  - `uv run poe test` -> `739 passed, 4 skipped`.
  - `uv run poe build` -> built `dist/quantleet-0.1.0b1.tar.gz` and
    `dist/quantleet-0.1.0b1-py3-none-any.whl`.
  - `uvx twine check --strict dist/*` -> wheel and sdist `PASSED`.
  - Isolated wheel smoke under `/tmp/quantleet-release-smoke` -> installed the
    built wheel and imported `quantleet`; printed `release smoke passed`.
  - Tag/version guard positive check with `GITHUB_REF_NAME=v0.1.0b1` -> passed.
  - Tag/version guard negative check with `GITHUB_REF_NAME=v0.1.0b2` -> failed
    as expected with `Expected tag: v0.1.0b1`.
  - `uv run poe repo-check` -> `repository checks passed`.
  - Remote ref checks confirmed these workflow references exist:
    `actions/checkout@v6`, `actions/setup-python@v6`,
    `astral-sh/setup-uv@v8.1.0`, `actions/upload-artifact@v7`,
    `actions/download-artifact@v8`, and
    `pypa/gh-action-pypi-publish@release/v1`.
  - `uvx zizmor --format plain .github/workflows/release.yaml` -> reports only
    expected `unpinned-uses` findings for the readable action refs.
- Final disposition:
  - Accepted for this implementation slice. Ready for human review; no commit,
    tag, push, or PyPI publication was performed.
