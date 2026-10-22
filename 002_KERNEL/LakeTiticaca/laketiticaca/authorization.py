"""
authorization.py — Bridges authentication (who is calling) to security.py's
capability checks (what are they allowed to do). Also supports a simple
role-to-capability mapping for convenience when issuing tokens.
"""
from __future__ import annotations
from typing import Dict, Set

from .security import CapabilityToken, SecurityKernel, issue_capability_token
from .authentication import AuthToken


class Authorizer:
    def __init__(self, security_kernel: SecurityKernel) -> None:
        self._kernel = security_kernel
        self._roles: Dict[str, Set[str]] = {}

    def define_role(self, role: str, capabilities: Set[str]) -> None:
        self._roles[role] = set(capabilities)

    def capability_token_for_role(
        self, subject: str, role: str, ttl_seconds: int | None = None
    ) -> CapabilityToken:
        capabilities = self._roles.get(role, set())
        return issue_capability_token(subject, capabilities, ttl_seconds)

    def authorize(self, token: CapabilityToken, capability: str) -> bool:
        return self._kernel.check(token, capability)

    def require(self, token: CapabilityToken, capability: str) -> None:
        self._kernel.require(token, capability)

    def authorize_auth_token(
        self, auth_token: AuthToken, role_of: Dict[str, str], capability: str
    ) -> bool:
        """Convenience: go straight from an AuthToken (identity) to an
        authorization decision, looking up the subject's role."""
        role = role_of.get(auth_token.subject)
        if role is None:
            return False
        cap_token = self.capability_token_for_role(auth_token.subject, role)
        return self.authorize(cap_token, capability)
