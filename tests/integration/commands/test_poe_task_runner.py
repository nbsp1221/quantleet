from __future__ import annotations

import subprocess

from tests.support import ROOT


def test_poe_help_lists_required_tasks() -> None:
    result = subprocess.run(
        ["uv", "run", "poe", "--help"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    output = result.stdout + result.stderr
    for task_name in [
        "lint",
        "format",
        "typecheck",
        "test",
        "test-live",
        "coverage",
        "verify",
        "verify-runtime",
    ]:
        assert task_name in output


def test_poe_verify_dry_run_succeeds() -> None:
    result = subprocess.run(
        ["uv", "run", "poe", "--dry-run", "verify"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    output = result.stdout + result.stderr
    for fragment in [
        "ruff check .",
        "mypy src",
        "pytest -q",
        "uv run python scripts/coverage_check.py",
        "uv build",
        "uv run python scripts/repo_check.py",
        "uv run python scripts/notebook_validate.py",
    ]:
        assert fragment in output


def test_poe_verify_runtime_dry_run_succeeds() -> None:
    result = subprocess.run(
        ["uv", "run", "poe", "--dry-run", "verify-runtime"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    output = result.stdout + result.stderr
    for fragment in [
        "ruff check .",
        "mypy src",
        "pytest -q",
        "uv run python scripts/coverage_check.py",
        "uv build",
        "uv run python scripts/repo_check.py",
        "uv run python scripts/notebook_validate.py",
        "pytest tests/perf/test_rsi_backtest_benchmark.py -q -x --run-perf",
    ]:
        assert fragment in output
