"""
replication.py — Interface for replicating Kernel AI state across nodes.
Real multi-node replication is 004_VERIFIED_BUS's + 012_STORAGE's job; this
defines the seam LakeTiticaca calls through, with a single-node no-op
implementation until a real backend is wired in.
"""
from __future__ import annotations
from typing import Any, Dict, List, Protocol


class Replicator(Protocol):
    def replicate(self, key: str, value: Any) -> None: ...
    def replicated_keys(self) -> List[str]: ...


class NoOpReplicator:
    """Single-node placeholder — records what WOULD be replicated so tests
    and callers can verify intent without needing a real cluster."""

    def __init__(self) -> None:
        self._log: Dict[str, Any] = {}

    def replicate(self, key: str, value: Any) -> None:
        self._log[key] = value

    def replicated_keys(self) -> List[str]:
        return list(self._log.keys())
