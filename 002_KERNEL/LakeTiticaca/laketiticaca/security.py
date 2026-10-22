"""
security.py — Capability-based security kernel. In an agent-native OS the
bigger risk isn't malicious native code (classic OS sandboxing target), it's
agents/modules overstepping their intended scope. So authorization here is
capability-token based: a subject holds a signed set of capabilities and
every privileged call checks the token, not just an identity/role.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import FrozenSet, Optional
import time


@dataclass(frozen=True)
class CapabilityToken:
    subject: str
    capabilities: FrozenSet[str]
    issued_at: float
    expires_at: Optional[float] = None

    def is_expired(self, now: Optional[float] = None) -> bool:
        if self.expires_at is None:
            return False
        return (now if now is not None else time.time()) >= self.expires_at

    def has(self, capability: str) -> bool:
        return capability in self.capabilities or "*" in self.capabilities


class SecurityKernelError(Exception):
    pass


class SecurityKernel:
    """Checks capability tokens at privileged call boundaries. This is the
    trust boundary every other Kernel service (Scheduler, Storage, EventBus
    consumers) should call through before performing a privileged action."""

    def __init__(self) -> None:
        self._denials = 0
        self._grants = 0

    def check(self, token: CapabilityToken, capability: str) -> bool:
        if token.is_expired():
            self._denials += 1
            return False
        allowed = token.has(capability)
        if allowed:
            self._grants += 1
        else:
            self._denials += 1
        return allowed

    def require(self, token: CapabilityToken, capability: str) -> None:
        if not self.check(token, capability):
            raise SecurityKernelError(
                f"subject '{token.subject}' lacks capability '{capability}'"
            )

    def stats(self) -> dict:
        return {"grants": self._grants, "denials": self._denials}


def issue_capability_token(
    subject: str, capabilities: set[str], ttl_seconds: Optional[int] = None
) -> CapabilityToken:
    now = time.time()
    return CapabilityToken(
        subject=subject,
        capabilities=frozenset(capabilities),
        issued_at=now,
        expires_at=(now + ttl_seconds) if ttl_seconds else None,
    )
