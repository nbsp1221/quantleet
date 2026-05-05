from __future__ import annotations

import tomllib

from scripts import coverage_check
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
    assert coverage_check.GLOBAL_MIN_COVERAGE == 90.0
    assert coverage_check.TRADING_DOMAIN_MIN_COVERAGE == 100.0
    assert coverage_check.TRADING_DOMAIN_PREFIX == "src/quantleet/trading/domain/"


def test_coverage_harness_targets_source_only() -> None:
    assert coverage_check.INCLUDE_PATTERN == "src/quantleet/*"
