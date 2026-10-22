"""
metrics.py — Lightweight counters/gauges/histograms. RuntimeMetrics
(002_KERNEL) and 999_OPERATIONS consume snapshots from here.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class MetricsRegistry:
    counters: Dict[str, float] = field(default_factory=dict)
    gauges: Dict[str, float] = field(default_factory=dict)
    histograms: Dict[str, List[float]] = field(default_factory=dict)

    def increment(self, name: str, amount: float = 1.0) -> None:
        self.counters[name] = self.counters.get(name, 0.0) + amount

    def gauge(self, name: str, value: float) -> None:
        self.gauges[name] = value

    def observe(self, name: str, value: float) -> None:
        self.histograms.setdefault(name, []).append(value)

    def histogram_avg(self, name: str) -> float:
        values = self.histograms.get(name, [])
        return sum(values) / len(values) if values else 0.0

    def snapshot(self) -> dict:
        return {
            "counters": dict(self.counters),
            "gauges": dict(self.gauges),
            "histogram_averages": {k: self.histogram_avg(k) for k in self.histograms},
        }
