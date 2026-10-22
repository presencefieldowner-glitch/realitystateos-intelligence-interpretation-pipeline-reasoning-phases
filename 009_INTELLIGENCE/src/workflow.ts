/**
 * RealityStateOS — Intelligence / Workflow
 * Chains multiple goals into a sequence of AgentRuntime tasks — each
 * planned fresh and run to completion (or suspension/failure) before the
 * next starts. A failed task halts the workflow rather than silently
 * continuing, since later steps may assume earlier ones succeeded.
 */
import { Planner } from "./planner";
import { AgentRuntime, StepExecutor, ApprovalGate, AgentTask } from "./agentRuntime";

export interface WorkflowResult {
  taskIds: string[];
  allCompleted: boolean;
  haltedAt?: string;
}

export class Workflow {
  constructor(private readonly planner: Planner, private readonly runtime: AgentRuntime) {}

  async run(goals: string[], executor: StepExecutor, approve: ApprovalGate = () => true): Promise<WorkflowResult> {
    const taskIds: string[] = [];
    let haltedAt: string | undefined;

    for (const goal of goals) {
      const plan = this.planner.plan(goal);
      const task = this.runtime.spawn(goal, plan);
      taskIds.push(task.id);

      const result: AgentTask = await this.runtime.run(task.id, executor, approve);
      if (result.state !== "completed") {
        haltedAt = task.id;
        break;
      }
    }

    const allCompleted = taskIds.every((id) => this.runtime.get(id).state === "completed");
    return { taskIds, allCompleted, haltedAt };
  }
}
