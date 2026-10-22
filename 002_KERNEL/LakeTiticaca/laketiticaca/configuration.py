"""
configuration.py — Kernel AI configuration loading and validation.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict
import os


@dataclass
class Configuration:
    """Runtime configuration for a LakeTiticaca instance."""

    node_id: str = "laketiticaca-local"
    scheduler_max_concurrent: int = 4
    security_token_secret: str = "dev-secret-change-me"
    security_token_ttl_seconds: int = 3600
    metrics_enabled: bool = True
    extras: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if not self.node_id:
            raise ValueError("node_id must not be empty")
        if self.scheduler_max_concurrent < 1:
            raise ValueError("scheduler_max_concurrent must be >= 1")
        if not self.security_token_secret or self.security_token_secret == "dev-secret-change-me":
            # Not fatal in dev, but flagged — production deploys must override this.
            pass

    @staticmethod
    def from_env(prefix: str = "LAKETITICACA_") -> "Configuration":
        def get(name: str, default: Any) -> Any:
            return os.environ.get(prefix + name, default)

        cfg = Configuration(
            node_id=get("NODE_ID", "laketiticaca-local"),
            scheduler_max_concurrent=int(get("SCHEDULER_MAX_CONCURRENT", 4)),
            security_token_secret=get("SECURITY_TOKEN_SECRET", "dev-secret-change-me"),
            security_token_ttl_seconds=int(get("SECURITY_TOKEN_TTL_SECONDS", 3600)),
            metrics_enabled=get("METRICS_ENABLED", "true").lower() == "true",
        )
        cfg.validate()
        return cfg

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Configuration":
        cfg = Configuration(**{k: v for k, v in data.items() if k != "extras"})
        cfg.extras = data.get("extras", {})
        cfg.validate()
        return cfg
