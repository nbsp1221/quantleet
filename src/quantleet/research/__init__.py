from __future__ import annotations

from importlib import import_module

__all__ = ["GridSearchResult", "GridSearchRow", "ParameterStudy", "Strategy", "qc", "ta"]


def __getattr__(name: str) -> object:
    if name == "Strategy":
        return getattr(import_module("quantleet.research.strategy"), name)
    if name in {"GridSearchResult", "GridSearchRow", "ParameterStudy"}:
        return getattr(import_module("quantleet.research.parameter_exploration"), name)
    if name in {"qc", "ta"}:
        return import_module(f"quantleet.research.{name}")
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
