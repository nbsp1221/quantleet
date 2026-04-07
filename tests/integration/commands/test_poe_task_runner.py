from __future__ import annotations

import subprocess

from tests.support import ROOT


def test_poe_help_lists_required_tasks() -> None:
    result = subprocess.run(
        ["uv", "run", "poe", "--help"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    output = result.stdout + result.stderr
    for task_name in [
        "lint",
        "format",
        "typecheck",
        "test",
        "test-live",
        "coverage",
        "verify",
        "verify-runtime",
    ]:
        assert task_name in output
