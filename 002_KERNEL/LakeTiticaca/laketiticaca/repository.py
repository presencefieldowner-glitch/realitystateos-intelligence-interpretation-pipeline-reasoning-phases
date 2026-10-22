"""
repository.py — Generic CRUD repository over database.py, giving cognition
modules (knowledge_graph, provenance, etc.) a consistent way to persist their
records without each reimplementing storage plumbing.
"""
from __future__ import annotations
from typing import Any, Callable, Dict, Generic, List, TypeVar
import uuid

from .database import DatabaseClient

T = TypeVar("T", bound=Dict[str, Any])


class Repository(Generic[T]):
    def __init__(self, collection: str, db: DatabaseClient) -> None:
        self._collection = collection
        self._db = db

    def create(self, data: T, record_id: str | None = None) -> str:
        record_id = record_id or str(uuid.uuid4())
        self._db.put(self._collection, record_id, dict(data))
        return record_id

    def get(self, record_id: str) -> T | None:
        return self._db.get(self._collection, record_id)  # type: ignore[return-value]

    def update(self, record_id: str, data: T) -> None:
        self._db.put(self._collection, record_id, dict(data))

    def delete(self, record_id: str) -> None:
        self._db.delete(self._collection, record_id)

    def find(self, predicate: Callable[[T], bool]) -> List[T]:
        return self._db.query(self._collection, predicate)  # type: ignore[arg-type]
