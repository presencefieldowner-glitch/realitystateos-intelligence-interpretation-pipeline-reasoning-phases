# 009_INTELLIGENCE — Status: Implemented (prototype)

Planning, reasoning, learning, agent runtime, workflows — the real home of what the dossier's IHI/RHI split describes in the abstract; this module doesn't separate them, matching what `002_KERNEL/LakeTiticaca`'s `reasoning.py`/`inference.py` already show. Backs `rsos agent run/list/logs/stop`.

| File | Provides |
|---|---|
| `planner.ts` | `Planner.plan()` — real, deterministic template-matching goal decomposition (backup / onboard_user / payment / revoke_access + a single-step fallback). Not an `intelligence.default_llm_provider` call — that integration is a documented follow-up behind the same `plan()` signature. |
| `agentRuntime.ts` | `AgentRuntime` — implements the task lifecycle `002_KERNEL/KERNEL_RFC.md` documents but leaves unbuilt: `spawned → running → (suspended ⇄ running) → completed \| failed → reaped`. Cooperative execution: a task runs its steps until done, failed, or yielded on a missing approval (`intelligence.require_approval_for`). Optionally publishes lifecycle events to `004_VERIFIED_BUS` when one is supplied. |
| `workflow.ts` | `Workflow` — chains multiple goals into sequential `AgentRuntime` tasks; halts on the first non-completed task rather than continuing blind. |
| `learning.ts` | `LearningTracker` — real (if modest) success/failure weighting per plan template; not machine learning, a success-rate counter callers can use to bias template choice. |

Depends on `003_FOUNDATION` (CoreTypes) directly, and optionally `004_VERIFIED_BUS` (EventPublisher-shaped) via compiled `dist/` imports.

## Known deviations from spec
- Planning is rule/template-based, not LLM-backed — `intelligence.default_llm_provider` names a real model integration this module deliberately doesn't fake.
- `LearningTracker` is a success-rate counter, not a learning algorithm in the ML sense — scoped honestly, not oversold.

Build/test: `npm install && npm test`.
