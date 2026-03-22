from __future__ import annotations

from pathlib import Path

from quantcraft._notebook_tools import run_notebook_validation


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    executed = run_notebook_validation(root)
    for notebook_name in executed:
        print(f"validated {notebook_name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
