"""
provenance.py — Tracks where every piece of knowledge came from. Nothing
LakeTiticaca reasons over should be untraceable — this is a hard requirement
for a "verifiable" OS (RealityStateOS's core promise), not an afterthought.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List
import time


@dataclass
class ProvenanceRecord:
    fact_id: str
    source: str
    confidence: float
    recorded_at: float = field(default_factory=time.time)
    notes: str = ""


class ProvenanceLog:
    """Append-only — provenance is never edited or deleted, only added to,
    matching the Tombstonable/no-mutation pattern used across Foundation."""

    def __init__(self) -> None:
        self._records: List[ProvenanceRecord] = []

    def record(self, fact_id: str, source: str, confidence: float, notes: str = "") -> ProvenanceRecord:
        rec = ProvenanceRecord(fact_id=fact_id, source=source, confidence=confidence, notes=notes)
        self._records.append(rec)
        return rec

    def history_for(self, fact_id: str) -> List[ProvenanceRecord]:
        return [r for r in self._records if r.fact_id == fact_id]

    def latest_confidence(self, fact_id: str) -> float | None:
        history = self.history_for(fact_id)
        return history[-1].confidence if history else None

    def sources_for(self, fact_id: str) -> List[str]:
        return [r.source for r in self.history_for(fact_id)]
