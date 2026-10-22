"""
cli.py — Command-line entry point for local inspection of a LakeTiticaca
instance (health, metrics, scheduler queue). Meant for developer use during
this prototype stage, not the end-user CLI (that's 011_INTERFACE's).
"""
from __future__ import annotations
import argparse
import json

from .main import LakeTiticaca


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="laketiticaca", description="Kernel AI inspection CLI")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("health")
    sub.add_parser("metrics")
    sub.add_parser("scheduler-status")
    return parser


def run(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    instance = LakeTiticaca()

    if args.command == "health":
        print(json.dumps({"healthy": instance.monitoring.is_healthy()}))
    elif args.command == "metrics":
        print(json.dumps(instance.metrics.snapshot()))
    elif args.command == "scheduler-status":
        print(json.dumps({"pending": instance.scheduler.pending_count}))


if __name__ == "__main__":
    run()
