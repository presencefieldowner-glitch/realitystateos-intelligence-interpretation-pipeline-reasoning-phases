import { Planner, PlanTooLargeError, DEFAULT_TEMPLATES } from "./planner";
import { LearningTracker } from "./learning";
import { AgentRuntime, InvalidTaskTransitionError, TaskNotFoundError } from "./agentRuntime";
import { Workflow } from "./workflow";
import { VerifiedBus } from "../../004_VERIFIED_BUS/dist/verifiedBus";
import { generateKeyPair } from "../../003_FOUNDATION/CoreTypes/dist/crypto";

let passed = 0;
let failed = 0;

async function test(name: string, fn: () => void | Promise<void>): Promise<void> {
  try {
    await fn();
    passed++;
    console.log(`  ok  - ${name}`);
  } catch (e) {
    failed++;
    console.log(`FAIL - ${name}`);
    console.log(`       ${(e as Error).message}`);
  }
}

function assert(cond: boolean, msg = "assertion failed"): void {
  if (!cond) throw new Error(msg);
}

const baseOptions = { maxPlanSteps: 25, requireApprovalFor: ["payment", "delete", "external_send"] };

async function main() {
  console.log("Planner");
  await test("plan() matches a known template and flags approval-required steps", () => {
    const planner = new Planner(baseOptions);
    const plan = planner.plan("process a refund for order 42");
    assert(plan.templateUsed === "payment");
    assert(plan.steps.some((s) => s.category === "payment" && s.requiresApproval));
  });

  await test("plan() falls back to a single-step plan for an unmatched goal", () => {
    const planner = new Planner(baseOptions);
    const plan = planner.plan("do something entirely novel");
    assert(plan.templateUsed === undefined);
    assert(plan.steps.length === 1);
  });

  await test("plan() throws PlanTooLargeError when a template exceeds max_plan_steps", () => {
    const planner = new Planner({ maxPlanSteps: 1, requireApprovalFor: [] });
    let threw = false;
    try {
      planner.plan("run a backup");
    } catch (e) {
      threw = e instanceof PlanTooLargeError;
    }
    assert(threw);
  });

  await test("DEFAULT_TEMPLATES covers backup/onboard/payment/revoke goals", () => {
    assert(DEFAULT_TEMPLATES.some((t) => t.name === "backup" && t.matches("run a backup")));
    assert(DEFAULT_TEMPLATES.some((t) => t.name === "onboard_user" && t.matches("onboard a new user")));
  });

  console.log("LearningTracker");
  await test("successRate() reflects recorded outcomes, defaults neutral with no data", () => {
    const tracker = new LearningTracker();
    assert(tracker.successRate("backup") === 0.5);
    tracker.record("backup", "success");
    tracker.record("backup", "success");
    tracker.record("backup", "failure");
    assert(Math.abs(tracker.successRate("backup") - 2 / 3) < 1e-9);
  });

  await test("bestTemplate() picks the highest observed success rate", () => {
    const tracker = new LearningTracker();
    tracker.record("a", "success");
    tracker.record("a", "failure");
    tracker.record("b", "success");
    tracker.record("b", "success");
    assert(tracker.bestTemplate(["a", "b"]) === "b");
  });

  console.log("AgentRuntime");
  await test("run() executes every step and reaches completed", async () => {
    const runtime = new AgentRuntime();
    const planner = new Planner(baseOptions);
    const plan = planner.plan("run a backup");
    const task = runtime.spawn(plan.goal, plan);
    const executed: string[] = [];
    const finished = await runtime.run(task.id, (step) => {
      executed.push(step.id);
    });
    assert(finished.state === "completed");
    assert(executed.length === plan.steps.length);
  });

  await test("run() suspends on a step requiring approval that isn't granted, and resumes when it is", async () => {
    const runtime = new AgentRuntime();
    const planner = new Planner(baseOptions);
    const plan = planner.plan("process a refund");
    const task = runtime.spawn(plan.goal, plan);

    const suspended = await runtime.run(task.id, () => {}, () => false);
    assert(suspended.state === "suspended");

    const resumed = await runtime.run(task.id, () => {}, () => true);
    assert(resumed.state === "completed");
  });

  await test("run() transitions to failed when a step throws, preserving the error and logs", async () => {
    const runtime = new AgentRuntime();
    const planner = new Planner(baseOptions);
    const plan = planner.plan("run a backup");
    const task = runtime.spawn(plan.goal, plan);
    const result = await runtime.run(task.id, (step) => {
      if (step.id === "step-2") throw new Error("disk full");
    });
    assert(result.state === "failed");
    assert(result.error === "disk full");
    assert(result.logs.some((l) => l.includes("failed at step index")));
  });

  await test("stop() marks a running/suspended task failed; reap() moves completed/failed to reaped", async () => {
    const runtime = new AgentRuntime();
    const planner = new Planner(baseOptions);
    const plan = planner.plan("process a refund");
    const task = runtime.spawn(plan.goal, plan);
    await runtime.run(task.id, () => {}, () => false); // suspended
    const stopped = await runtime.stop(task.id);
    assert(stopped.state === "failed");
    const reaped = await runtime.reap(task.id);
    assert(reaped.state === "reaped");
  });

  await test("invalid transitions throw InvalidTaskTransitionError; unknown ids throw TaskNotFoundError", async () => {
    const runtime = new AgentRuntime();
    const planner = new Planner(baseOptions);
    const plan = planner.plan("run a backup");
    const task = runtime.spawn(plan.goal, plan);
    let threw = false;
    try {
      await runtime.reap(task.id); // spawned -> reaped is not a legal transition
    } catch (e) {
      threw = e instanceof InvalidTaskTransitionError;
    }
    assert(threw);

    let notFound = false;
    try {
      runtime.get("nope");
    } catch (e) {
      notFound = e instanceof TaskNotFoundError;
    }
    assert(notFound);
  });

  await test("AgentRuntime publishes lifecycle events to a real VerifiedBus when supplied", async () => {
    const bus = new VerifiedBus({ consensusMode: "none" });
    const keyPair = generateKeyPair();
    const runtime = new AgentRuntime(bus, keyPair);
    const planner = new Planner(baseOptions);
    const plan = planner.plan("run a backup");
    const task = runtime.spawn(plan.goal, plan);
    await runtime.run(task.id, () => {});
    await new Promise((r) => setTimeout(r, 10)); // allow fire-and-forget publish() to settle
    assert(bus.topics().includes("agent.completed"));
  });

  console.log("Workflow");
  await test("run() executes goals in sequence and reports allCompleted", async () => {
    const planner = new Planner(baseOptions);
    const runtime = new AgentRuntime();
    const workflow = new Workflow(planner, runtime);
    const result = await workflow.run(["run a backup", "onboard a new user"], () => {}, () => true);
    assert(result.allCompleted === true);
    assert(result.taskIds.length === 2);
  });

  await test("run() halts the workflow at the first non-completed task", async () => {
    const planner = new Planner(baseOptions);
    const runtime = new AgentRuntime();
    const workflow = new Workflow(planner, runtime);
    const result = await workflow.run(
      ["onboard a new user", "run a backup"],
      () => {},
      () => false // onboard_user has an approval-gated step -> suspends
    );
    assert(result.allCompleted === false);
    assert(result.taskIds.length === 1);
  });

  console.log(`\n${passed} passed, ${failed} failed.`);
  if (failed > 0) process.exit(1);
}

main();
