/**
 * RealityStateOS — Intelligence / Planner
 * Backs `rsos agent run <goal>`. Real, deterministic, template-matching
 * decomposition — not a call to `intelligence.default_llm_provider`. This
 * is the honest scope for planning this sandbox can prototype for real
 * without a live model integration; swap in a real LLM-backed planner
 * behind the same plan() signature later.
 */

export interface PlanStep {
  id: string;
  description: string;
  category?: string;
  requiresApproval: boolean;
}

export interface Plan {
  goal: string;
  templateUsed?: string;
  steps: PlanStep[];
}

export interface PlanTemplate {
  name: string;
  matches: (goal: string) => boolean;
  steps: (goal: string) => { description: string; category?: string }[];
}

export const DEFAULT_TEMPLATES: PlanTemplate[] = [
  {
    name: "backup",
    matches: (g) => /backup/i.test(g),
    steps: () => [
      { description: "create storage snapshot" },
      { description: "verify snapshot integrity" },
      { description: "record snapshot in audit log" },
    ],
  },
  {
    name: "onboard_user",
    matches: (g) => /onboard|create.*user|new user/i.test(g),
    steps: () => [
      { description: "create user profile" },
      { description: "send welcome notification", category: "external_send" },
    ],
  },
  {
    name: "payment",
    matches: (g) => /\b(pay|charge|refund)\b/i.test(g),
    steps: () => [
      { description: "validate payment request" },
      { description: "execute payment", category: "payment" },
      { description: "record transaction" },
    ],
  },
  {
    name: "revoke_access",
    matches: (g) => /revoke|delete.*(account|profile|data)/i.test(g),
    steps: () => [
      { description: "confirm target identity" },
      { description: "delete/revoke target record", category: "delete" },
      { description: "record revocation in audit log" },
    ],
  },
];

export class PlanTooLargeError extends Error {
  constructor(stepCount: number, maxPlanSteps: number) {
    super(`plan for goal has ${stepCount} steps, exceeding intelligence.max_plan_steps (${maxPlanSteps})`);
  }
}

export interface PlannerOptions {
  maxPlanSteps: number;
  requireApprovalFor: string[];
}

export class Planner {
  constructor(
    private readonly options: PlannerOptions,
    private readonly templates: PlanTemplate[] = DEFAULT_TEMPLATES
  ) {}

  plan(goal: string): Plan {
    const template = this.templates.find((t) => t.matches(goal));
    const rawSteps = template ? template.steps(goal) : [{ description: goal }];

    if (rawSteps.length > this.options.maxPlanSteps) {
      throw new PlanTooLargeError(rawSteps.length, this.options.maxPlanSteps);
    }

    const steps: PlanStep[] = rawSteps.map((s, i) => ({
      id: `step-${i + 1}`,
      description: s.description,
      category: s.category,
      requiresApproval: s.category ? this.options.requireApprovalFor.includes(s.category) : false,
    }));

    return { goal, templateUsed: template?.name, steps };
  }
}
