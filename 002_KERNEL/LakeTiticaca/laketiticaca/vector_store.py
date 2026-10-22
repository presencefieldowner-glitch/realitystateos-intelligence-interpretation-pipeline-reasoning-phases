"""
vector_store.py — In-memory vector similarity search (pure Python, no numpy
dependency). Placeholder for a real vector DB (Pinecone/pgvector/etc, wired
in via 012_STORAGE) — same cosine-similarity math, just not indexed for scale.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Sequence, Tuple
import math


@dataclass
class VectorRecord:
    vector_id: str
    vector: List[float]
    metadata: dict


def _cosine_similarity(a: Sequence[float], b: Sequence[float]) -> float:
    if len(a) != len(b):
        raise ValueError("vectors must be the same dimension")
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


class VectorStore:
    def __init__(self) -> None:
        self._records: Dict[str, VectorRecord] = {}

    def upsert(self, vector_id: str, vector: List[float], metadata: dict | None = None) -> None:
        self._records[vector_id] = VectorRecord(vector_id, vector, metadata or {})

    def delete(self, vector_id: str) -> None:
        self._records.pop(vector_id, None)

    def search(self, query_vector: List[float], top_k: int = 5) -> List[Tuple[str, float]]:
        scored = [
            (rec.vector_id, _cosine_similarity(query_vector, rec.vector))
            for rec in self._records.values()
        ]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]
