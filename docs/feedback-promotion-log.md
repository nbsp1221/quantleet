# Feedback Promotion Log

This artifact records repeated review findings that were promoted into repository docs or checks.

## Update Rule

- Add a row when the same finding appears twice or a single mistake justifies immediate promotion under [design-docs/architecture-governance.md](design-docs/architecture-governance.md).
- Link the doc or check that absorbed the rule so future agents can find the current source of truth.
- For metric-, benchmark-, or check-related findings, include the protected behavior, proxy risk, and revalidation/removal expectation in the promoted docs.

## Entries

| Date | Finding | Promotion | Status |
| --- | --- | --- | --- |
| 2026-03-22 | The garbage-collection loop for repeated review findings was implicit and easy to miss. | Promoted into [design-docs/golden-principles.md](design-docs/golden-principles.md), [design-docs/doc-gardening.md](design-docs/doc-gardening.md), and repo checks in `src/quantcraft/_repo_tools.py`. | active |
| 2026-04-02 | Proxy metrics and evaluator outputs could become fake rigor unless the repository records what behavior they protect, how they can be gamed, and when they should be removed. | Promoted into [design-docs/architecture-governance.md](design-docs/architecture-governance.md), [design-docs/doc-gardening.md](design-docs/doc-gardening.md), and the active anti-gaming execution plan. | active |
