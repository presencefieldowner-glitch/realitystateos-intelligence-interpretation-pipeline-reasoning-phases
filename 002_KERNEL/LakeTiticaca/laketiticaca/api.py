"""
api.py — In-process command surface for LakeTiticaca. Deliberately not a
running network server (that's websocket.py/rest.py/grpc.py's job, and
ultimately 011_INTERFACE's) — this is the handler-registration pattern those
transports call into, kept transport-agnostic.
"""
from __future__ import annotations
from typing import Any, Callable, Dict

Handler = Callable[[Dict[str, Any]], Any]


class ApiError(Exception):
    pass


class Api:
    def __init__(self) -> None:
        self._handlers: Dict[str, Handler] = {}

    def register(self, command: str, handler: Handler) -> None:
        self._handlers[command] = handler

    def dispatch(self, command: str, payload: Dict[str, Any] | None = None) -> Any:
        handler = self._handlers.get(command)
        if handler is None:
            raise ApiError(f"no handler registered for command '{command}'")
        return handler(payload or {})

    def commands(self) -> list[str]:
        return list(self._handlers.keys())
