"""
evolution.py — Step 5 of the cognition loop. Records how LakeTiticaca's own
knowledge/config changes over time — an append-only log of "evolution
events" layered on top of version_control.py's per-entity history, giving a
single timeline of the Kernel AI's own change history.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List
import time

from .version_control import VersionControl


@dataclass
class EvolutionEvent:
    entity_id: str
    kind: str  # e.g. "policy_updated", "rule_added", "config_changed"
    detail: Dict[str, Any]
    occurred_at: float = field(default_factory=time.time)


class EvolutionTracker:
    def __init__(self, version_control: VersionControl | None = None) -> None:
        self._events: List[EvolutionEvent] = []
        self._vc = version_control or VersionControl()

    def record_change(self, entity_id: str, kind: str, new_data: Dict[str, Any], detail: Dict[str, Any] | None = None) -> EvolutionEvent:
        self._vc.commit(entity_id, new_data, message=kind)
        event = EvolutionEvent(entity_id=entity_id, kind=kind, detail=detail or {})
        self._events.append(event)
        return event

    def timeline(self) -> List[EvolutionEvent]:
        return list(self._events)

    def timeline_for(self, entity_id: str) -> List[EvolutionEvent]:
        return [e for e in self._events if e.entity_id == entity_id]
