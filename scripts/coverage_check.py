from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
INCLUDE_PATTERN = "src/quantcraft/*"
TRADING_DOMAIN_PREFIX = "src/quantcraft/trading/domain/"
GLOBAL_MIN_COVERAGE = 90.0
TRADING_DOMAIN_MIN_COVERAGE = 100.0


def _run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=ROOT, text=True, check=False)


def _coverage_command(*args: str) -> list[str]:
    return [sys.executable, "-m", "coverage", *args]


def main() -> int:
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        data_file = temp_path / ".coverage"
        json_file = temp_path / "coverage.json"

        test_run = _run(_coverage_command("run", f"--data-file={data_file}", "-m", "pytest", "-q"))
        if test_run.returncode != 0:
            return test_run.returncode

        json_result = _run(
            _coverage_command(
                "json",
                f"--data-file={data_file}",
                f"--include={INCLUDE_PATTERN}",
                "-o",
                str(json_file),
            )
        )
        if json_result.returncode != 0:
            return json_result.returncode

        report_result = _run(
            _coverage_command(
                "report",
                f"--data-file={data_file}",
                f"--include={INCLUDE_PATTERN}",
                "-m",
            )
        )
        if report_result.returncode != 0:
            return report_result.returncode

        if not json_file.exists():
            print("coverage policy check failed")
            print("- coverage json output was not created at the expected path")
            return 1

        payload = json.loads(json_file.read_text(encoding="utf-8"))
        global_percent = float(payload["totals"]["percent_covered"])
        failures: list[str] = []

        if global_percent < GLOBAL_MIN_COVERAGE:
            failures.append(
                "Global source line coverage is below the approved floor: "
                f"{global_percent:.2f}% < {GLOBAL_MIN_COVERAGE:.1f}%"
            )

        file_summaries: dict[str, dict[str, object]] = payload["files"]
        for relative_path, file_payload in sorted(file_summaries.items()):
            if not relative_path.startswith(TRADING_DOMAIN_PREFIX):
                continue
            file_percent = float(file_payload["summary"]["percent_covered"])
            if file_percent < TRADING_DOMAIN_MIN_COVERAGE:
                failures.append(
                    "Tier A trading/domain file is below the approved full-coverage bar: "
                    f"{relative_path} = {file_percent:.2f}% < {TRADING_DOMAIN_MIN_COVERAGE:.1f}%"
                )

        if failures:
            print()
            print("coverage policy check failed")
            for failure in failures:
                print(f"- {failure}")
            print("- Add targeted tests for the uncovered source lines before retrying.")
            return 1

        print()
        print("coverage policy check passed")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
