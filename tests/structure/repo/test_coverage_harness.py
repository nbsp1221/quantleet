from __future__ import annotations

import tomllib

from tests.support import ROOT


def _pyproject() -> dict[str, object]:
    return tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))


def test_pyproject_defines_coverage_poe_task() -> None:
    tasks = _pyproject()["tool"]["poe"]["tasks"]

    assert "coverage" in tasks
    assert "coverage-diff" in tasks
    assert "coverage-baseline" in tasks
    assert "coverage-baseline-update" in tasks
    assert "coverage-gates" in tasks


def test_poe_check_includes_quality_and_coverage_gates() -> None:
    check = _pyproject()["tool"]["poe"]["tasks"]["check"]

    assert check["sequence"] == [
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
    assert "test" not in check["sequence"]
    assert "coverage" not in check["sequence"]
    assert "coverage-diff" not in check["sequence"]


def test_repository_defines_approved_coverage_thresholds() -> None:
    coverage = _pyproject()["tool"]["coverage"]
    dev_dependencies = _pyproject()["dependency-groups"]["dev"]

    assert coverage["run"]["branch"] is True
    assert coverage["run"]["source"] == ["quantleet"]
    assert coverage["report"]["fail_under"] == 90
    assert coverage["report"]["show_missing"] is True
    assert any(dependency.startswith("diff-cover>=") for dependency in dev_dependencies)


def test_coverage_poe_task_uses_native_coverage_commands() -> None:
    tasks = _pyproject()["tool"]["poe"]["tasks"]

    assert tasks["coverage"]["sequence"] == [
        {"cmd": "coverage run -m pytest -q"},
        {"cmd": "coverage report -m"},
    ]


def test_coverage_diff_poe_task_uses_diff_cover_for_changed_lines() -> None:
    tasks = _pyproject()["tool"]["poe"]["tasks"]

    assert tasks["coverage-diff"]["sequence"] == [
        {"cmd": "coverage erase"},
        {"cmd": "coverage run -m pytest -q"},
        {"cmd": "coverage xml -o coverage.xml --fail-under=0"},
        {
            "cmd": (
                "diff-cover coverage.xml --compare-branch HEAD --include-untracked --fail-under 80"
            ),
        },
    ]


def test_coverage_gates_poe_task_reuses_one_pytest_run_for_both_gates() -> None:
    tasks = _pyproject()["tool"]["poe"]["tasks"]

    assert tasks["coverage-gates"]["sequence"] == [
        {"cmd": "coverage erase"},
        {"cmd": "coverage run -m pytest -q"},
        {"cmd": "coverage report -m"},
        {"cmd": "coverage xml -o coverage.xml --fail-under=0"},
        {
            "cmd": (
                "diff-cover coverage.xml --compare-branch HEAD --include-untracked --fail-under 80"
            ),
        },
        "coverage-baseline",
    ]
    assert tasks["coverage-gates"]["help"] == (
        "Run tests once and enforce full-project, changed-lines, and regression coverage gates"
    )


def test_coverage_baseline_poe_tasks_use_repo_local_script() -> None:
    tasks = _pyproject()["tool"]["poe"]["tasks"]

    assert tasks["coverage-baseline"]["cmd"] == (
        "uv run python scripts/coverage_baseline.py check "
        "--baseline .coverage-baseline.json "
        "--allowed-drop 0.25 "
        "--current-json coverage-baseline-current.json"
    )
    assert tasks["coverage-baseline-update"]["cmd"] == (
        "uv run python scripts/coverage_baseline.py update "
        "--baseline .coverage-baseline.json "
        "--current-json coverage-baseline-current.json"
    )


def test_test_poe_task_is_plain_pytest_without_coverage() -> None:
    tasks = _pyproject()["tool"]["poe"]["tasks"]

    assert tasks["test"]["cmd"] == "pytest -q"
    assert "coverage" not in tasks["test"]["cmd"]
    assert "--cov" not in tasks["test"]["cmd"]
