from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from os import replace
from pathlib import Path
from typing import Any, Literal

SCHEMA_VERSION = 1
DEFAULT_BASELINE_PATH = Path(".coverage-baseline.json")
DEFAULT_CURRENT_JSON_PATH = Path("coverage-baseline-current.json")
DEFAULT_ALLOWED_DROP = Decimal("0.25")
DEFAULT_COVERAGE_COMMAND = "coverage run -m pytest -q"
DEFAULT_COVERAGE_SOURCE = ["quantleet"]

ExitCode = Literal[0, 1, 2, 3]
Decision = Literal["raised", "unchanged", "tolerated", "failed", "created", "refused"]


@dataclass(frozen=True)
class Baseline:
    coverage_percent: Decimal
    allowed_drop: Decimal


@dataclass(frozen=True)
class Evaluation:
    decision: Decision
    baseline_percent: Decimal | None
    current_percent: Decimal
    drop: Decimal
    allowed_drop: Decimal
    exit_code: ExitCode


class CoverageBaselineError(Exception):
    """Operational error in the coverage baseline harness."""


def decimal_from_json(value: object, *, field_name: str) -> Decimal:
    if not isinstance(value, int | float | str):
        raise CoverageBaselineError(f"{field_name} must be a number")
    try:
        parsed = Decimal(str(value))
    except InvalidOperation as exc:
        raise CoverageBaselineError(f"{field_name} must be a valid number") from exc
    if not parsed.is_finite():
        raise CoverageBaselineError(f"{field_name} must be finite")
    return parsed


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise CoverageBaselineError(f"missing file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise CoverageBaselineError(f"invalid JSON in {path}: {exc.msg}") from exc
    if not isinstance(data, dict):
        raise CoverageBaselineError(f"{path} must contain a JSON object")
    return data


def read_current_percent(path: Path) -> Decimal:
    data = load_json(path)
    totals = data.get("totals")
    if not isinstance(totals, dict):
        raise CoverageBaselineError(f"{path} is missing totals")
    return decimal_from_json(totals.get("percent_covered"), field_name="totals.percent_covered")


def read_baseline(path: Path) -> Baseline:
    data = load_json(path)
    coverage_percent = decimal_from_json(
        data.get("coverage_percent"),
        field_name="coverage_percent",
    )
    allowed_drop = decimal_from_json(
        data.get("allowed_drop", DEFAULT_ALLOWED_DROP),
        field_name="allowed_drop",
    )
    return Baseline(coverage_percent=coverage_percent, allowed_drop=allowed_drop)


def current_commit() -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def baseline_payload(current_percent: Decimal, *, allowed_drop: Decimal) -> dict[str, object]:
    payload: dict[str, object] = {
        "schema_version": SCHEMA_VERSION,
        "baseline_commit": current_commit(),
        "coverage_percent": float(current_percent),
        "allowed_drop": float(allowed_drop),
        "coverage_tool": "coverage.py",
        "coverage_command": DEFAULT_COVERAGE_COMMAND,
        "coverage_run_branch": True,
        "coverage_run_source": DEFAULT_COVERAGE_SOURCE,
    }
    return payload


def write_baseline(path: Path, current_percent: Decimal, *, allowed_drop: Decimal) -> None:
    payload = baseline_payload(current_percent, allowed_drop=allowed_drop)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_name(f".{path.name}.tmp")
    temporary_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    replace(temporary_path, path)


def generate_current_json(path: Path) -> None:
    if not Path(".coverage").exists():
        raise CoverageBaselineError("missing .coverage; run through coverage-gates first")
    result = subprocess.run(
        ["coverage", "json", "-o", str(path)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        output = (result.stderr or result.stdout).strip()
        raise CoverageBaselineError(f"coverage json failed: {output}")


def evaluate_check(
    baseline_path: Path,
    current_json_path: Path,
    *,
    allowed_drop: Decimal,
) -> Evaluation:
    baseline = read_baseline(baseline_path)
    current_percent = read_current_percent(current_json_path)
    effective_allowed_drop = allowed_drop
    drop = baseline.coverage_percent - current_percent

    if current_percent > baseline.coverage_percent:
        write_baseline(baseline_path, current_percent, allowed_drop=effective_allowed_drop)
        return Evaluation(
            decision="raised",
            baseline_percent=baseline.coverage_percent,
            current_percent=current_percent,
            drop=drop,
            allowed_drop=effective_allowed_drop,
            exit_code=0,
        )
    if drop > effective_allowed_drop:
        return Evaluation(
            decision="failed",
            baseline_percent=baseline.coverage_percent,
            current_percent=current_percent,
            drop=drop,
            allowed_drop=effective_allowed_drop,
            exit_code=2,
        )
    decision: Decision = "unchanged" if drop == Decimal("0") else "tolerated"
    return Evaluation(
        decision=decision,
        baseline_percent=baseline.coverage_percent,
        current_percent=current_percent,
        drop=drop,
        allowed_drop=effective_allowed_drop,
        exit_code=0,
    )


def evaluate_update(
    baseline_path: Path,
    current_json_path: Path,
    *,
    allowed_drop: Decimal,
) -> Evaluation:
    current_percent = read_current_percent(current_json_path)
    if not baseline_path.exists():
        write_baseline(baseline_path, current_percent, allowed_drop=allowed_drop)
        return Evaluation(
            decision="created",
            baseline_percent=None,
            current_percent=current_percent,
            drop=Decimal("0"),
            allowed_drop=allowed_drop,
            exit_code=0,
        )

    baseline = read_baseline(baseline_path)
    drop = baseline.coverage_percent - current_percent
    if current_percent > baseline.coverage_percent:
        write_baseline(baseline_path, current_percent, allowed_drop=allowed_drop)
        return Evaluation(
            decision="raised",
            baseline_percent=baseline.coverage_percent,
            current_percent=current_percent,
            drop=drop,
            allowed_drop=allowed_drop,
            exit_code=0,
        )
    if current_percent < baseline.coverage_percent:
        return Evaluation(
            decision="refused",
            baseline_percent=baseline.coverage_percent,
            current_percent=current_percent,
            drop=drop,
            allowed_drop=allowed_drop,
            exit_code=3,
        )
    return Evaluation(
        decision="unchanged",
        baseline_percent=baseline.coverage_percent,
        current_percent=current_percent,
        drop=Decimal("0"),
        allowed_drop=allowed_drop,
        exit_code=0,
    )


def format_decimal(value: Decimal) -> str:
    return f"{value:.6f}"


def format_evaluation(evaluation: Evaluation, *, baseline_path: Path) -> str:
    baseline = (
        "none"
        if evaluation.baseline_percent is None
        else f"{format_decimal(evaluation.baseline_percent)}%"
    )
    return (
        f"coverage baseline {evaluation.decision}: "
        f"baseline={baseline}, current={format_decimal(evaluation.current_percent)}%, "
        f"drop={format_decimal(evaluation.drop)} percentage points, "
        f"allowed={format_decimal(evaluation.allowed_drop)}, source={baseline_path}"
    )


def parse_decimal(value: str) -> Decimal:
    try:
        parsed = Decimal(value)
    except InvalidOperation as exc:
        raise argparse.ArgumentTypeError(f"invalid decimal value: {value}") from exc
    if not parsed.is_finite():
        raise argparse.ArgumentTypeError(f"decimal value must be finite: {value}")
    return parsed


def parser() -> argparse.ArgumentParser:
    argument_parser = argparse.ArgumentParser(
        description="Check and ratchet the committed coverage baseline.",
    )
    argument_parser.add_argument("mode", choices=("check", "update"))
    argument_parser.add_argument(
        "--baseline",
        type=Path,
        default=DEFAULT_BASELINE_PATH,
        help="Committed coverage baseline JSON path",
    )
    argument_parser.add_argument(
        "--current-json",
        type=Path,
        default=DEFAULT_CURRENT_JSON_PATH,
        help="Temporary coverage.py JSON report path",
    )
    argument_parser.add_argument(
        "--allowed-drop",
        type=parse_decimal,
        default=DEFAULT_ALLOWED_DROP,
        help="Allowed coverage drop in percentage points",
    )
    argument_parser.add_argument(
        "--keep-current-json",
        action="store_true",
        help="Keep the generated current coverage JSON report for debugging",
    )
    return argument_parser


def run(args: argparse.Namespace) -> ExitCode:
    generated_current_json = False
    current_json_existed = args.current_json.exists()
    try:
        generate_current_json(args.current_json)
        generated_current_json = True
        if args.mode == "check":
            evaluation = evaluate_check(
                args.baseline,
                args.current_json,
                allowed_drop=args.allowed_drop,
            )
        else:
            evaluation = evaluate_update(
                args.baseline,
                args.current_json,
                allowed_drop=args.allowed_drop,
            )
    except CoverageBaselineError as exc:
        print(f"coverage baseline error: {exc}")
        return 1
    finally:
        current_json = getattr(args, "current_json", None)
        if (
            generated_current_json
            and not current_json_existed
            and not getattr(args, "keep_current_json", False)
            and isinstance(current_json, Path)
        ):
            current_json.unlink(missing_ok=True)

    print(format_evaluation(evaluation, baseline_path=args.baseline))
    return evaluation.exit_code


def main() -> int:
    return run(parser().parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
