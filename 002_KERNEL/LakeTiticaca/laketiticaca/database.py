"""
database.py — Thin structured-query wrapper over storage.py. This is
intentionally minimal: real relational/graph querying is 012_STORAGE's job.
This module exists so Kernel AI code has one seam to swap when that's wired in.
"""
from __future__ import annotations
from typing import Any, Callable, Dict, List

from .storage import Storage, InMemoryStorage


class DatabaseClient:
    def __init__(self, storage: Storage | None = None) -> None:
        self._storage = storage or InMemoryStorage()

    def put(self, collection: str, record_id: str, data: Dict[str, Any]) -> None:
        self._storage.set(f"{collection}:{record_id}", data)

    def get(self, collection: str, record_id: str) -> Dict[str, Any] | None:
        return self._storage.get(f"{collection}:{record_id}")

    def delete(self, collection: str, record_id: str) -> None:
        self._storage.delete(f"{collection}:{record_id}")

    def query(self, collection: str, predicate: Callable[[Dict[str, Any]], bool]) -> List[Dict[str, Any]]:
        prefix = f"{collection}:"
        matches = []
        for key in self._storage.keys(prefix):
            record = self._storage.get(key)
            if record is not None and predicate(record):
                matches.append(record)
        return matches
