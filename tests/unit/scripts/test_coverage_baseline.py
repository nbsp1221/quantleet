from __future__ import annotations

import json
import subprocess
import sys
from argparse import Namespace
from decimal import Decimal
from pathlib import Path

import pytest

from scripts import coverage_baseline


def write_current(path: Path, percent: float) -> None:
    path.write_text(
        json.dumps({"totals": {"percent_covered": percent}}),
        encoding="utf-8",
    )


def write_baseline(path: Path, percent: float, *, allowed_drop: float = 0.25) -> None:
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "coverage_percent": percent,
                "allowed_drop": allowed_drop,
                "coverage_tool": "coverage.py",
                "coverage_command": "coverage run -m pytest -q",
                "coverage_run_branch": True,
                "coverage_run_source": ["quantleet"],
            },
        ),
        encoding="utf-8",
    )


def read_baseline_percent(path: Path) -> float:
    return float(json.loads(path.read_text(encoding="utf-8"))["coverage_percent"])


def read_baseline_payload(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_check_passes_when_drop_equals_allowed_threshold(tmp_path: Path) -> None:
    baseline_path = tmp_path / ".coverage-baseline.json"
    current_path = tmp_path / "coverage-baseline-current.json"
    write_baseline(baseline_path, 90.25)
    write_current(current_path, 90.0)

    evaluation = coverage_baseline.evaluate_check(
        baseline_path,
        current_path,
        allowed_drop=Decimal("0.25"),
    )

    assert evaluation.decision == "tolerated"
    assert evaluation.exit_code == 0
    assert read_baseline_percent(baseline_path) == 90.25


def test_check_fails_when_drop_exceeds_allowed_threshold(tmp_path: Path) -> None:
    baseline_path = tmp_path / ".coverage-baseline.json"
    current_path = tmp_path / "coverage-baseline-current.json"
    write_baseline(baseline_path, 90.26)
    write_current(current_path, 90.0)

    evaluation = coverage_baseline.evaluate_check(
        baseline_path,
        current_path,
        allowed_drop=Decimal("0.25"),
    )

    assert evaluation.decision == "failed"
    assert evaluation.exit_code == 2
    assert read_baseline_percent(baseline_path) == 90.26


def test_check_raises_baseline_when_current_coverage_improves(tmp_path: Path) -> None:
    baseline_path = tmp_path / ".coverage-baseline.json"
    current_path = tmp_path / "coverage-baseline-current.json"
    write_baseline(baseline_path, 90.0)
    write_current(current_path, 91.5)

    evaluation = coverage_baseline.evaluate_check(
        baseline_path,
        current_path,
        allowed_drop=Decimal("0.25"),
    )

    assert evaluation.decision == "raised"
    assert evaluation.exit_code == 0
    payload = read_baseline_payload(baseline_path)
    assert payload["schema_version"] == 1
    assert "baseline_commit" in payload
    assert payload["coverage_percent"] == 91.5
    assert payload["allowed_drop"] == 0.25
    assert payload["coverage_tool"] == "coverage.py"
    assert payload["coverage_command"] == "coverage run -m pytest -q"
    assert payload["coverage_run_branch"] is True
    assert payload["coverage_run_source"] == ["quantleet"]


def test_check_leaves_baseline_unchanged_when_coverage_is_equal(tmp_path: Path) -> None:
    baseline_path = tmp_path / ".coverage-baseline.json"
    current_path = tmp_path / "coverage-baseline-current.json"
    write_baseline(baseline_path, 90.0)
    before = baseline_path.read_text(encoding="utf-8")
    write_current(current_path, 90.0)

    evaluation = coverage_baseline.evaluate_check(
        baseline_path,
        current_path,
        allowed_drop=Decimal("0.25"),
    )

    assert evaluation.decision == "unchanged"
    assert evaluation.exit_code == 0
    assert baseline_path.read_text(encoding="utf-8") == before


def test_update_creates_missing_baseline(tmp_path: Path) -> None:
    baseline_path = tmp_path / ".coverage-baseline.json"
    current_path = tmp_path / "coverage-baseline-current.json"
    write_current(current_path, 92.0)

    evaluation = coverage_baseline.evaluate_update(
        baseline_path,
        current_path,
        allowed_drop=Decimal("0.25"),
    )

    assert evaluation.decision == "created"
    assert evaluation.exit_code == 0
    assert read_baseline_percent(baseline_path) == 92.0


def test_update_refuses_to_lower_existing_baseline(tmp_path: Path) -> None:
    baseline_path = tmp_path / ".coverage-baseline.json"
    current_path = tmp_path / "coverage-baseline-current.json"
    write_baseline(baseline_path, 92.0)
    write_current(current_path, 91.0)

    evaluation = coverage_baseline.evaluate_update(
        baseline_path,
        current_path,
        allowed_drop=Decimal("0.25"),
    )

    assert evaluation.decision == "refused"
    assert evaluation.exit_code == 3
    assert read_baseline_percent(baseline_path) == 92.0


def test_current_percent_must_come_from_coverage_totals(tmp_path: Path) -> None:
    current_path = tmp_path / "coverage-baseline-current.json"
    write_current(current_path, 93.125)

    assert coverage_baseline.read_current_percent(current_path) == Decimal("93.125")


def test_generate_current_json_requires_existing_coverage_data(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    with pytest.raises(coverage_baseline.CoverageBaselineError, match="missing .coverage"):
        coverage_baseline.generate_current_json(tmp_path / "coverage-baseline-current.json")


def test_generate_current_json_uses_coverage_json_without_rerunning_pytest(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[list[str]] = []
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".coverage").write_text("coverage data", encoding="utf-8")

    def fake_run(
        command: list[str],
        *,
        capture_output: bool,
        text: bool,
        check: bool,
    ) -> subprocess.CompletedProcess[str]:
        calls.append(command)
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    monkeypatch.setattr(coverage_baseline.subprocess, "run", fake_run)

    coverage_baseline.generate_current_json(tmp_path / "coverage-baseline-current.json")

    assert calls == [["coverage", "json", "-o", str(tmp_path / "coverage-baseline-current.json")]]


def test_run_propagates_regression_exit_code_and_keeps_existing_current_json(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    baseline_path = tmp_path / ".coverage-baseline.json"
    current_path = tmp_path / "coverage-baseline-current.json"
    write_baseline(baseline_path, 91.0)
    current_path.write_text("pre-existing", encoding="utf-8")

    def fake_generate(path: Path) -> None:
        write_current(path, 90.0)

    monkeypatch.setattr(coverage_baseline, "generate_current_json", fake_generate)

    exit_code = coverage_baseline.run(
        Namespace(
            mode="check",
            baseline=baseline_path,
            current_json=current_path,
            allowed_drop=Decimal("0.25"),
            keep_current_json=False,
        ),
    )

    assert exit_code == 2
    assert current_path.exists()


def test_run_cleans_generated_current_json_when_path_did_not_preexist(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    baseline_path = tmp_path / ".coverage-baseline.json"
    current_path = tmp_path / "coverage-baseline-current.json"
    write_baseline(baseline_path, 90.0)

    def fake_generate(path: Path) -> None:
        write_current(path, 90.0)

    monkeypatch.setattr(coverage_baseline, "generate_current_json", fake_generate)

    exit_code = coverage_baseline.run(
        Namespace(
            mode="check",
            baseline=baseline_path,
            current_json=current_path,
            allowed_drop=Decimal("0.25"),
            keep_current_json=False,
        ),
    )

    assert exit_code == 0
    assert not current_path.exists()


def test_non_finite_numbers_are_rejected(tmp_path: Path) -> None:
    current_path = tmp_path / "coverage-baseline-current.json"
    write_current(current_path, float("nan"))

    with pytest.raises(coverage_baseline.CoverageBaselineError, match="must be finite"):
        coverage_baseline.read_current_percent(current_path)


def test_script_entrypoint_preserves_failure_exit_code(tmp_path: Path) -> None:
    baseline_path = tmp_path / ".coverage-baseline.json"
    write_baseline(baseline_path, 90.0)

    result = subprocess.run(
        [
            sys.executable,
            str(Path(coverage_baseline.__file__).resolve()),
            "check",
            "--baseline",
            str(baseline_path),
            "--current-json",
            str(tmp_path / "coverage-baseline-current.json"),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert "missing .coverage" in result.stdout
