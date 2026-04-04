import tomllib

from quantcraft._repo_tools import poe_executor_type
from scripts import check_docs
from tests.support import ROOT

REQUIRED_POE_TASKS = [
    "lint",
    "format",
    "perf-check",
    "verify-runtime",
    "typecheck",
    "test",
    "test-unit",
    "test-integration",
    "test-structure",
    "test-smoke",
    "test-live",
    "coverage",
    "build",
    "repo-check",
    "notebook-validate",
    "live-smoke",
    "verify",
]


def write_minimal_repo_docs(tmp_path) -> None:
    (tmp_path / "README.md").write_text(
        (
            "# quantcraft\n\n## Setup\n\n"
            "uv run poe verify\n"
            "uv run poe perf-check\n"
            "uv run poe verify-runtime\n"
        ),
        encoding="utf-8",
    )
    (tmp_path / "AGENTS.md").write_text(
        (
            "uv run poe verify\n"
            "uv run poe perf-check\n"
            "uv run poe verify-runtime\n"
            "uv run poe coverage\n"
            "repo-local harness commands\n"
            "docs/design-docs/index.md\n"
        ),
        encoding="utf-8",
    )
    (tmp_path / "ARCHITECTURE.md").write_text(
        "docs/design-docs/quantcraft-architecture-draft-ko.md\n",
        encoding="utf-8",
    )
    (tmp_path / "agent-development-guide-ko.md").write_text(
        "scripts/\nuv run poe verify\nuv run poe verify-runtime\n",
        encoding="utf-8",
    )

    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "DESIGN.md").write_text("design docs live here\n", encoding="utf-8")
    (docs_dir / "PLANS.md").write_text(
        (
            "docs/plans/\n"
            "docs/exec-plans/active/\n"
            "docs/exec-plans/completed/\n"
            "Durable architecture or contract drafts do not belong in `docs/plans/`;\n"
        ),
        encoding="utf-8",
    )
    (docs_dir / "QUALITY_SCORE.md").write_text(
        "docs_system\ndocs/feedback-promotion-log.md\n",
        encoding="utf-8",
    )
    (docs_dir / "RELIABILITY.md").write_text("reliability\n", encoding="utf-8")
    (docs_dir / "SECURITY.md").write_text("security\n", encoding="utf-8")
    (docs_dir / "feedback-promotion-log.md").write_text(
        "feedback promotion log\n",
        encoding="utf-8",
    )

    design_docs_dir = docs_dir / "design-docs"
    design_docs_dir.mkdir()
    (design_docs_dir / "index.md").write_text(
        (
            "# Design Docs\n\n"
            "## Metadata\n"
            "- index_kind: design-doc-status-map\n\n"
            "## Documents\n"
            "| Document | Status | Canonical | Applicability | Read When | Notes |\n"
            "| --- | --- | --- | --- | --- | --- |\n"
            "| [`quantcraft-architecture-draft-ko.md`](quantcraft-architecture-draft-ko.md) "
            "| approved | yes | architecture work | Before changing bounded contexts. "
            "| Canonical architecture doc. |\n"
            "| [`trading-kernel-contract-draft-ko.md`](trading-kernel-contract-draft-ko.md) "
            "| draft | no | trading-kernel planning | When evaluating draft kernel semantics. "
            "| Still draft. |\n"
            "| [`golden-principles.md`](golden-principles.md) "
            "| approved | yes | all agent work | Before promoting repository-wide drift rules. "
            "| Canonical cleanup invariants. |\n"
            "| [`architecture-governance-draft-ko.md`](architecture-governance-draft-ko.md) "
            "| approved | yes | harness governance work | Before changing repo checks. "
            "| Governance baseline. |\n"
        ),
        encoding="utf-8",
    )
    (design_docs_dir / "quantcraft-architecture-draft-ko.md").write_text(
        "draft architecture\n",
        encoding="utf-8",
    )
    (design_docs_dir / "trading-kernel-contract-draft-ko.md").write_text(
        "draft trading contract\n",
        encoding="utf-8",
    )
    (design_docs_dir / "golden-principles.md").write_text(
        "golden principles\n",
        encoding="utf-8",
    )
    (design_docs_dir / "architecture-governance-draft-ko.md").write_text(
        "draft governance\n",
        encoding="utf-8",
    )

    references_dir = docs_dir / "references"
    references_dir.mkdir()
    (references_dir / "index.md").write_text("tooling.md\n", encoding="utf-8")
    (references_dir / "tooling.md").write_text(
        (
            "uv run poe verify\n"
            "uv run poe perf-check\n"
            "uv run poe verify-runtime\n"
            "uv run poe coverage\n"
            "uv run poe format\n"
            "uv run poe test-live\n"
            "uv run python scripts/coverage_check.py\n"
            "uv run python scripts/repo_check.py\n"
            "uv run python scripts/notebook_validate.py\n"
            "uv run python scripts/live_smoke.py\n"
        ),
        encoding="utf-8",
    )

    product_specs_dir = docs_dir / "product-specs"
    product_specs_dir.mkdir()
    (product_specs_dir / "index.md").write_text(
        (
            "# Product Specs\n\n"
            "## Metadata\n"
            "- index_kind: product-spec-status-map\n\n"
            "## Documents\n"
            "| Document | Status | Canonical | Applicability | Read When | Notes |\n"
            "| --- | --- | --- | --- | --- | --- |\n"
            "| [`market-data.md`](market-data.md) | implemented | yes | "
            "current implemented scope | Before changing the current "
            "market-data surface. | Current implemented-scope entry. |\n"
            "| [`backtest-mvp.md`](backtest-mvp.md) | approved | yes | "
            "approved next slice | Before changing current backtest slice "
            "behavior. | Canonical slice spec. |\n"
        ),
        encoding="utf-8",
    )
    (product_specs_dir / "market-data.md").write_text("market data\n", encoding="utf-8")
    (product_specs_dir / "backtest-mvp.md").write_text("backtest mvp\n", encoding="utf-8")


def test_repo_check_accepts_current_poe_task_contract() -> None:
    assert check_docs.collect_issues(ROOT) == []


def test_pyproject_defines_required_poe_tasks() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    assert poe_executor_type(pyproject) == "uv"

    task_names = pyproject["tool"]["poe"]["tasks"].keys()
    for task_name in REQUIRED_POE_TASKS:
        assert task_name in task_names


def test_poe_task_surface_is_documented() -> None:
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    tooling = (ROOT / "docs" / "references" / "tooling.md").read_text(encoding="utf-8")

    for command in [
        "uv run poe verify",
        "uv run poe perf-check",
        "uv run poe verify-runtime",
        "uv run poe coverage",
        "uv run poe format",
        "uv run poe test-live",
    ]:
        assert command in agents or command in tooling
    assert "project.scripts" not in agents
    for command in [
        "uv run python scripts/coverage_check.py",
        "uv run python scripts/repo_check.py",
        "uv run python scripts/notebook_validate.py",
        "uv run python scripts/live_smoke.py",
    ]:
        assert command in agents or command in tooling


def test_repo_check_flags_missing_required_poe_task(tmp_path) -> None:
    write_minimal_repo_docs(tmp_path)
    (tmp_path / "pyproject.toml").write_text(
        """
[project]
name = "quantcraft"
version = "0.1.0"

[dependency-groups]
dev = ["poethepoet>=0.42.1"]

[tool.poe]
executor = "uv"

[tool.poe.tasks]
lint = "ruff check ."
""".strip(),
        encoding="utf-8",
    )

    issues = check_docs.collect_issues(tmp_path)

    assert any("Missing required Poe task: verify" in issue for issue in issues)


def test_repo_check_accepts_table_form_poe_executor(tmp_path) -> None:
    write_minimal_repo_docs(tmp_path)
    (tmp_path / "pyproject.toml").write_text(
        """
[project]
name = "quantcraft"
version = "0.1.0"

[dependency-groups]
dev = ["poethepoet>=0.42.1"]

[tool.poe.executor]
type = "uv"

[tool.poe.tasks]
lint = "ruff check ."
format = "ruff format ."
perf-check = "pytest tests/perf -q"
verify-runtime = ["verify", "perf-check"]
typecheck = "mypy src"
test = "pytest -q"
test-unit = "pytest tests/unit -q"
test-integration = "pytest tests/integration -q"
test-structure = "pytest tests/structure -q"
test-smoke = "pytest tests/smoke/local -q"
test-live = "pytest tests/smoke/live -q"
coverage = "uv run python scripts/coverage_check.py"
build = "uv build"
repo-check = "uv run python scripts/repo_check.py"
notebook-validate = "uv run python scripts/notebook_validate.py"
live-smoke = "uv run python scripts/live_smoke.py"
verify = ["lint", "typecheck", "test", "coverage", "build", "repo-check", "notebook-validate"]
""".strip(),
        encoding="utf-8",
    )

    assert check_docs.collect_issues(tmp_path) == []
