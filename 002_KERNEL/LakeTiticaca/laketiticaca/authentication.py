"""
authentication.py — HMAC-signed bearer tokens proving "who is calling."
Deliberately simple (HMAC-SHA256, not full JWT) — this is a Kernel-internal
mechanism for subjects (modules, agents, users) to prove identity to the
SecurityKernel before capabilities are checked in authorization.py.
"""
from __future__ import annotations
import base64
import hashlib
import hmac
import json
import time
from dataclasses import dataclass
from typing import Optional


class AuthenticationError(Exception):
    pass


@dataclass(frozen=True)
class AuthToken:
    subject: str
    issued_at: float
    expires_at: Optional[float]
    raw: str


def _sign(payload_b64: str, secret: str) -> str:
    sig = hmac.new(secret.encode(), payload_b64.encode(), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(sig).decode().rstrip("=")


def issue_token(subject: str, secret: str, ttl_seconds: Optional[int] = None) -> AuthToken:
    now = time.time()
    expires_at = (now + ttl_seconds) if ttl_seconds else None
    payload = {"sub": subject, "iat": now, "exp": expires_at}
    payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    signature = _sign(payload_b64, secret)
    raw = f"{payload_b64}.{signature}"
    return AuthToken(subject=subject, issued_at=now, expires_at=expires_at, raw=raw)


def verify_token(raw: str, secret: str) -> AuthToken:
    try:
        payload_b64, signature = raw.split(".", 1)
    except ValueError:
        raise AuthenticationError("malformed token")

    expected_sig = _sign(payload_b64, secret)
    if not hmac.compare_digest(expected_sig, signature):
        raise AuthenticationError("signature mismatch")

    padded = payload_b64 + "=" * (-len(payload_b64) % 4)
    payload = json.loads(base64.urlsafe_b64decode(padded))

    if payload.get("exp") is not None and time.time() >= payload["exp"]:
        raise AuthenticationError("token expired")

    return AuthToken(
        subject=payload["sub"],
        issued_at=payload["iat"],
        expires_at=payload.get("exp"),
        raw=raw,
    )
