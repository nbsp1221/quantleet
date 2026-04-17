from __future__ import annotations

from importlib import import_module

__all__ = ["Strategy", "qc", "ta"]


def __getattr__(name: str) -> object:
    if name == "Strategy":
        return getattr(import_module("quantcraft.research.strategy"), name)
    if name in {"qc", "ta"}:
        return import_module(f"quantcraft.research.{name}")
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
