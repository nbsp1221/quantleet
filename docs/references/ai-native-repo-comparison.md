# AI-Native Repo Comparison

This note records a 2026-04-04 comparison between `quantcraft` and a sample of actively maintained, high-visibility AI-native repositories.

The goal is not to rank projects.
The goal is to answer a narrower question:

- when repositories are themselves part of an AI-agent operating environment, what patterns actually appear in the wild?

## Selection Method

Repositories were selected using the following criteria:

- public open-source repository
- clearly AI-native product, agent, or AI-check workflow
- meaningful adoption signal by GitHub stars
- evidence of recent maintenance from `pushed_at`
- repository cloned locally and inspected directly

Metadata below is from the GitHub API as observed on 2026-04-04 UTC.

## Repositories Sampled

| Repo | Focus | Stars | Forks | `pushed_at` | Local commit inspected |
| --- | --- | ---: | ---: | --- | --- |
| `openclaw/openclaw` | personal AI assistant platform | 347,376 | 69,308 | 2026-04-04T04:08:09Z | `53b5b1b32d3d3e1d38f6f36bb82f6d00e45c399c` |
| `sst/opencode` | open-source coding agent | 136,675 | 14,938 | 2026-04-04T03:26:31Z | `00fa68b3a70facfe942523d35e2ecbf8456f0d49` |
| `All-Hands-AI/OpenHands` | AI-driven development platform | 70,534 | 8,836 | 2026-04-04T02:49:57Z | `8ce3089a68018c507025c7410ee3ba25856b23fd` |
| `Aider-AI/aider` | terminal AI pair programming | 42,775 | 4,126 | 2026-03-17T01:21:34Z | `bdb4d9ff8ef88c3015a9845119bff37f49c93d7b` |
| `continuedev/continue` | source-controlled AI checks and CI enforcement | 32,273 | 4,329 | 2026-04-03T09:20:35Z | `a1ead04122664b308131bdf1c3345ead00146bbc` |

## Comparison Dimensions

The same questions were applied to each repository:

1. Does the repo contain an explicit agent intent layer such as `AGENTS.md`, `CLAUDE.md`, or structured prompt/check directories?
2. Does it rely mostly on traditional tests and contributor docs, or does it also encode AI review/check behavior in-repo?
3. Does it use repo-local rules to reduce AI slop or documentation drift?
4. How centralized or fragmented is its command/test surface?

## Findings

### 1. AI-native repos are not all managed the same way

The sample splits into at least three shapes:

- **agent-map heavy**: `openclaw`, `opencode`
- **hybrid traditional + agent automation**: `openhands`
- **traditional repo management despite AI product focus**: `aider`
- **AI checks as first-class repo artifact**: `continue`

This means there is no single industry-standard "AI harness repo layout" yet.

## Repo Notes

### OpenClaw

Evidence:

- top-level `AGENTS.md` and `CLAUDE.md` both exist
- local scan found `11` `AGENTS.md` files and `11` `CLAUDE.md` files
- repo contains `.agents/`, `.codex/`, `skills/`, and `docs/`
- guidance is boundary-heavy and highly specific
- test guidance includes coverage thresholds and test-performance guardrails
- CI includes install smoke and sandbox smoke workflows

Concrete evidence:

- top-level intent map: `https://github.com/openclaw/openclaw/blob/53b5b1b32d3d3e1d38f6f36bb82f6d00e45c399c/AGENTS.md`
- mirrored Claude file: `https://github.com/openclaw/openclaw/blob/53b5b1b32d3d3e1d38f6f36bb82f6d00e45c399c/CLAUDE.md`
- install smoke workflow: `https://github.com/openclaw/openclaw/blob/53b5b1b32d3d3e1d38f6f36bb82f6d00e45c399c/.github/workflows/install-smoke.yml`

What is distinctive:

- this is the closest sample to a full agent-operating-system repo
- instructions are hierarchical and duplicated across agent brands (`AGENTS.md` and `CLAUDE.md`)
- the repo mixes classic CI smoke tests with very detailed agent-facing invariants

Comparison to `quantcraft`:

- similar: in-repo intent layer, explicit testing guidance, smoke checks, strong architecture rules
- different: much broader scale, many more local boundary guides, much more operational/runtime complexity

### OpenCode

Evidence:

- top-level `AGENTS.md` exists
- local scan found `7` `AGENTS.md` files
- repo contains `.opencode/`
- root `package.json` explicitly blocks running tests from repo root with `test: echo 'do not run tests from root' && exit 1`
- package-local AGENTS files provide narrower instructions

Concrete evidence:

- top-level AGENTS: `https://github.com/sst/opencode/blob/00fa68b3a70facfe942523d35e2ecbf8456f0d49/AGENTS.md`
- package-local AGENTS: `https://github.com/sst/opencode/blob/00fa68b3a70facfe942523d35e2ecbf8456f0d49/packages/opencode/AGENTS.md`

What is distinctive:

- strong agent instruction layer, but thinner system-of-record docs than `quantcraft`
- command surface is intentionally decentralized to package directories
- the repo appears to optimize for fast local development in package scope rather than one central verification bundle

Comparison to `quantcraft`:

- similar: explicit agent instructions embedded in repo
- different: less central harness unification, less obvious repository-rule test layer, fewer root-level verification contracts

### OpenHands

Evidence:

- top-level `AGENTS.md` exists
- repo includes `Makefile`, `pyproject.toml`, `pytest.ini`, `scripts/`, `tests/`, and `.agents/`
- GitHub workflows include `pr-review-by-openhands.yml` and `pr-review-evaluation.yml`
- AGENTS guidance is detailed, but still looks closer to an expanded contributor guide than to a full doc-as-system-of-record hierarchy

Concrete evidence:

- AGENTS: `https://github.com/All-Hands-AI/OpenHands/blob/8ce3089a68018c507025c7410ee3ba25856b23fd/AGENTS.md`
- PR review workflow: `https://github.com/All-Hands-AI/OpenHands/blob/8ce3089a68018c507025c7410ee3ba25856b23fd/.github/workflows/pr-review-by-openhands.yml`

What is distinctive:

- combines conventional engineering workflows with explicit agent review automation
- agent review is part of GitHub workflow execution, not just local guidance
- test and build surface is broad and conventional: frontend tests, backend tests, e2e, enterprise checks

Comparison to `quantcraft`:

- similar: AI review/check activity is first-class, explicit local commands exist
- different: much more CI/workflow oriented, less dependent on repository-structure tests as the core harness concept

### Aider

Evidence:

- no `AGENTS.md` found
- no `CLAUDE.md` found
- repo uses a conventional `CONTRIBUTING.md`, `tests/`, `benchmark/`, `pytest.ini`, and workflows
- benchmark harness is treated as a major artifact

Concrete evidence:

- contributing guide: `https://github.com/Aider-AI/aider/blob/bdb4d9ff8ef88c3015a9845119bff37f49c93d7b/CONTRIBUTING.md`
- benchmark harness: `https://github.com/Aider-AI/aider/blob/bdb4d9ff8ef88c3015a9845119bff37f49c93d7b/benchmark/README.md`

What is distinctive:

- despite being an AI coding product, the repo itself is managed much more like a traditional OSS project
- quantitative benchmark infrastructure is prominent
- there is less evidence of a repo-local intent layer aimed at coding agents

Comparison to `quantcraft`:

- similar: benchmarks and tests matter
- different: much less agent-instruction scaffolding, more conventional contributor workflow

### Continue

Evidence:

- product positioning is itself "source-controlled AI checks, enforceable in CI"
- repo includes `.continue/checks/`, `.continue/agents/`, `.continue/rules/`, `.continue/prompts/`, and `skills/`
- checks include `anti-slop`, `security-audit`, and `update-agents-md`
- `update-agents-md` explicitly treats AGENTS/CLAUDE files as an "intent layer"

Concrete evidence:

- README: `https://github.com/continuedev/continue/blob/a1ead04122664b308131bdf1c3345ead00146bbc/README.md`
- anti-slop check: `https://github.com/continuedev/continue/blob/a1ead04122664b308131bdf1c3345ead00146bbc/.continue/checks/anti-slop.md`
- AGENTS sync check: `https://github.com/continuedev/continue/blob/a1ead04122664b308131bdf1c3345ead00146bbc/.continue/checks/update-agents-md.md`
- test coverage agent: `https://github.com/continuedev/continue/blob/a1ead04122664b308131bdf1c3345ead00146bbc/.continue/agents/test-coverage.md`

What is distinctive:

- this sample is the clearest direct proof that AI review/check definitions are being versioned like code
- it explicitly encodes anti-slop and intent-layer synchronization as machine-enforced review behaviors
- it makes the AI harness part of the product and part of the repo governance model

Comparison to `quantcraft`:

- similar: strong emphasis on in-repo agent guidance and mechanical enforcement
- different: `continue` externalizes much of the harness into check/agent markdown files rather than repo-structure tests and command bundles

## Cross-Sample Patterns

### Pattern 1: Explicit agent-facing repo instructions are real, not hypothetical

Observed in:

- `openclaw`
- `opencode`
- `openhands`
- `continue` at least in partial or scoped form

This supports the idea that repo-local intent files are a real emerging pattern for AI-native projects.

### Pattern 2: AI-native repos still keep traditional tests and CI

Observed in:

- `openhands`
- `aider`
- `openclaw`
- `continue`

This supports a narrower conclusion:

- AI-native repos do not replace ordinary tests with prompt files
- they layer agent instructions and AI checks on top of conventional test/CI infrastructure

### Pattern 3: Anti-slop / drift management is becoming explicit in some repos

Observed clearly in:

- `continue` via `.continue/checks/anti-slop.md` and `.continue/checks/update-agents-md.md`
- `openclaw` via large intent-layer files and many test/perf guardrails

This is directly relevant to `quantcraft`, because it confirms that:

- the need for cleanup and anti-drift mechanisms is not unique to this repository
- some AI-native projects already encode those concerns explicitly

### Pattern 4: Centralization varies a lot

Examples:

- `quantcraft`: one repo-local harness contract with `poe`, `scripts/`, indexed docs, and structure tests
- `openclaw`: many local intent files plus CI smokes and skill directories
- `opencode`: package-local execution and package-local instructions
- `openhands`: Makefile + workflows + tests + one top-level AGENTS
- `aider`: mostly conventional OSS structure
- `continue`: AI checks and agent definitions in dedicated hidden directories

So the evidence does **not** support one mandatory best-practice layout.

## Implications For `quantcraft`

Evidence-supported takeaways:

1. `quantcraft` is not strange for having repo-local agent guidance. Multiple AI-native repos do this.
2. `quantcraft` is more documentation-and-structure-test heavy than several sampled repos.
3. `quantcraft` is less explicit than `continue` about anti-slop and automated intent-sync checks as first-class AI review artifacts.
4. `quantcraft` is smaller and more centralized than `openclaw`, which likely makes local reasoning easier but also concentrates duplication pressure into fewer files.
5. `quantcraft` is less conventional than `aider`, but more conventional than `continue` in how it encodes governance.

The highest-confidence synthesis is:

- `quantcraft` is not following a fake or imaginary pattern
- it is participating in a real emerging design space
- but different successful AI-native repos are making materially different choices about where to place the harness:
  - docs and structure tests
  - local intent files
  - CI review agents
  - source-controlled AI checks
  - benchmark harnesses

## Sources

### GitHub API metadata

- `https://api.github.com/repos/openclaw/openclaw`
- `https://api.github.com/repos/sst/opencode`
- `https://api.github.com/repos/All-Hands-AI/OpenHands`
- `https://api.github.com/repos/Aider-AI/aider`
- `https://api.github.com/repos/continuedev/continue`

### Repository pages inspected

- `https://github.com/openclaw/openclaw`
- `https://github.com/sst/opencode`
- `https://github.com/All-Hands-AI/OpenHands`
- `https://github.com/Aider-AI/aider`
- `https://github.com/continuedev/continue`
