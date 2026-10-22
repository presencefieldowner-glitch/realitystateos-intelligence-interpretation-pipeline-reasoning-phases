"""
websocket.py — Transport stub over api.py for streaming/bidirectional
callers. No real socket is opened here — actual network binding belongs to
011_INTERFACE. This defines the message-framing contract that surface will use.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict

from .api import Api


@dataclass
class WebSocketMessage:
    command: str
    payload: Dict[str, Any]
    request_id: str | None = None


class WebSocketGateway:
    def __init__(self, api: Api) -> None:
        self._api = api

    def handle_message(self, message: WebSocketMessage) -> Dict[str, Any]:
        result = self._api.dispatch(message.command, message.payload)
        return {"request_id": message.request_id, "result": result}
