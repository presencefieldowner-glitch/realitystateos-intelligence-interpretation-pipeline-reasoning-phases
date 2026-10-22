"""
scheduler.py — Kernel task scheduler. "Processes" in RealityStateOS are agent
tasks/jobs, not OS threads, so this is a cooperative priority scheduler, not
a preemptive one. LakeTiticaca can influence priority scoring (e.g. bump a
task's priority based on reasoning about urgency) rather than just executing
whatever's queued in FIFO order.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, List, Optional
import heapq
import itertools


TaskStatus = str  # "pending" | "running" | "completed" | "failed" | "cancelled"

_counter = itertools.count()


@dataclass
class Task:
    name: str
    fn: Callable[[], Any]
    priority: int = 0  # lower runs first
    status: TaskStatus = "pending"
    result: Any = None
    error: Optional[BaseException] = None
    _seq: int = field(default_factory=lambda: next(_counter))

    def __lt__(self, other: "Task") -> bool:
        # Lower priority number = higher urgency; ties broken by insertion order (FIFO).
        return (self.priority, self._seq) < (other.priority, other._seq)


class Scheduler:
    """A simple, cooperative priority-queue scheduler."""

    def __init__(self, max_concurrent: int = 4) -> None:
        self._queue: List[Task] = []
        self._max_concurrent = max_concurrent
        self._running: List[Task] = []
        self._completed: List[Task] = []

    def submit(self, task: Task) -> Task:
        heapq.heappush(self._queue, task)
        return task

    @property
    def is_empty(self) -> bool:
        return len(self._queue) == 0

    @property
    def pending_count(self) -> int:
        return len(self._queue)

    def run_next(self) -> Optional[Task]:
        """Runs the single highest-priority pending task synchronously."""
        if self.is_empty:
            return None
        task = heapq.heappop(self._queue)
        task.status = "running"
        self._running.append(task)
        try:
            task.result = task.fn()
            task.status = "completed"
        except BaseException as e:  # noqa: BLE001 — kernel must not crash on task failure
            task.error = e
            task.status = "failed"
        finally:
            self._running.remove(task)
            self._completed.append(task)
        return task

    def run_all(self) -> List[Task]:
        """Runs every currently-queued task to completion, respecting priority order."""
        results = []
        while not self.is_empty:
            results.append(self.run_next())
        return results

    def reprioritize(self, name: str, new_priority: int) -> bool:
        """Kernel AI hook — allows LakeTiticaca's reasoning to bump a queued
        task's priority (e.g. it inferred urgency the caller didn't specify)."""
        for task in self._queue:
            if task.name == name:
                task.priority = new_priority
                heapq.heapify(self._queue)
                return True
        return False
