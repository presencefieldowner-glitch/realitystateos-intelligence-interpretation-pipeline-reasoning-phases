"""
grpc.py — Transport stub over api.py for typed RPC-style callers. Mirrors
rest.py's shape; kept as its own module because 011_INTERFACE's real gRPC
service definitions will map 1:1 onto api.py commands, not onto rest.py.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict

from .api import Api


@dataclass
class RpcRequest:
    method_name: str
    payload: Dict[str, Any]


class GrpcGateway:
    def __init__(self, api: Api) -> None:
        self._api = api

    def call(self, request: RpcRequest) -> Any:
        return self._api.dispatch(request.method_name, request.payload)
