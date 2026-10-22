"""
monitoring.py — Health-check registry built on top of metrics.py. Each
subsystem (Scheduler, SecurityKernel, EventBus, Storage) can register a
health check; run_checks() gives an aggregate system status.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Dict, List

from .metrics import MetricsRegistry

HealthCheckFn = Callable[[], bool]


@dataclass
class HealthStatus:
    name: str
    healthy: bool
    detail: str = ""


class Monitoring:
    def __init__(self, metrics: MetricsRegistry | None = None) -> None:
        self._checks: Dict[str, HealthCheckFn] = {}
        self.metrics = metrics or MetricsRegistry()

    def register_check(self, name: str, fn: HealthCheckFn) -> None:
        self._checks[name] = fn

    def run_checks(self) -> List[HealthStatus]:
        results = []
        for name, fn in self._checks.items():
            try:
                ok = fn()
                results.append(HealthStatus(name=name, healthy=ok))
            except Exception as e:  # noqa: BLE001
                results.append(HealthStatus(name=name, healthy=False, detail=str(e)))
            self.metrics.increment(f"healthcheck.{name}.runs")
        return results

    def is_healthy(self) -> bool:
        return all(r.healthy for r in self.run_checks())
