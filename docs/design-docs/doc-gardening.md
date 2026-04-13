# Doc Gardening

This note defines the recurring cleanup loop for repository docs and routing
surfaces.

## Promotion Loop

1. When the same review finding repeats, update the relevant governing doc or
   route it into a narrow mechanical check.
2. If the rule is still judgment-heavy, update
   [golden-principles.md](golden-principles.md) or the relevant canonical doc.
3. If the rule is objective and cheap, promote it into `repo_check` or a
   structure test, following
   [architecture-governance.md](architecture-governance.md).
4. Remove workflow complexity only after a plan, trial, or repeated operation
   shows that the old control was not load-bearing.
5. When a control-plane artifact is retired from active use but kept for audit
   continuity, rewrite it as historical or advisory and move any still-useful
   rationale into the surviving governing docs first.
6. If a retired artifact no longer carries unique rationale and no active doc
   routes to it, prefer deletion over keeping a confusing second entry surface.

When the promoted artifact is a metric, benchmark, or new check, record:

- the protected behavior
- the measured proxy
- the likely gaming vector
- the decision the artifact should change
- the revalidation or removal condition

If those fields are not clear yet, keep the rule in docs or evaluator prompts
instead of promoting it into enforcement.

## Recurring Checks

- remove placeholder text
- keep indexes aligned with real files
- keep active plan, plan template, and trial pointers aligned with real files
- keep historical archive surfaces clearly marked as historical
- keep advisory governance artifacts clearly marked as non-authoritative
- capture repeated review comments as docs or checks
- remove stale proxies or checks that no longer change decisions

## Local Trigger

Until the repository has remote automation, doc gardening is a local
maintenance task that should run after major harness, architecture, or
workflow-authority changes.
