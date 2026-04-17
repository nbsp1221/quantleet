# Active Plan

- Date: 2026-04-15
- Task: cross-engine validation for real-data limit-order regressions
- Status: `complete`
- Risk class: `Tier B`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal: Validate whether `quantcraft`'s future real-data limit-order canonical regressions can be trusted by comparing the same dataset and strategy logic against multiple external backtesting libraries before freezing any new golden results.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/plans/2026-04-14-limit-strategy-regression-design.md`
- Why these are governing:
  - they define the repo workflow, safety boundaries, reproducibility expectations, current backtest scope, and the approved limit-strategy regression set
- In-repo scope:
  - this active plan artifact
  - optional repo-local notes that summarize experiment results
  - later code or docs changes only if the experiment justifies them
- Out-of-repo scope:
  - use `/tmp` for temporary experiment code and environments
  - task-driven web research to select comparator libraries from official documentation
  - install and run external Python packages with `uv`
- Tier A progression requested: `no`
- Approval record, if required:
  - requestor: user
  - human approver: `Naki`
  - countersignature or equivalent verification marker: interactive user approval in chat on 2026-04-15 after `git config user.name` returned `Naki`
  - scope granted: `/tmp` experimental workspace use, task-driven web research, external package installation with `uv`, and cross-engine backtest comparison using the checked-in BTC USD-M 1h 2025 fixture
  - expiration: 2026-04-15 end of current session
  - audit reference or sanitized audit link: this active plan plus the recorded approval in session chat
- Verification commands:
  - `python --version`
  - `/tmp` experiment scripts executed with `uv run ...`
  - `uv run pytest tests/integration/research -q`
  - `git diff -- docs/plans/2026-04-15-limit-cross-engine-experiment.md`
- Success criteria:
  - select at least three reasonable external comparator libraries with official documented limit-order support
  - run the shared BTC USD-M 1h 2025 fixture through `quantcraft` and the comparator libraries for the approved limit strategy set or the maximal subset that can be expressed comparably
  - capture where results align, differ slightly, or diverge materially
  - identify whether divergences appear to come from engine semantics, library defaults, or strategy-translation constraints
  - produce a clear recommendation for whether `quantcraft` values are trustworthy enough to freeze as canonical regressions
- Out of scope:
  - live trading
  - secrets or external account usage
  - claiming Tier A completion

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice: The experiment is complete only if it produces evidence-bearing cross-engine comparisons that can either support or block freezing `quantcraft` limit-order golden results.
- Acceptance artifact location: this active plan plus any linked result notes created during the experiment
- How the generator and evaluator agreed on done before execution: at least three external comparator libraries must be investigated from official docs first, and actual run outputs must be reviewed before any trust claim is made
- Checks the evaluator will use:
  - official-doc evidence for selected libraries
  - fresh run outputs from `/tmp` experiment scripts
  - comparison tables or normalized result summaries
  - confirmation that repo-local tests still pass if repo files change
- Auto-fail conditions:
  - freezing or endorsing `quantcraft` limit golden values without external comparison evidence
  - relying on libraries that cannot express comparable limit semantics without clearly labeling the mismatch
  - mixing unsupported assumptions into the comparison without documentation

## Generator Work Log

- Planned slice order:
  1. choose comparator libraries from official docs
  2. scaffold `/tmp` experiment workspace with `uv`
  3. normalize the shared dataset for each engine
  4. implement comparable versions of the approved limit strategies
  5. run experiments and collect outputs
  6. compare results and summarize trust implications
- Notes:
  - if a library cannot support a strategy or cost model comparably, record the limitation rather than forcing a bad comparison
- Blockers or scope changes:
  - 2026-04-15 scope change approved in-session by the user:
    - add `NautilusTrader` as an explicit comparator because its architecture is philosophically closest to `quantcraft`
    - rerun the comparison with non-zero cost assumptions:
      - slippage: `1 tick`
      - fee rate: `0.04%`
    - treat the prior zero-cost run as an exploratory baseline, not the final trust decision

## Evaluator Review

- Findings:
  - initial zero-cost baseline was completed, but the user explicitly rejected zero slippage/fees as insufficient for the trust decision
  - the follow-up run was completed with:
    - fee rate `0.04%`
    - slippage `1 tick`
    - `NautilusTrader` added as an explicit comparator
  - `Backtrader` and `PyAlgoTrade` formed a tight conservative cluster in the cost run
  - `quantcraft` remained materially more optimistic than that conservative cluster on all three approved strategies
  - `NautilusTrader` was successfully ported for the EMA pullback strategy and landed extremely close to `quantcraft`, which is evidence that `quantcraft` may be closer to an execution-engine style optimistic fill philosophy than to conservative bar-backtester semantics
  - the current Nautilus ports for the other two strategies are not yet apples-to-apples enough to use as decisive validation for the whole strategy set
  - the experiment still does not support freezing `quantcraft` limit-order golden results yet; a semantics decision is needed first
- Verification evidence:
  - zero-cost baseline evidence recorded in `docs/plans/2026-04-15-limit-cross-engine-results.md`
  - cost-adjusted rerun output for `quantcraft`, `backtrader`, and `pyalgotrade`
  - NautilusTrader successful EMA pullback run with a custom market-only one-tick slippage fill model
- Final disposition:
  - complete for the cost-adjusted comparison slice; canonical freezing remains blocked pending a semantics decision and a cleaner all-strategy Nautilus comparison
