"""
interpretation.py — Step 2 of the cognition loop. Turns raw Observations
into structured Findings via simple rule-based tagging. This is intentionally
not an LLM call here — Kernel-level interpretation needs to be fast,
deterministic, and auditable; genuinely open-ended interpretation belongs to
009_INTELLIGENCE, which can call back down through LakeTiticaca if needed.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, List

from .observation import Observation

Rule = Callable[[Observation], "Finding | None"]


@dataclass
class Finding:
    observation: Observation
    label: str
    detail: Any = None


class Interpreter:
    def __init__(self) -> None:
        self._rules: List[Rule] = []

    def add_rule(self, rule: Rule) -> None:
        self._rules.append(rule)

    def interpret(self, observation: Observation) -> List[Finding]:
        findings = []
        for rule in self._rules:
            result = rule(observation)
            if result is not None:
                findings.append(result)
        return findings

    def interpret_all(self, observations: List[Observation]) -> List[Finding]:
        out: List[Finding] = []
        for obs in observations:
            out.extend(self.interpret(obs))
        return out
