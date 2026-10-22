"""
reasoning.py — Step 4 of the cognition loop. A small forward-chaining rule
engine (inference.py) plus knowledge_graph.py lookups produce Conclusions
from Findings. Deliberately simple/deterministic at Kernel level — deep,
open-ended reasoning is 009_INTELLIGENCE's job; this is the fast, auditable
reasoning the Kernel AI needs for its own decisions (scheduling, security).
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, List

from .interpretation import Finding
from .inference import InferenceEngine
from .knowledge_graph import KnowledgeGraph


@dataclass
class Conclusion:
    finding: Finding
    inferred: List[Any]


class ReasoningEngine:
    def __init__(self, inference_engine: InferenceEngine, graph: KnowledgeGraph) -> None:
        self._inference = inference_engine
        self._graph = graph

    def reason(self, findings: List[Finding]) -> List[Conclusion]:
        conclusions = []
        for finding in findings:
            facts = {"label": finding.label, "detail": finding.detail}
            inferred = self._inference.run(facts)
            conclusions.append(Conclusion(finding=finding, inferred=inferred))
        return conclusions
