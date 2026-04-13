# Golden Principles

This note captures the repository-level cleanup rules that should survive any
one slice, reviewer, or prompt.

## Principles

- Keep durable rules in repository docs or checks, not in chat memory.
- Keep workflow rules self-contained at the repo boundary; host-specific command
  names are implementation details, not canonical repo instructions.
- When the same review finding repeats, promote it into the smallest governing
  doc or check that actually reduces future ambiguity.
- If the finding is objective and cheap to check, promote it into `repo_check`
  or a structure test.
- If the finding still needs judgment, promote it into a short canonical doc
  such as this one or the task-specific design/spec doc.
- Remove complexity only after proof shows the older rule or artifact was not
  protecting a live failure mode.
- If a retired artifact must stay in the repo for audit continuity, make its
  historical or advisory status explicit and route future decisions elsewhere.
- For evaluation and reviewer policy details, defer to
  [architecture-governance.md](architecture-governance.md).
- Treat reviewer output as strongest when it names a concrete failure mode
  rather than generic approval.
