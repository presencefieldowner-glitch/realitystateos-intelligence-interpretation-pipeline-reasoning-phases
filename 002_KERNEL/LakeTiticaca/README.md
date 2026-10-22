# LakeTiticaca — Kernel-level AI

**Proprietary — © Joseph Michael Rounsaville. See root `LICENSE.md` / `OWNERSHIP.md`.**

LakeTiticaca is RealityStateOS's Kernel AI: it sits *at* 002_KERNEL's privilege
level, not above it. It wraps the Kernel's mechanical services (scheduler,
security kernel, event bus) with reasoning, so decisions like "what runs next"
and "is this action allowed" can be informed by knowledge and inference, not
just static rules.

## Core cognition loop
```
Observe -> Interpret -> Align -> Reason -> Evolve
```
- **Observe** (`observation.py`) — append raw inputs, uninterpreted.
- **Interpret** (`interpretation.py`) — rule-based tagging into structured Findings.
- **Align** (`alignment.py`) — check any proposed action against policy before it runs. This is the governance gate — the Kernel AI is not allowed to act outside declared bounds.
- **Reason** (`reasoning.py` + `inference.py`) — forward-chaining rules over Findings + knowledge graph lookups, producing Conclusions.
- **Evolve** (`evolution.py`) — records how LakeTiticaca's own knowledge/config changed, on top of `version_control.py`.

## Kernel services
- `scheduler.py` — cooperative priority-queue task scheduler. Tasks are agent jobs, not OS threads.
- `security.py` — capability-token based security kernel (the trust boundary).
- `authentication.py` / `authorization.py` — HMAC-signed identity tokens bridged to capability checks.
- `encryption.py` — AES-GCM via the `cryptography` package.
- `event_bus.py` — synchronous pub/sub every subsystem communicates through.

## Knowledge layer (single-node prototype — real backends noted per file)
`knowledge_graph.py`, `semantic_index.py`, `vector_store.py`, `provenance.py`,
`version_control.py`, `relationships.py`, `retrieval.py` — all in-memory,
functionally real for a single node. Each module's docstring notes which
RealityStateOS module (005/006/012) eventually backs it for real, at scale.

## Interface surface
`api.py` is the transport-agnostic command registry; `websocket.py`, `rest.py`,
`grpc.py` are thin gateways over it (no servers actually bound here — that's
011_INTERFACE's job). `cli.py` and `dashboard.py` are developer-facing
inspection tools for this prototype stage.

## Distributed concerns (stubbed, single-node for now)
`replication.py`, `synchronization.py` — define the seams; real multi-node
behavior belongs to 004_VERIFIED_BUS / 012_STORAGE.

## Build & test
```bash
pip install -e .
python -m pytest tests/ -v
# or, no pytest required:
python tests/test_laketiticaca.py
```
