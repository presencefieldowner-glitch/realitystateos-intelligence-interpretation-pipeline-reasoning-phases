"""
synchronization.py — Interface for reconciling divergent state across
LakeTiticaca instances (e.g. after a network partition). Real conflict
resolution/consensus is 004_VERIFIED_BUS's job; this defines a simple
last-write-wins reconciler sufficient for the single-node prototype stage.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Tuple


@dataclass
class VersionedValue:
    value: Any
    updated_at: float


class LastWriteWinsSynchronizer:
    def reconcile(self, local: Dict[str, VersionedValue], remote: Dict[str, VersionedValue]) -> Dict[str, VersionedValue]:
        merged: Dict[str, VersionedValue] = dict(local)
        for key, remote_val in remote.items():
            local_val = merged.get(key)
            if local_val is None or remote_val.updated_at > local_val.updated_at:
                merged[key] = remote_val
        return merged
