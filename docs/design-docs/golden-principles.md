# Golden Principles

This note captures the repository-level cleanup rules that should survive any one slice, reviewer, or prompt.

## Principles

- Keep durable rules in repository docs or checks, not in chat memory.
- When the same review finding repeats, add it to [../feedback-promotion-log.md](../feedback-promotion-log.md).
- If the finding is objective and cheap to check, promote it into `repo_check` or a structure test.
- If the finding still needs judgment, promote it into a short canonical doc such as this one or the task-specific design/spec doc.
- Update [`../QUALITY_SCORE.md`](../QUALITY_SCORE.md) when the promotion changes docs-system or verification evidence.
- For evaluation and reviewer policy details, defer to [architecture-governance.md](architecture-governance.md).
- Treat reviewer output as strongest when it names a concrete failure mode rather than generic approval.
