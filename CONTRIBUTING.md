# Contributing

Quantleet is in its first public beta documentation phase. The current product
scope is single-symbol historical backtesting and quant research tooling.

## Setup

```bash
uv sync
uv run poe verify
```

Useful targeted checks:

```bash
uv run poe repo-check
uv run pytest tests/structure/docs tests/structure/repo -q
uv run pytest tests/smoke/local -q
```

Runtime-sensitive backtest or research changes may need the stronger lane:

```bash
uv run poe verify-runtime
```

## Documentation

Public user documentation lives in `docs/site`. Update those pages when a
public import, quickstart, example, or user-facing behavior changes.

Internal planning, product, design, research, and workflow records stay in their
existing directories. Do not turn internal plans into public user navigation.

## Issues

GitHub issue templates are not part of the first documentation cleanup slice.
Until they exist, include the following information manually.

For bugs:

- environment and Python version
- minimal reproduction
- expected behavior
- actual behavior
- relevant traceback or output

For feature requests:

- user problem
- proposed scope
- unsupported scope that should remain out of the request

For documentation issues:

- page path
- incorrect or missing text
- proposed correction when known

## Pull Requests

Pull requests should include:

- summary
- linked issue when applicable
- change type
- docs impact
- verification evidence
- changelog or release impact when applicable

If a change used AI-assisted or generated output, the human PR author must
review it line by line, understand it, verify it, and own the result. The human
author stands behind the change.

Changes under `trading` or `execution` have stricter review expectations because
they are safety-sensitive Tier A areas in this repository.
