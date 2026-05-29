import subprocess
from pathlib import Path

from scripts import check_docs, repo_check
from tests.structure.repo.test_poe_task_contracts import write_minimal_repo_docs
from tests.support import ROOT


def test_check_docs_reports_no_issues_for_current_required_docs() -> None:
    assert check_docs.collect_issues(ROOT) == []


def test_check_docs_flags_missing_required_doc(tmp_path: Path) -> None:
    write_minimal_repo_docs(tmp_path)
    (tmp_path / "ARCHITECTURE.md").unlink()

    issues = check_docs.collect_issues(tmp_path)

    assert "Missing required document: ARCHITECTURE.md" in issues


def test_check_docs_flags_placeholder_project_metadata(tmp_path: Path) -> None:
    write_minimal_repo_docs(tmp_path)
    (tmp_path / "README.md").write_text(
        "# quantleet\n\n## Setup\n\nAdd your description here\n",
        encoding="utf-8",
    )

    issues = check_docs.collect_issues(tmp_path)

    assert any("placeholder" in issue.lower() for issue in issues)


def test_check_docs_does_not_fail_on_untracked_indexed_artifact_when_head_exists(
    tmp_path: Path,
) -> None:
    from tests.structure.repo.test_poe_task_contracts import write_minimal_repo_docs

    write_minimal_repo_docs(tmp_path)
    (tmp_path / "pyproject.toml").write_text(
        """
[project]
name = "quantleet"
version = "0.1.0"

[dependency-groups]
dev = ["poethepoet>=0.42.1"]

[tool.poe]
executor = "uv"

[tool.poe.tasks]
lint = "ruff check ."
format = "ruff format ."
format-check = "ruff format --check ."
dead-code = "vulture"
dependency-check = "deptry src"
perf-check = "pytest tests/perf -q -x --run-perf"
check-runtime = ["check", "perf-check"]
typecheck = "mypy src"
test = "pytest -q"
test-unit = "pytest tests/unit -q"
test-integration = "pytest tests/integration -q"
test-structure = "pytest tests/structure -q"
test-smoke = "pytest tests/smoke/local -q"
test-live = "pytest tests/smoke/live -q"
coverage = [{ cmd = "coverage run -m pytest -q" }, { cmd = "coverage report -m" }]
coverage-diff = [
    { cmd = "coverage erase" },
    { cmd = "coverage run -m pytest -q" },
    { cmd = "coverage xml -o coverage.xml --fail-under=0" },
    { cmd = "diff-cover coverage.xml --compare-branch HEAD --include-untracked --fail-under 80" },
]
coverage-baseline = { cmd = '''
uv run python scripts/coverage_baseline.py check
--baseline .coverage-baseline.json
--allowed-drop 0.25
--current-json coverage-baseline-current.json
''' }
coverage-baseline-update = { cmd = '''
uv run python scripts/coverage_baseline.py update
--baseline .coverage-baseline.json
--current-json coverage-baseline-current.json
''' }
coverage-gates = [
    { cmd = "coverage erase" },
    { cmd = "coverage run -m pytest -q" },
    { cmd = "coverage report -m" },
    { cmd = "coverage xml -o coverage.xml --fail-under=0" },
    { cmd = "diff-cover coverage.xml --compare-branch HEAD --include-untracked --fail-under 80" },
    "coverage-baseline",
]
build = "uv build"
twine-check = "uvx twine check --strict dist/*.whl dist/*.tar.gz"
repo-check = "uv run python scripts/repo_check.py"
notebook-validate = "uv run python scripts/notebook_validate.py"
live-smoke = "uv run python scripts/live_smoke.py"
check = [
    "format-check",
    "lint",
    "dead-code",
    "dependency-check",
    "typecheck",
    "coverage-gates",
    "build",
    "twine-check",
    "repo-check",
    "notebook-validate",
]
""".strip(),
        encoding="utf-8",
    )

    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "commit", "-m", "init"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )

    extra_design_doc = tmp_path / "docs" / "design-docs" / "future-draft.md"
    extra_design_doc.write_text("future draft\n", encoding="utf-8")
    index_path = tmp_path / "docs" / "design-docs" / "index.md"
    index_path.write_text(
        index_path.read_text(encoding="utf-8") + "future-draft.md\n",
        encoding="utf-8",
    )

    issues = check_docs.collect_issues(tmp_path)

    assert "Indexed artifact is untracked: docs/design-docs/future-draft.md" not in issues


def test_check_docs_flags_missing_markdown_link_target(tmp_path: Path) -> None:
    write_minimal_repo_docs(tmp_path)
    architecture_path = tmp_path / "ARCHITECTURE.md"
    architecture_path.write_text(
        "[missing](docs/design-docs/missing-draft-ko.md)\n",
        encoding="utf-8",
    )

    issues = check_docs.collect_issues(tmp_path)

    assert (
        "ARCHITECTURE.md points to missing target: docs/design-docs/missing-draft-ko.md" in issues
    )


def test_check_docs_flags_unindexed_golden_principles_doc(tmp_path: Path) -> None:
    write_minimal_repo_docs(tmp_path)
    (tmp_path / "pyproject.toml").write_text(
        """
[project]
name = "quantleet"
version = "0.1.0"

[dependency-groups]
dev = ["poethepoet>=0.42.1"]

[tool.poe]
executor = "uv"

[tool.poe.tasks]
lint = "ruff check ."
format = "ruff format ."
format-check = "ruff format --check ."
dead-code = "vulture"
dependency-check = "deptry src"
perf-check = "pytest tests/perf -q -x --run-perf"
check-runtime = ["check", "perf-check"]
typecheck = "mypy src"
test = "pytest -q"
test-unit = "pytest tests/unit -q"
test-integration = "pytest tests/integration -q"
test-structure = "pytest tests/structure -q"
test-smoke = "pytest tests/smoke/local -q"
test-live = "pytest tests/smoke/live -q"
coverage = [{ cmd = "coverage run -m pytest -q" }, { cmd = "coverage report -m" }]
coverage-diff = [
    { cmd = "coverage erase" },
    { cmd = "coverage run -m pytest -q" },
    { cmd = "coverage xml -o coverage.xml --fail-under=0" },
    { cmd = "diff-cover coverage.xml --compare-branch HEAD --include-untracked --fail-under 80" },
]
coverage-baseline = { cmd = '''
uv run python scripts/coverage_baseline.py check
--baseline .coverage-baseline.json
--allowed-drop 0.25
--current-json coverage-baseline-current.json
''' }
coverage-baseline-update = { cmd = '''
uv run python scripts/coverage_baseline.py update
--baseline .coverage-baseline.json
--current-json coverage-baseline-current.json
''' }
coverage-gates = [
    { cmd = "coverage erase" },
    { cmd = "coverage run -m pytest -q" },
    { cmd = "coverage report -m" },
    { cmd = "coverage xml -o coverage.xml --fail-under=0" },
    { cmd = "diff-cover coverage.xml --compare-branch HEAD --include-untracked --fail-under 80" },
    "coverage-baseline",
]
build = "uv build"
twine-check = "uvx twine check --strict dist/*.whl dist/*.tar.gz"
repo-check = "uv run python scripts/repo_check.py"
notebook-validate = "uv run python scripts/notebook_validate.py"
live-smoke = "uv run python scripts/live_smoke.py"
check = [
    "format-check",
    "lint",
    "dead-code",
    "dependency-check",
    "typecheck",
    "coverage-gates",
    "build",
    "twine-check",
    "repo-check",
    "notebook-validate",
]
""".strip(),
        encoding="utf-8",
    )
    design_index_path = tmp_path / "docs" / "design-docs" / "index.md"
    design_index_path.write_text(
        design_index_path.read_text(encoding="utf-8").replace(
            "| [`golden-principles.md`](golden-principles.md) "
            "| Governing | repository cleanup and promotion work | Before promoting "
            "repeated review findings into docs or checks. |\n",
            "",
        ),
        encoding="utf-8",
    )

    issues = check_docs.collect_issues(tmp_path)

    assert "docs/design-docs/index.md is missing design doc: golden-principles.md" in issues


def test_check_docs_flags_missing_plan_pointer_doc(tmp_path: Path) -> None:
    write_minimal_repo_docs(tmp_path)
    (tmp_path / "docs" / "PLANS.md").unlink()

    issues = check_docs.collect_issues(tmp_path)

    assert "Missing required document: docs/PLANS.md" in issues


def test_repo_check_accepts_minimal_active_contract_without_legacy_harness_artifacts(
    tmp_path: Path,
) -> None:
    write_minimal_repo_docs(tmp_path)
    (tmp_path / "pyproject.toml").write_text(
        """
[project]
name = "quantleet"
version = "0.1.0"

[dependency-groups]
dev = ["poethepoet>=0.42.1"]

[tool.poe]
executor = "uv"

[tool.poe.tasks]
lint = "ruff check ."
format = "ruff format ."
format-check = "ruff format --check ."
dead-code = "vulture"
dependency-check = "deptry src"
perf-check = "pytest tests/perf -q -x --run-perf"
check-runtime = ["check", "perf-check"]
typecheck = "mypy src"
test = "pytest -q"
test-unit = "pytest tests/unit -q"
test-integration = "pytest tests/integration -q"
test-structure = "pytest tests/structure -q"
test-smoke = "pytest tests/smoke/local -q"
test-live = "pytest tests/smoke/live -q"
coverage = [{ cmd = "coverage run -m pytest -q" }, { cmd = "coverage report -m" }]
coverage-diff = [
    { cmd = "coverage erase" },
    { cmd = "coverage run -m pytest -q" },
    { cmd = "coverage xml -o coverage.xml --fail-under=0" },
    { cmd = "diff-cover coverage.xml --compare-branch HEAD --include-untracked --fail-under 80" },
]
coverage-baseline = { cmd = '''
uv run python scripts/coverage_baseline.py check
--baseline .coverage-baseline.json
--allowed-drop 0.25
--current-json coverage-baseline-current.json
''' }
coverage-baseline-update = { cmd = '''
uv run python scripts/coverage_baseline.py update
--baseline .coverage-baseline.json
--current-json coverage-baseline-current.json
''' }
coverage-gates = [
    { cmd = "coverage erase" },
    { cmd = "coverage run -m pytest -q" },
    { cmd = "coverage report -m" },
    { cmd = "coverage xml -o coverage.xml --fail-under=0" },
    { cmd = "diff-cover coverage.xml --compare-branch HEAD --include-untracked --fail-under 80" },
    "coverage-baseline",
]
build = "uv build"
twine-check = "uvx twine check --strict dist/*.whl dist/*.tar.gz"
repo-check = "uv run python scripts/repo_check.py"
notebook-validate = "uv run python scripts/notebook_validate.py"
live-smoke = "uv run python scripts/live_smoke.py"
check = [
    "format-check",
    "lint",
    "dead-code",
    "dependency-check",
    "typecheck",
    "coverage-gates",
    "build",
    "twine-check",
    "repo-check",
    "notebook-validate",
]
""".strip(),
        encoding="utf-8",
    )
    package_root = tmp_path / "src" / "quantleet"
    package_root.mkdir(parents=True)
    (package_root / "__init__.py").write_text("", encoding="utf-8")

    assert repo_check.collect_issues(tmp_path) == []
