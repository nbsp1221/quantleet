from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any, cast


def run_notebook_validation(root: Path) -> list[str]:
    try:
        import nbformat
        from nbclient import NotebookClient
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Notebook validation requires nbformat and nbclient in the current environment",
        ) from exc

    notebook_paths = sorted((root / "notebooks").glob("*.ipynb"))
    executed: list[str] = []
    read_notebook = cast(Callable[..., Any], nbformat.read)

    for path in notebook_paths:
        with path.open(encoding="utf-8") as handle:
            notebook = read_notebook(handle, as_version=4)
        client = NotebookClient(notebook, timeout=600, kernel_name="python3")
        client.execute()
        executed.append(path.name)

    return executed
