"""
relationships.py — Python-side mirror of the TypeScript EntityModel's
Relationship semantics (003_FOUNDATION/EntityModel): directed, cardinality-
typed, temporally-scoped. Kept here so LakeTiticaca's knowledge_graph can
work with typed relationships without pulling in the TS module.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Literal, Optional
import time
import uuid

Cardinality = Literal["one-to-one", "one-to-many", "many-to-many"]


@dataclass
class Relationship:
    rel_type: str
    from_id: str
    to_id: str
    cardinality: Cardinality
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    valid_from: float = field(default_factory=time.time)
    valid_to: Optional[float] = None

    def is_active(self, at_time: Optional[float] = None) -> bool:
        t = at_time if at_time is not None else time.time()
        return t >= self.valid_from and (self.valid_to is None or t < self.valid_to)


def end_relationship(rel: Relationship) -> Relationship:
    """Ends (invalidates) a relationship as of now — never delete, so
    point-in-time queries stay historically accurate."""
    rel.valid_to = time.time()
    return rel
