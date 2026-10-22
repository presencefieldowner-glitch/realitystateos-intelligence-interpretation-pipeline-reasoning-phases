/**
 * RealityStateOS — Intelligence / AgentRuntime
 * Backs `rsos agent run/list/logs/stop`. Implements the task lifecycle
 * state machine 002_KERNEL/KERNEL_RFC.md documents but leaves unbuilt:
 * spawned -> running -> (suspended <-> running) -> completed | failed -> reaped.
 * Execution is cooperative (a task runs its steps until it completes, fails,
 * or yields on a missing approval — never preempted), matching the Kernel's
 * own scheduling model. Optionally publishes lifecycle events to the
 * Verified Bus (004) when one is supplied, so agent activity is itself
 * auditable through the same verified event chain as everything else.
 */
import { newId, Id } from "../../003_FOUNDATION/CoreTypes/dist/id";
import { defaultClock } from "../../003_FOUNDATION/CoreTypes/dist/timestamp";
import { KeyPair } from "../../003_FOUNDATION/CoreTypes/dist/crypto";
import { Plan, PlanStep } from "./planner";

export type TaskState = "spawned" | "running" | "suspended" | "completed" | "failed" | "reaped";

export interface AgentTask {
  id: Id;
  goal: string;
  plan: Plan;
  state: TaskState;
  currentStepIndex: number;
  logs: string[];
  error?: string;
}

export class InvalidTaskTransitionError extends Error {
  constructor(from: TaskState, to: TaskState) {
    super(`cannot transition agent task from "${from}" to "${to}"`);
  }
}

export class TaskNotFoundError extends Error {
  constructor(id: string) {
    super(`no agent task found with id "${id}"`);
  }
}

const TRANSITIONS: Record<TaskState, TaskState[]> = {
  spawned: ["running"],
  running: ["suspended", "completed", "failed"],
  // A suspended task can resume (-> running) or be forcefully stopped (-> failed).
  suspended: ["running", "failed"],
  completed: ["reaped"],
  failed: ["reaped"],
  reaped: [],
};

export type StepExecutor = (step: PlanStep) => unknown | Promise<unknown>;
export type ApprovalGate = (step: PlanStep) => boolean | Promise<boolean>;

export interface EventPublisher {
  publish<T>(topic: string, schemaVersion: string, payload: T, keyPair: KeyPair): Promise<unknown>;
}

export class AgentRuntime {
  private tasks = new Map<Id, AgentTask>();

  constructor(private readonly bus?: EventPublisher, private readonly keyPair?: KeyPair) {}

  spawn(goal: string, plan: Plan): AgentTask {
    const task: AgentTask = {
      id: newId(),
      goal,
      plan,
      state: "spawned",
      currentStepIndex: 0,
      logs: [`spawned at ${defaultClock.nowRfc3339()} with ${plan.steps.length} step(s)`],
    };
    this.tasks.set(task.id, task);
    return task;
  }

  get(id: Id): AgentTask {
    const task = this.tasks.get(id);
    if (!task) throw new TaskNotFoundError(id);
    return task;
  }

  list(filter?: TaskState): AgentTask[] {
    const all = [...this.tasks.values()];
    return filter ? all.filter((t) => t.state === filter) : all;
  }

  logs(id: Id): string[] {
    return [...this.get(id).logs];
  }

  /** Runs (or resumes) a task cooperatively: executes steps in order,
   * yielding to "suspended" the moment a step requires approval that isn't
   * granted, and resuming from the same step index on the next run() call. */
  async run(id: Id, executor: StepExecutor, approve: ApprovalGate = () => true): Promise<AgentTask> {
    const task = this.get(id);
    this.transition(task, "running");

    try {
      while (task.currentStepIndex < task.plan.steps.length) {
        const step = task.plan.steps[task.currentStepIndex];
        if (step.requiresApproval && !(await approve(step))) {
          task.logs.push(`suspended at ${step.id}: approval required but not granted`);
          this.transition(task, "suspended");
          return task;
        }
        await executor(step);
        task.logs.push(`completed ${step.id}: ${step.description}`);
        task.currentStepIndex++;
      }
      this.transition(task, "completed");
    } catch (e) {
      task.error = (e as Error).message;
      task.logs.push(`failed at step index ${task.currentStepIndex}: ${task.error}`);
      this.transition(task, "failed");
    }
    return task;
  }

  /** Forceful stop, per `rsos agent stop <agent_id>` — a running task is
   * marked failed rather than silently vanishing, preserving its logs. */
  async stop(id: Id): Promise<AgentTask> {
    const task = this.get(id);
    if (task.state !== "running" && task.state !== "suspended") {
      throw new InvalidTaskTransitionError(task.state, "failed");
    }
    task.error = "stopped by operator";
    task.logs.push(`stopped by operator at ${defaultClock.nowRfc3339()}`);
    this.transition(task, "failed");
    return task;
  }

  async reap(id: Id): Promise<AgentTask> {
    const task = this.get(id);
    this.transition(task, "reaped");
    return task;
  }

  private transition(task: AgentTask, next: TaskState): void {
    if (!TRANSITIONS[task.state].includes(next)) {
      throw new InvalidTaskTransitionError(task.state, next);
    }
    task.state = next;
    if (this.bus && this.keyPair) {
      void this.bus.publish(`agent.${next}`, "1.0.0", { taskId: task.id, goal: task.goal }, this.keyPair);
    }
  }
}
