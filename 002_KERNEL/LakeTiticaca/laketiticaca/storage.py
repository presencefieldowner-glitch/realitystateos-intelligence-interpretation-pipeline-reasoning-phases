"""
storage.py — Kernel AI data access abstraction. In-memory implementation for
now; a real deployment swaps this for a client of 012_STORAGE (Postgres/
graph store/vector store) without changing callers, since they only ever
depend on the Storage protocol below.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional, Protocol


class Storage(Protocol):
    def get(self, key: str) -> Optional[Any]: ...
    def set(self, key: str, value: Any) -> None: ...
    def delete(self, key: str) -> None: ...
    def keys(self, prefix: str = "") -> List[str]: ...


class InMemoryStorage:
    """Reference implementation — good for tests and single-node bootstrap.
    NOT durable: contents are lost on process exit. See 012_STORAGE for the
    durable backend this is meant to be swapped for."""

    def __init__(self) -> None:
        self._data: Dict[str, Any] = {}

    def get(self, key: str) -> Optional[Any]:
        return self._data.get(key)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value

    def delete(self, key: str) -> None:
        self._data.pop(key, None)

    def keys(self, prefix: str = "") -> List[str]:
        return [k for k in self._data.keys() if k.startswith(prefix)]
