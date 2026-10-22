"""
semantic_index.py — Naive keyword-overlap search index. Placeholder for real
embedding-based semantic search (005_KNOWLEDGE will use real embeddings +
a vector DB); this gives LakeTiticaca *something* to retrieve by meaning
today without requiring an external embedding model in the sandbox.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple
import re


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


@dataclass
class IndexedDocument:
    doc_id: str
    text: str
    tokens: set[str]


class SemanticIndex:
    def __init__(self) -> None:
        self._docs: Dict[str, IndexedDocument] = {}

    def add(self, doc_id: str, text: str) -> None:
        self._docs[doc_id] = IndexedDocument(doc_id=doc_id, text=text, tokens=_tokenize(text))

    def remove(self, doc_id: str) -> None:
        self._docs.pop(doc_id, None)

    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        query_tokens = _tokenize(query)
        if not query_tokens:
            return []
        scored = []
        for doc in self._docs.values():
            overlap = len(query_tokens & doc.tokens)
            if overlap == 0:
                continue
            score = overlap / len(query_tokens | doc.tokens)  # Jaccard similarity
            scored.append((doc.doc_id, score))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]
