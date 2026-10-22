"""
retrieval.py — Unifies semantic_index, vector_store, and knowledge_graph
lookups behind one retrieve() call, so the cognition loop doesn't need to
know which backing store answered a given query.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, List

from .semantic_index import SemanticIndex
from .vector_store import VectorStore
from .knowledge_graph import KnowledgeGraph


@dataclass
class RetrievalResult:
    source: str  # "semantic_index" | "vector_store" | "knowledge_graph"
    ref_id: str
    score: float


class Retriever:
    def __init__(
        self,
        semantic_index: SemanticIndex,
        vector_store: VectorStore,
        graph: KnowledgeGraph,
    ) -> None:
        self._semantic = semantic_index
        self._vectors = vector_store
        self._graph = graph

    def retrieve_by_text(self, query: str, top_k: int = 5) -> List[RetrievalResult]:
        hits = self._semantic.search(query, top_k=top_k)
        return [RetrievalResult(source="semantic_index", ref_id=doc_id, score=score) for doc_id, score in hits]

    def retrieve_by_vector(self, vector: List[float], top_k: int = 5) -> List[RetrievalResult]:
        hits = self._vectors.search(vector, top_k=top_k)
        return [RetrievalResult(source="vector_store", ref_id=vec_id, score=score) for vec_id, score in hits]

    def retrieve_related(self, node_id: str, rel_type: str | None = None) -> List[RetrievalResult]:
        neighbors = self._graph.neighbors(node_id, rel_type)
        return [RetrievalResult(source="knowledge_graph", ref_id=n.id, score=1.0) for n in neighbors]
