"""
rest.py — Transport stub over api.py for request/response callers. Maps
HTTP-shaped calls (method + path + body) onto api.py commands. No HTTP
server is started here — 011_INTERFACE owns the actual binding.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict

from .api import Api


@dataclass
class RestRequest:
    method: str
    path: str
    body: Dict[str, Any]


class RestGateway:
    def __init__(self, api: Api) -> None:
        self._api = api

    def handle(self, request: RestRequest) -> Dict[str, Any]:
        # path convention: /commands/<command_name>
        command = request.path.strip("/").split("/")[-1]
        result = self._api.dispatch(command, request.body)
        return {"status": 200, "body": result}
