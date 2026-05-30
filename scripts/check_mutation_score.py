from __future__ import annotations

import argparse
import json
import sys
import tomllib
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STATS = ROOT / "mutants" / "mutmut-cicd-stats.json"
PYPROJECT = ROOT / "pyproject.toml"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail when the exported mutmut CI score is below the configured floor."
    )
    parser.add_argument(
        "--stats-file",
        type=Path,
        default=DEFAULT_STATS,
        help="Path to mutmut-cicd-stats.json.",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=None,
        help="Override [tool.mutation_score].fail_under.",
    )
    args = parser.parse_args()

    threshold = args.threshold if args.threshold is not None else _configured_threshold()
    stats = _load_stats(args.stats_file)
    return _evaluate(stats, threshold)


def _configured_threshold() -> float:
    config = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    score_config = config.get("tool", {}).get("mutation_score", {})
    threshold = score_config.get("fail_under")
    if not isinstance(threshold, int | float):
        raise SystemExit("[tool.mutation_score].fail_under must be a number")
    return float(threshold)


def _load_stats(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"mutmut stats file not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _evaluate(stats: dict[str, Any], threshold: float) -> int:
    total = int(stats.get("total", 0))
    killed = int(stats.get("killed", 0))
    survived = int(stats.get("survived", 0))
    no_tests = int(stats.get("no_tests", 0))
    suspicious = int(stats.get("suspicious", 0))
    timeout = int(stats.get("timeout", 0))
    segfault = int(stats.get("segfault", 0))
    score = killed / total * 100 if total else 0.0

    print(
        "mutation score: "
        f"total={total} killed={killed} survived={survived} "
        f"no_tests={no_tests} suspicious={suspicious} timeout={timeout} "
        f"segfault={segfault} score={score:.2f}% threshold={threshold:g}%",
        flush=True,
    )

    failures: dict[str, float | int] = {}
    if total == 0:
        failures["total"] = total
    if no_tests:
        failures["no_tests"] = no_tests
    if score < threshold:
        failures["score"] = round(score, 2)
    for key, value in {
        "suspicious": suspicious,
        "timeout": timeout,
        "segfault": segfault,
    }.items():
        if value:
            failures[key] = value

    if failures:
        print(f"mutation score gate failed: {failures}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
