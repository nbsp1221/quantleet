# Installation

Quantleet requires Python 3.13.

The first beta package is `0.1.0b1`. Once published, package users should
install that release from the configured Python package index.

With `uv`:

```bash
uv add quantleet==0.1.0b1
```

With `pip`:

```bash
python -m pip install quantleet==0.1.0b1
```

From a local checkout:

```bash
uv sync
uv run poe verify
```

For a faster local documentation and import check:

```bash
uv run poe repo-check
uv run pytest tests/smoke/local -q
```

The quickstart uses in-memory data and does not require live exchange
credentials.

Contributor setup and pull request expectations are covered in the repository
contribution guide.
