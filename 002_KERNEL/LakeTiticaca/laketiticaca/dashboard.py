"""
dashboard.py — Renders a plain-text snapshot of Kernel AI state (health,
metrics, scheduler queue, security stats). A real dashboard UI is
011_INTERFACE's job; this is the data-gathering seam it would call into.
"""
from __future__ import annotations
from typing import Any, Dict

from .main import LakeTiticaca


def snapshot(instance: LakeTiticaca) -> Dict[str, Any]:
    return {
        "node_id": instance.config.node_id,
        "healthy": instance.monitoring.is_healthy(),
        "metrics": instance.metrics.snapshot(),
        "scheduler_pending": instance.scheduler.pending_count,
        "security_stats": instance.security.stats(),
        "plugins": instance.plugins.list_plugins(),
    }


def render_text(instance: LakeTiticaca) -> str:
    data = snapshot(instance)
    lines = [f"LakeTiticaca [{data['node_id']}] — {'HEALTHY' if data['healthy'] else 'UNHEALTHY'}"]
    lines.append(f"  scheduler pending: {data['scheduler_pending']}")
    lines.append(f"  security: {data['security_stats']}")
    lines.append(f"  plugins: {data['plugins']}")
    for k, v in data["metrics"]["counters"].items():
        lines.append(f"  metric[{k}] = {v}")
    return "\n".join(lines)
