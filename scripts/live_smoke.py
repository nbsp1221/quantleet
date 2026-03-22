from __future__ import annotations

from quantcraft._repo_tools import run_live_smoke


def main() -> int:
    results = run_live_smoke()
    for result in results:
        print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
