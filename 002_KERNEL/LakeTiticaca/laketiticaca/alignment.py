"""
alignment.py — Step 3 of the cognition loop, and a governance/security
gate: before LakeTiticaca reasons its way to an action, that action is
checked against declared policies/values. This is where "the Kernel AI
overstepped its scope" gets caught, before Reasoning ever executes anything.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, List

PolicyCheck = Callable[["ProposedAction"], bool]


@dataclass
class ProposedAction:
    name: str
    payload: dict


@dataclass
class AlignmentResult:
    action: ProposedAction
    allowed: bool
    reason: str = ""


class AlignmentChecker:
    def __init__(self) -> None:
        self._policies: List[tuple[str, PolicyCheck]] = []

    def add_policy(self, name: str, check: PolicyCheck) -> None:
        self._policies.append((name, check))

    def evaluate(self, action: ProposedAction) -> AlignmentResult:
        for name, check in self._policies:
            if not check(action):
                return AlignmentResult(action=action, allowed=False, reason=f"blocked by policy '{name}'")
        return AlignmentResult(action=action, allowed=True)
