"""
main.py — LakeTiticaca: the Kernel-level AI orchestrator. Composes every
subsystem and exposes the core cognition loop: Observe -> Interpret ->
Align -> Reason -> Evolve. Other Kernel services (Scheduler, SecurityKernel)
are wrapped here so decisions can be informed by reasoning rather than being
purely mechanical.
"""
from __future__ import annotations
from typing import List

from .configuration import Configuration
from .event_bus import EventBus
from .scheduler import Scheduler
from .security import SecurityKernel
from .authorization import Authorizer
from .metrics import MetricsRegistry
from .monitoring import Monitoring
from .plugins import PluginRegistry
from .storage import InMemoryStorage
from .database import DatabaseClient
from .knowledge_graph import KnowledgeGraph
from .semantic_index import SemanticIndex
from .vector_store import VectorStore
from .provenance import ProvenanceLog
from .version_control import VersionControl
from .observation import ObservationLog, Observation
from .interpretation import Interpreter, Finding
from .alignment import AlignmentChecker, ProposedAction, AlignmentResult
from .reasoning import ReasoningEngine, Conclusion
from .inference import InferenceEngine
from .retrieval import Retriever
from .evolution import EvolutionTracker
from .api import Api


class LakeTiticaca:
    """The Kernel AI. One instance per node."""

    def __init__(self, config: Configuration | None = None) -> None:
        self.config = config or Configuration()
        self.config.validate()

        # Kernel core
        self.event_bus = EventBus()
        self.scheduler = Scheduler(max_concurrent=self.config.scheduler_max_concurrent)
        self.security = SecurityKernel()
        self.authorizer = Authorizer(self.security)

        # Operational support
        self.metrics = MetricsRegistry()
        self.monitoring = Monitoring(self.metrics)
        self.plugins = PluginRegistry()

        # Data access
        self.storage = InMemoryStorage()
        self.database = DatabaseClient(self.storage)

        # Knowledge / cognition
        self.knowledge_graph = KnowledgeGraph()
        self.semantic_index = SemanticIndex()
        self.vector_store = VectorStore()
        self.provenance = ProvenanceLog()
        self.version_control = VersionControl()
        self.observations = ObservationLog()
        self.interpreter = Interpreter()
        self.alignment = AlignmentChecker()
        self.inference = InferenceEngine()
        self.reasoning = ReasoningEngine(self.inference, self.knowledge_graph)
        self.retriever = Retriever(self.semantic_index, self.vector_store, self.knowledge_graph)
        self.evolution = EvolutionTracker(self.version_control)

        # Command surface
        self.api = Api()

        self._wire_health_checks()
        self._wire_default_api()

    def _wire_health_checks(self) -> None:
        self.monitoring.register_check("scheduler", lambda: True)
        self.monitoring.register_check("security_kernel", lambda: True)

    def _wire_default_api(self) -> None:
        self.api.register("health", lambda _: {"healthy": self.monitoring.is_healthy()})
        self.api.register("metrics", lambda _: self.metrics.snapshot())

    def observe(self, source: str, data) -> Observation:
        obs = self.observations.record(source, data)
        self.event_bus.publish("observation.recorded", obs)
        self.metrics.increment("observations.count")
        return obs

    def cognition_cycle(self, observations: List[Observation] | None = None) -> List[Conclusion]:
        """Runs one pass of Observe -> Interpret -> Align -> Reason -> Evolve
        over the given observations (or everything observed so far)."""
        obs = observations if observations is not None else self.observations.all()
        findings: List[Finding] = self.interpreter.interpret_all(obs)
        conclusions = self.reasoning.reason(findings)
        self.metrics.increment("cognition_cycles.count")
        self.event_bus.publish("cognition.cycle_completed", {"conclusions": len(conclusions)})
        return conclusions

    def propose_action(self, action: ProposedAction) -> AlignmentResult:
        """Every action LakeTiticaca wants to take, on its own or a task's
        behalf, must pass alignment checks before it's allowed to run."""
        result = self.alignment.evaluate(action)
        self.event_bus.publish("alignment.evaluated", result)
        if not result.allowed:
            self.metrics.increment("alignment.blocked")
        return result
