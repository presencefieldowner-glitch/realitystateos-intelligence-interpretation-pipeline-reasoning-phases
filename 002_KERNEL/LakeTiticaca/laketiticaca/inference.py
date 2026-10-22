"""
inference.py — Minimal forward-chaining rule engine: register a condition
and an action; run() applies every matching rule to a fact set. Backs
reasoning.py. Kept simple and deterministic on purpose (see reasoning.py).
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable, Dict, List

Condition = Callable[[Dict[str, Any]], bool]
Action = Callable[[Dict[str, Any]], Any]


@dataclass
class Rule:
    name: str
    condition: Condition
    action: Action


class InferenceEngine:
    def __init__(self) -> None:
        self._rules: List[Rule] = []

    def register_rule(self, name: str, condition: Condition, action: Action) -> None:
        self._rules.append(Rule(name=name, condition=condition, action=action))

    def run(self, facts: Dict[str, Any]) -> List[Any]:
        results = []
        for rule in self._rules:
            if rule.condition(facts):
                results.append(rule.action(facts))
        return results
