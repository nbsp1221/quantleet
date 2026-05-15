from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def test_walk_forward_resume_docs_avoid_deferred_public_patterns() -> None:
    text = (ROOT / "docs/product-specs/walk-forward-analysis-resume.md").read_text()
    code_examples = "\n".join(re.findall(r"```(?:python)?\n(.*?)```", text, flags=re.S))

    forbidden = [
        "source=",
        'objective="sharpe"',
        "oos_report",
        "stitched OOS equity",
        "paper trading",
        "live trading",
    ]
    for phrase in forbidden:
        assert phrase not in code_examples


def test_walk_forward_resume_docs_present_validation_not_recommendation() -> None:
    text = (ROOT / "docs/product-specs/walk-forward-analysis-resume.md").read_text()

    assert "validation evidence" in text
    assert "financial advice" in text
    assert "guarantee of future performance" in text
