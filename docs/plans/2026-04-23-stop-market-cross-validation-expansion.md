# Active Plan

- Date: `2026-04-23`
- Task: `Expand stop_market cross-validation to at least five comparator libraries`
- Status: `complete`
- Risk class: `Tier A`
- Requestor: `user`
- Owner: `Codex`

## Planner Contract

- Goal:
  - expand the existing stop-market cross-validation experiment from two
    comparator libraries to at least five comparator libraries
  - prefer runnable comparator engines that can express the same non-linked
    stop-market validation strategies against the shared BTC/USDT 1h dataset
  - if some candidate libraries are rejected, record why they were rejected and
    keep the final report focused on actual mismatch causes, not only on score
    counts
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/backtest-mvp.md`
  - `docs/product-specs/research-ergonomics.md`
  - `docs/design-docs/index.md`
  - `docs/design-docs/package-topology-and-naming.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/DESIGN.md`
  - `docs/PLANS.md`
  - `docs/plans/2026-04-23-stop-trigger-order-spec-design.md`
  - `docs/plans/2026-04-23-stop-trigger-order-test-matrix-design.md`
  - `docs/plans/2026-04-23-stop-market-real-world-strategy-candidates.md`
  - `docs/plans/2026-04-23-stop-market-cross-validation-execution.md`
  - `docs/plans/2026-04-23-stop-market-cross-validation-rerun.md`
- Why these are governing:
  - They define the shipped `stop_market` scope, the non-linked validation
    strategy set, the required review/verification workflow, and the prior
    comparator findings that this expansion will supersede.
- In-repo scope:
  - add this active plan
  - update plan findings after the expanded experiment
- Out-of-repo scope:
  - modify the temporary `/tmp/quantcraft-stop-xval` harness
  - install additional local or remote comparator dependencies into the `/tmp`
    uv project when needed
  - execute expanded comparator runs there
  - update temporary result artifacts there
- Tier A progression requested: `yes`
- Approval record, if required:
  - Tier A and scope-expansion approval record:
    - Requestor: `Naki (thread user)`
    - Human approver: `Naki (thread user)`
    - Verification marker:
      explicit thread direction on `2026-04-23` to rerun the stop-market
      experiment with at least five comparator libraries and report the mismatch
      reasons again
    - Granted scope:
      repository-local plan updates, `/tmp` harness edits, local comparator
      execution, and task-driven package installation/network access required to
      assemble the comparator set
    - Expiration:
      end of this expanded cross-validation slice
    - Audit reference:
      this active plan plus the prior stop-market cross-validation plans and
      stop-trigger governing documents
- Verification commands:
  - `uv run poe repo-check`
  - expanded rerun command to be recorded after execution
- Success criteria:
  - at least five comparator libraries are either executed successfully or
    explicitly triaged with concrete feasibility reasons
  - final report distinguishes actual experimental comparators from
    code-reading-only comparators
  - final report explains mismatch causes in plain language and identifies any
    majority stop-fill pattern across the successfully executed comparator set
- Out of scope:
  - changing shipped `quantcraft` runtime code
  - implementing `stop_limit`, linked orders, or new order families

## Evaluator Acceptance Contract

- Evaluator owner: `Codex`
- Evaluator-owned done contract for this slice:
  - accept only if the expanded experiment is rerun from fresh artifacts and
    the final report clearly states both the executed comparator set and the
    observed stop-fill pattern
- Acceptance artifact location:
  - this active plan
  - temporary `/tmp/quantcraft-stop-xval/results/` artifacts
- How the generator and evaluator agreed on done before execution:
  - done means the comparator set has been materially widened beyond the
    current two-engine sample and the conclusions are supported by fresh output
- Checks the evaluator will use:
  - inspect the expanded harness comparator list
  - inspect fresh result artifacts
  - run `uv run poe repo-check`
- Auto-fail conditions:
  - claiming five comparators without fresh executable evidence
  - blending “code-reading evidence” with “actual rerun evidence” without
    explicitly separating them

## Generator Work Log

- Planned slice order:
  1. evaluate feasible additional comparator libraries
  2. extend the `/tmp` harness to the chosen comparator set
  3. rerun the experiment and summarize differences
  4. update this plan with evaluator findings and verification evidence
- Notes:
  - exact equality is not the target; mismatch explanation is the target
  - if a library cannot express the exact strategy surface or is operationally
    infeasible in the allotted slice, record the rejection reason rather than
    silently omitting it
- Blockers or scope changes:
  - None yet.

## Evaluator Review

- Findings:
  - Fresh expanded stop-fill stress rerun focused on
    `mean_reversion_market` was executed from:
    - `/tmp/quantcraft-stop-xval/run_stop_fill_expansion.py`
    - `/tmp/quantcraft-stop-xval-nautilus/run_nautilus_mean_reversion.py`
  - Successfully executed comparator engines:
    - `backtesting.py`
    - `backtrader`
    - `vectorbt`
    - `nautilus`
  - Repository engine under test:
    - `quantcraft`
  - Triage-only comparator outcomes:
    - `pyalgotrade`
      - strategy translation did not produce credible closed-trade output for
        the stop-heavy signal-driven pattern
      - it opened a position but never closed trades under this translation, so
        it was excluded from trend judgment
    - `zipline-reloaded`
      - Python 3.13 compatibility issues (`distutils`/`interface`) blocked a
        reliable runner despite separate-environment attempts
    - `nautilus_trader` source install
      - source build blocked on missing `clang`, but registry wheel install in
        a separate environment succeeded and was used for the final run
    - `freqtrade`
      - installed package line available in the main temp env was not Python
        3.13 compatible (`typing.io` import failure), so it was not promoted to
        a runnable comparator
  - Trend judgment from the successful comparator set:
    - `backtesting.py` matched `quantcraft` very closely on many early trades
      and remained less conservative than `backtrader` / `vectorbt`
    - `nautilus` also tracked `quantcraft` much more closely than the more
      conservative comparators
    - `backtrader` and `vectorbt` realized worse stop exits more often
    - therefore the prior “all comparators are more conservative” framing does
      not hold once the sample is widened
  - Practical product judgment:
    - the widened sample suggests `quantcraft` is not an outlier by itself
    - the comparator landscape appears split:
      - trigger-price-friendly or near-trigger models:
        `quantcraft`, `backtesting.py`, `nautilus`
      - more conservative post-cross models:
        `backtrader`, `vectorbt`
- Verification evidence:
  - Repo/document lane:
    - `uv run poe repo-check`
    - Result: `repository checks passed`
  - Expanded rerun command:
    - `cd /tmp/quantcraft-stop-xval && uv run python run_stop_fill_expansion.py`
  - Separate Nautilus runner command:
    - `cd /tmp/quantcraft-stop-xval-nautilus && uv run python run_nautilus_mean_reversion.py`
  - Temporary result artifacts:
    - `/tmp/quantcraft-stop-xval/results/stop_fill_expansion.json`
    - `/tmp/quantcraft-stop-xval/results/cross_validation_results.json`
    - `/tmp/quantcraft-stop-xval/results/summary.md`
- Final disposition:
  - `accepted`
