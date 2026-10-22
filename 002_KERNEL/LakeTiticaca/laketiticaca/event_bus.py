"""
event_bus.py — Kernel-level synchronous pub/sub. Every LakeTiticaca subsystem
(scheduler, security kernel, cognition loop) publishes and reacts through this
bus rather than calling each other directly, keeping the Kernel AI decoupled
from any one subsystem's implementation.
"""
from __future__ import annotations
from typing import Any, Callable, Dict, List
from dataclasses import dataclass, field
import time


Handler = Callable[[Any], None]


@dataclass
class EventRecord:
    event_type: str
    payload: Any
    timestamp: float = field(default_factory=time.time)


class EventBus:
    def __init__(self) -> None:
        self._handlers: Dict[str, List[Handler]] = {}
        self._history: List[EventRecord] = []

    def subscribe(self, event_type: str, handler: Handler) -> None:
        self._handlers.setdefault(event_type, []).append(handler)

    def unsubscribe(self, event_type: str, handler: Handler) -> None:
        if event_type in self._handlers:
            self._handlers[event_type] = [h for h in self._handlers[event_type] if h != handler]

    def publish(self, event_type: str, payload: Any = None) -> None:
        self._history.append(EventRecord(event_type=event_type, payload=payload))
        for handler in self._handlers.get(event_type, []):
            handler(payload)

    def history(self, event_type: str | None = None) -> List[EventRecord]:
        if event_type is None:
            return list(self._history)
        return [e for e in self._history if e.event_type == event_type]
