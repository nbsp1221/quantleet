# Doc Gardening

This note defines the recurring cleanup loop for repository docs and lightweight quality tracking.

## Promotion Loop

1. When the same review finding repeats, add it to [../feedback-promotion-log.md](../feedback-promotion-log.md).
2. If the rule is still judgment-heavy, update [golden-principles.md](golden-principles.md) or the relevant canonical doc.
3. If the rule is objective and cheap, promote it into `repo_check` or a structure test, following [architecture-governance.md](architecture-governance.md).
4. If the promotion changes docs-system or verification evidence, update [`../QUALITY_SCORE.md`](../QUALITY_SCORE.md).

## Recurring Checks

- remove placeholder text
- keep indexes aligned with real files
- make historical plans discoverable
- update quality notes when the repository structure changes
- capture repeated review comments as docs or checks
- keep [../feedback-promotion-log.md](../feedback-promotion-log.md) aligned with promoted docs and checks

## Local Trigger

Until the repository has remote automation, doc gardening is a local maintenance task that should be run after major harness or architecture changes.
