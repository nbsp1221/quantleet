from __future__ import annotations

from pathlib import Path

from quantcraft._repo_tools import (
    TIER_A,
    collect_architecture_issues,
    validate_domain_dependency,
)

__all__ = ["TIER_A", "collect_issues", "main", "validate_domain_dependency"]


def collect_issues(root: Path) -> list[str]:
    return collect_architecture_issues(root)


def main() -> int:
    issues = collect_issues(Path(__file__).resolve().parents[1])
    if issues:
        for issue in issues:
            print(issue)
        return 1

    print("architecture checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
