from __future__ import annotations

import tomllib

from tests.support import ROOT


def _pyproject() -> dict[str, object]:
    return tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))


def test_pyproject_defines_coverage_poe_task() -> None:
    tasks = _pyproject()["tool"]["poe"]["tasks"]

    assert "coverage" in tasks


def test_poe_verify_includes_coverage_gate() -> None:
    verify = _pyproject()["tool"]["poe"]["tasks"]["verify"]

    assert "coverage" in verify["sequence"]


def test_repository_defines_approved_coverage_thresholds() -> None:
    coverage = _pyproject()["tool"]["coverage"]

    assert coverage["run"]["branch"] is True
    assert coverage["run"]["source"] == ["quantleet"]
    assert coverage["report"]["fail_under"] == 90
    assert coverage["report"]["show_missing"] is True


def test_coverage_poe_task_uses_native_coverage_commands() -> None:
    tasks = _pyproject()["tool"]["poe"]["tasks"]

    assert tasks["coverage"]["sequence"] == [
        {"cmd": "coverage run -m pytest -q"},
        {"cmd": "coverage report -m"},
    ]


def test_test_poe_task_is_plain_pytest_without_coverage() -> None:
    tasks = _pyproject()["tool"]["poe"]["tasks"]

    assert tasks["test"]["cmd"] == "pytest -q"
    assert "coverage" not in tasks["test"]["cmd"]
    assert "--cov" not in tasks["test"]["cmd"]
