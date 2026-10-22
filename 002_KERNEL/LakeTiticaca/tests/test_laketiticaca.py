"""
LakeTiticaca self-tests. Run with:
    python tests/test_laketiticaca.py
(no pytest dependency required — plain assert-based runner, same style as
the TypeScript Foundation modules' test.ts files.)
"""
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from laketiticaca.configuration import Configuration
from laketiticaca.event_bus import EventBus
from laketiticaca.scheduler import Scheduler, Task
from laketiticaca.security import SecurityKernel, issue_capability_token
from laketiticaca.authentication import issue_token, verify_token, AuthenticationError
from laketiticaca.authorization import Authorizer
from laketiticaca.encryption import generate_key, encrypt, decrypt, encrypt_str, decrypt_str
from laketiticaca.plugins import PluginRegistry, PluginError
from laketiticaca.metrics import MetricsRegistry
from laketiticaca.monitoring import Monitoring
from laketiticaca.storage import InMemoryStorage
from laketiticaca.database import DatabaseClient
from laketiticaca.repository import Repository
from laketiticaca.knowledge_graph import KnowledgeGraph, Node, Edge
from laketiticaca.semantic_index import SemanticIndex
from laketiticaca.vector_store import VectorStore
from laketiticaca.provenance import ProvenanceLog
from laketiticaca.version_control import VersionControl
from laketiticaca.relationships import Relationship, end_relationship
from laketiticaca.observation import ObservationLog
from laketiticaca.interpretation import Interpreter, Finding
from laketiticaca.alignment import AlignmentChecker, ProposedAction
from laketiticaca.inference import InferenceEngine
from laketiticaca.reasoning import ReasoningEngine
from laketiticaca.retrieval import Retriever
from laketiticaca.evolution import EvolutionTracker
from laketiticaca.replication import NoOpReplicator
from laketiticaca.synchronization import LastWriteWinsSynchronizer, VersionedValue
from laketiticaca.api import Api, ApiError
from laketiticaca.websocket import WebSocketGateway, WebSocketMessage
from laketiticaca.rest import RestGateway, RestRequest
from laketiticaca.grpc import GrpcGateway, RpcRequest
from laketiticaca.main import LakeTiticaca
from laketiticaca.dashboard import snapshot as dashboard_snapshot

_passed = 0
_failed = 0


def test(name, fn):
    global _passed, _failed
    try:
        fn()
        _passed += 1
        print(f"  ok  - {name}")
    except Exception as e:
        _failed += 1
        print(f"FAIL - {name}")
        print(f"       {type(e).__name__}: {e}")


print("configuration")
test("defaults validate cleanly", lambda: Configuration().validate())
test("from_dict round trips fields", lambda: (
    (lambda cfg: (_ for _ in ()).throw(AssertionError()) if cfg.node_id != "n1" else None)(
        Configuration.from_dict({"node_id": "n1", "scheduler_max_concurrent": 2})
    )
))

print("event_bus")
def _test_event_bus():
    bus = EventBus()
    received = []
    bus.subscribe("ping", lambda payload: received.append(payload))
    bus.publish("ping", "hello")
    assert received == ["hello"]
    assert len(bus.history("ping")) == 1
test("publish delivers to subscribers", _test_event_bus)

print("scheduler")
def _test_scheduler_priority():
    sched = Scheduler()
    order = []
    sched.submit(Task(name="low", fn=lambda: order.append("low"), priority=5))
    sched.submit(Task(name="high", fn=lambda: order.append("high"), priority=1))
    sched.run_all()
    assert order == ["high", "low"]
test("runs highest-priority (lowest number) task first", _test_scheduler_priority)

def _test_scheduler_failure_isolation():
    sched = Scheduler()
    sched.submit(Task(name="boom", fn=lambda: (_ for _ in ()).throw(RuntimeError("bad"))))
    sched.submit(Task(name="ok", fn=lambda: "fine"))
    results = sched.run_all()
    assert results[0].status == "failed"
    assert results[1].status == "completed"
test("a failing task doesn't block the queue", _test_scheduler_failure_isolation)

print("security")
def _test_security_capability():
    kernel = SecurityKernel()
    token = issue_capability_token("agent-1", {"scheduler.submit"})
    assert kernel.check(token, "scheduler.submit") is True
    assert kernel.check(token, "storage.delete") is False
test("capability token grants only what it holds", _test_security_capability)

def _test_security_expiry():
    kernel = SecurityKernel()
    token = issue_capability_token("agent-1", {"*"}, ttl_seconds=-1)
    assert kernel.check(token, "anything") is False
test("expired tokens are denied", _test_security_expiry)

print("authentication")
def _test_auth_roundtrip():
    token = issue_token("joseph", "secret123", ttl_seconds=60)
    verified = verify_token(token.raw, "secret123")
    assert verified.subject == "joseph"
test("issue/verify token round trip", _test_auth_roundtrip)

def _test_auth_tamper_detection():
    token = issue_token("joseph", "secret123")
    tampered = token.raw[:-2] + "xx"
    try:
        verify_token(tampered, "secret123")
        raise AssertionError("should have raised")
    except AuthenticationError:
        pass
test("tampered token signature is rejected", _test_auth_tamper_detection)

print("authorization")
def _test_authorization_role():
    kernel = SecurityKernel()
    authz = Authorizer(kernel)
    authz.define_role("scheduler_admin", {"scheduler.submit", "scheduler.reprioritize"})
    token = authz.capability_token_for_role("agent-1", "scheduler_admin")
    assert authz.authorize(token, "scheduler.submit") is True
    assert authz.authorize(token, "security.revoke_all") is False
test("role-based capability issuance works", _test_authorization_role)

print("encryption")
def _test_encryption_roundtrip():
    key = generate_key()
    payload = encrypt(b"top secret plans", key)
    assert decrypt(payload, key) == b"top secret plans"
test("AES-GCM encrypt/decrypt round trip", _test_encryption_roundtrip)

def _test_encryption_str_helpers():
    key = generate_key()
    blob = encrypt_str("RealityStateOS is proprietary", key)
    assert decrypt_str(blob, key) == "RealityStateOS is proprietary"
test("string convenience helpers round trip", _test_encryption_str_helpers)

print("plugins")
def _test_plugin_registry():
    class DummyPlugin:
        name = "dummy"
    registry = PluginRegistry()
    registry.register(DummyPlugin())
    assert "dummy" in registry.list_plugins()
    try:
        registry.register(DummyPlugin())
        raise AssertionError("should not allow duplicate registration")
    except PluginError:
        pass
test("register/duplicate-detection works", _test_plugin_registry)

print("metrics + monitoring")
def _test_metrics_and_monitoring():
    metrics = MetricsRegistry()
    metrics.increment("tasks.completed")
    metrics.increment("tasks.completed")
    metrics.observe("latency_ms", 10)
    metrics.observe("latency_ms", 20)
    assert metrics.counters["tasks.completed"] == 2
    assert metrics.histogram_avg("latency_ms") == 15

    mon = Monitoring(metrics)
    mon.register_check("always_ok", lambda: True)
    mon.register_check("always_bad", lambda: False)
    assert mon.is_healthy() is False
test("counters/histograms and health checks aggregate correctly", _test_metrics_and_monitoring)

print("storage + database + repository")
def _test_repository_crud():
    db = DatabaseClient(InMemoryStorage())
    repo = Repository("agents", db)
    rid = repo.create({"name": "Kernel AI", "active": True})
    assert repo.get(rid)["name"] == "Kernel AI"
    repo.update(rid, {"name": "Kernel AI", "active": False})
    assert repo.get(rid)["active"] is False
    matches = repo.find(lambda r: r.get("name") == "Kernel AI")
    assert len(matches) == 1
    repo.delete(rid)
    assert repo.get(rid) is None
test("generic repository CRUD works over in-memory storage", _test_repository_crud)

print("knowledge_graph")
def _test_knowledge_graph():
    g = KnowledgeGraph()
    g.add_node(Node(id="a", kind="agent"))
    g.add_node(Node(id="b", kind="agent"))
    g.add_node(Node(id="c", kind="agent"))
    g.add_edge(Edge(from_id="a", to_id="b", rel_type="knows"))
    g.add_edge(Edge(from_id="b", to_id="c", rel_type="knows"))
    assert [n.id for n in g.neighbors("a")] == ["b"]
    assert g.shortest_path("a", "c") == ["a", "b", "c"]
test("add nodes/edges and find shortest path", _test_knowledge_graph)

print("semantic_index + vector_store + retrieval")
def _test_retrieval():
    idx = SemanticIndex()
    idx.add("doc1", "the kernel schedules agent tasks")
    idx.add("doc2", "reasoning about reality graphs")
    vs = VectorStore()
    vs.upsert("v1", [1.0, 0.0])
    vs.upsert("v2", [0.0, 1.0])
    g = KnowledgeGraph()
    g.add_node(Node(id="x", kind="thing"))
    g.add_node(Node(id="y", kind="thing"))
    g.add_edge(Edge(from_id="x", to_id="y", rel_type="related"))

    retriever = Retriever(idx, vs, g)
    text_hits = retriever.retrieve_by_text("kernel agent tasks")
    assert text_hits[0].ref_id == "doc1"
    vector_hits = retriever.retrieve_by_vector([1.0, 0.0])
    assert vector_hits[0].ref_id == "v1"
    related = retriever.retrieve_related("x")
    assert related[0].ref_id == "y"
test("unified retrieval across text/vector/graph backends", _test_retrieval)

print("provenance")
def _test_provenance():
    log = ProvenanceLog()
    log.record("fact-1", "sensor-A", 0.6)
    log.record("fact-1", "sensor-B", 0.9)
    assert log.latest_confidence("fact-1") == 0.9
    assert log.sources_for("fact-1") == ["sensor-A", "sensor-B"]
test("append-only provenance tracks confidence over time", _test_provenance)

print("version_control")
def _test_version_control():
    vc = VersionControl()
    vc.commit("entity-1", {"status": "draft"})
    vc.commit("entity-1", {"status": "published"})
    assert vc.latest("entity-1").version_number == 2
    diff = vc.diff("entity-1", 1, 2)
    assert diff["status"] == ("draft", "published")
test("commit history and diff work", _test_version_control)

print("relationships")
def _test_relationships():
    rel = Relationship(rel_type="owns", from_id="a", to_id="b", cardinality="one-to-many")
    assert rel.is_active() is True
    end_relationship(rel)
    assert rel.is_active() is False
    assert rel.is_active(at_time=rel.valid_from) is True
test("relationships end rather than delete, temporal queries work", _test_relationships)

print("observation + interpretation + alignment + reasoning + evolution")
def _test_cognition_loop():
    obs_log = ObservationLog()
    obs = obs_log.record("sensor-A", {"temp": 99})

    interpreter = Interpreter()
    interpreter.add_rule(lambda o: Finding(observation=o, label="overheat") if o.data.get("temp", 0) > 90 else None)
    findings = interpreter.interpret(obs)
    assert len(findings) == 1 and findings[0].label == "overheat"

    checker = AlignmentChecker()
    checker.add_policy("no_shutdown_without_confirmation", lambda action: action.name != "shutdown")
    blocked = checker.evaluate(ProposedAction(name="shutdown", payload={}))
    allowed = checker.evaluate(ProposedAction(name="restart", payload={}))
    assert blocked.allowed is False
    assert allowed.allowed is True

    inference = InferenceEngine()
    inference.register_rule(
        "overheat_response",
        lambda facts: facts.get("label") == "overheat",
        lambda facts: "trigger_cooldown",
    )
    graph = KnowledgeGraph()
    reasoner = ReasoningEngine(inference, graph)
    conclusions = reasoner.reason(findings)
    assert conclusions[0].inferred == ["trigger_cooldown"]

    evo = EvolutionTracker()
    evo.record_change("policy-1", "policy_updated", {"threshold": 90})
    assert len(evo.timeline_for("policy-1")) == 1
test("full Observe->Interpret->Align->Reason->Evolve loop", _test_cognition_loop)

print("replication + synchronization")
def _test_replication_and_sync():
    repl = NoOpReplicator()
    repl.replicate("key1", "value1")
    assert "key1" in repl.replicated_keys()

    sync = LastWriteWinsSynchronizer()
    local = {"k": VersionedValue(value="old", updated_at=1.0)}
    remote = {"k": VersionedValue(value="new", updated_at=2.0)}
    merged = sync.reconcile(local, remote)
    assert merged["k"].value == "new"
test("replication log and last-write-wins reconciliation", _test_replication_and_sync)

print("api + transports")
def _test_api_transports():
    api = Api()
    api.register("echo", lambda payload: payload)
    assert api.dispatch("echo", {"x": 1}) == {"x": 1}
    try:
        api.dispatch("missing")
        raise AssertionError("should raise ApiError")
    except ApiError:
        pass

    ws = WebSocketGateway(api)
    resp = ws.handle_message(WebSocketMessage(command="echo", payload={"y": 2}, request_id="r1"))
    assert resp["result"] == {"y": 2} and resp["request_id"] == "r1"

    rest = RestGateway(api)
    resp2 = rest.handle(RestRequest(method="POST", path="/commands/echo", body={"z": 3}))
    assert resp2["body"] == {"z": 3}

    grpc_gw = GrpcGateway(api)
    resp3 = grpc_gw.call(RpcRequest(method_name="echo", payload={"w": 4}))
    assert resp3 == {"w": 4}
test("api dispatch + websocket/rest/grpc gateways all route correctly", _test_api_transports)

print("main — LakeTiticaca orchestrator")
def _test_main_orchestrator():
    instance = LakeTiticaca()
    instance.observe("sensor-A", {"temp": 95})
    conclusions = instance.cognition_cycle()
    assert isinstance(conclusions, list)

    result = instance.propose_action(ProposedAction(name="restart", payload={}))
    assert result.allowed is True

    assert instance.monitoring.is_healthy() is True
    snap = dashboard_snapshot(instance)
    assert snap["node_id"] == "laketiticaca-local"
    assert snap["healthy"] is True
test("LakeTiticaca composes all subsystems and runs a full cycle", _test_main_orchestrator)

print(f"\n{_passed} passed, {_failed} failed.")
if _failed:
    sys.exit(1)
