from __future__ import annotations

from pathlib import Path

from quantcraft._repo_tools import (
    collect_architecture_issues,
    collect_doc_issues,
)


def collect_issues(root: Path) -> list[str]:
    return [
        *collect_doc_issues(root),
        *collect_architecture_issues(root),
    ]


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    issues = collect_issues(root)
    if issues:
        for issue in issues:
            print(issue)
        return 1

    print("repository checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
