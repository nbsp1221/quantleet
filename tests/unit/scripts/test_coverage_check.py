from __future__ import annotations

import json
import subprocess
from contextlib import nullcontext
from pathlib import Path

from scripts import coverage_check


def test_coverage_check_passes_when_thresholds_are_met(
    monkeypatch,
    tmp_path: Path,
    capsys,
) -> None:
    calls: list[list[str]] = []

    def fake_run(args: list[str]) -> subprocess.CompletedProcess[str]:
        calls.append(args)
        if "json" in args:
            json_path = Path(args[args.index("-o") + 1])
            json_path.write_text(
                json.dumps(
                    {
                        "totals": {"percent_covered": 90.5},
                        "files": {
                            "src/quantleet/trading/domain/matching.py": {
                                "summary": {"percent_covered": 100.0}
                            }
                        },
                    }
                ),
                encoding="utf-8",
            )
        return subprocess.CompletedProcess(args=args, returncode=0)

    monkeypatch.setattr(coverage_check, "_run", fake_run)
    monkeypatch.setattr(coverage_check, "TemporaryDirectory", lambda: nullcontext(str(tmp_path)))

    assert coverage_check.main() == 0
    assert any("-o" in call for call in calls)

    out = capsys.readouterr().out
    assert "coverage policy check passed" in out


def test_coverage_check_fails_when_thresholds_are_below_policy(
    monkeypatch,
    tmp_path: Path,
    capsys,
) -> None:
    def fake_run(args: list[str]) -> subprocess.CompletedProcess[str]:
        if "json" in args:
            json_path = Path(args[args.index("-o") + 1])
            json_path.write_text(
                json.dumps(
                    {
                        "totals": {"percent_covered": 89.0},
                        "files": {
                            "src/quantleet/trading/domain/matching.py": {
                                "summary": {"percent_covered": 99.0}
                            }
                        },
                    }
                ),
                encoding="utf-8",
            )
        return subprocess.CompletedProcess(args=args, returncode=0)

    monkeypatch.setattr(coverage_check, "_run", fake_run)
    monkeypatch.setattr(coverage_check, "TemporaryDirectory", lambda: nullcontext(str(tmp_path)))

    assert coverage_check.main() == 1

    out = capsys.readouterr().out
    assert "Global source line coverage is below the approved floor" in out
    assert "Tier A trading/domain file is below the approved full-coverage bar" in out
