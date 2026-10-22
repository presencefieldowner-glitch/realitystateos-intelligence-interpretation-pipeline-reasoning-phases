"""
observation.py — Step 1 of LakeTiticaca's cognition loop (Observe -> Interpret
-> Align -> Reason -> Evolve). Raw, uninterpreted inputs get appended here
before anything tries to make sense of them. Feeds 008_REALITY_TAPE's sensor
ingestion model at larger scale; this is the Kernel-local version.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, List
import time


@dataclass
class Observation:
    source: str
    data: Any
    observed_at: float = field(default_factory=time.time)


class ObservationLog:
    """Append-only, matches the Reality Tape / EventStore pattern — raw
    observations are never edited, only ever added to."""

    def __init__(self) -> None:
        self._log: List[Observation] = []

    def record(self, source: str, data: Any) -> Observation:
        obs = Observation(source=source, data=data)
        self._log.append(obs)
        return obs

    def since(self, timestamp: float) -> List[Observation]:
        return [o for o in self._log if o.observed_at >= timestamp]

    def from_source(self, source: str) -> List[Observation]:
        return [o for o in self._log if o.source == source]

    def all(self) -> List[Observation]:
        return list(self._log)
