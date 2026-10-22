"""
version_control.py — Git-lite version history for any entity LakeTiticaca
manages. Every commit is retained (no rewriting history), consistent with
the append-only ethos everywhere else in RealityStateOS.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List
import time


@dataclass
class Version:
    entity_id: str
    version_number: int
    data: Dict[str, Any]
    committed_at: float = field(default_factory=time.time)
    message: str = ""


class VersionControl:
    def __init__(self) -> None:
        self._history: Dict[str, List[Version]] = {}

    def commit(self, entity_id: str, data: Dict[str, Any], message: str = "") -> Version:
        history = self._history.setdefault(entity_id, [])
        version = Version(
            entity_id=entity_id,
            version_number=len(history) + 1,
            data=dict(data),
            message=message,
        )
        history.append(version)
        return version

    def get_version(self, entity_id: str, version_number: int) -> Version | None:
        history = self._history.get(entity_id, [])
        for v in history:
            if v.version_number == version_number:
                return v
        return None

    def latest(self, entity_id: str) -> Version | None:
        history = self._history.get(entity_id, [])
        return history[-1] if history else None

    def diff(self, entity_id: str, v1: int, v2: int) -> Dict[str, tuple]:
        a = self.get_version(entity_id, v1)
        b = self.get_version(entity_id, v2)
        if a is None or b is None:
            raise KeyError("one or both versions do not exist")
        changed = {}
        keys = set(a.data.keys()) | set(b.data.keys())
        for k in keys:
            av, bv = a.data.get(k), b.data.get(k)
            if av != bv:
                changed[k] = (av, bv)
        return changed
