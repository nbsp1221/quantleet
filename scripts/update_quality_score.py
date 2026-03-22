from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from quantcraft._repo_tools import collect_quality_issues, quality_score_snapshot_for_date


def build_quality_score_report(root: Path, *, today: date | None = None) -> dict[str, object]:
    effective_today = today or date.today()
    quality_issues = collect_quality_issues(root, today=effective_today)
    quality_score = quality_score_snapshot_for_date(root, today=effective_today)
    quality_score["validation"]["issue_count"] = len(quality_issues)
    return {
        "quality_score": quality_score,
        "quality_validation": quality_score["validation"],
        "quality_issues": quality_issues,
    }


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    print(json.dumps(build_quality_score_report(root), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
