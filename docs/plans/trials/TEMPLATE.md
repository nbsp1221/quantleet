# Workflow Trial Or Exception Record

- Record type: `authority-trial` | `exception-record`
- Date:
- Task:
- Risk class: `Tier A` | `Tier B` | `Tier C`
- Operator:
- Operator familiarity with evaluated workflow:
- Human reviewer:
- Reviewer sign-off:

## Governing Spec

- Product or design spec:
- Why this is the governing spec:
- Repo-local hard-gate docs:

## Execution Status

- Trial fully executed: `yes` | `no`
- Stop point:
- Blocker or exception reason:
- Does this record count toward the migration evidence gate: `yes` | `no`

## Task And Scope

- Task description:
- In-repo scope:
- Out-of-repo scope requested: `none` | `requested`
- Tier A progression requested: `no` | `yes`

## Comparator Notes

| Comparator | Planning time | Clarifying loops | Review signal notes | Workflow friction notes |
| --- | --- | --- | --- | --- |
| Baseline current flow |  |  |  |  |
| Slim-local comparator |  |  |  |  |
| Candidate workflow |  |  |  |  |

## Hard Gates Invoked

- Architecture boundary checks:
- Runtime-sensitive verification:
- Live-test policy handling:
- Performance-check handling:
- Coverage or contract-test checks:
- Tier A approval gate:
- Non-repo or connector approval gate:

## Reviewer-Signal Rubric

| Field | Baseline | Slim-local | Candidate workflow | Result |
| --- | --- | --- | --- | --- |
| Actionable findings that changed the implementation or plan |  |  |  |  |
| False positives rejected by human review |  |  |  |  |
| Missed issues found later by tests or follow-up review |  |  |  |  |
| Governing spec and guardrails identified correctly |  |  |  |  |
| Approval-bypass or out-of-scope access blocked correctly |  |  |  |  |

## Approval-Sensitive Handling

### Non-Repo Access / Connector Use

- Attempted:
- Requestor:
- Scope granted:
- Allowed resources:
- Human approver:
- Countersignature or verification marker:
- Expiration:
- Audit reference or sanitized audit link:
- Gate response:

### Tier A Progression

- Attempted:
- Requestor:
- Scope granted:
- Human approver:
- Countersignature or verification marker:
- Approval record location:
- Expiration:
- Audit reference or sanitized audit link:
- Gate response:

## Sanitization

- Secrets, tokens, credential details, and connector configuration omitted:
  `yes` | `no`
- Approval record uses minimum necessary detail only: `yes` | `no`
- Sensitive evidence stored as sanitized reference only: `yes` | `no`
- Sanitized reference, if any:

## Operator-Effects Controls

- Comparator order:
- Same operator/reviewer skill bar used across comparators: `yes` | `no`
- Learning effects or order effects noted:

## Judgment

- Final judgment: `pass` | `fail`
- Why:
- Reviewer conclusion on workflow authority clarity:

Exception records that stop before a scored comparison should end in `fail`
or another explicitly non-passing disposition. They must not be written as
evidence-gate passes.
