/**
 * RealityStateOS — Intelligence / Learning
 * Deliberately modest, honest scope: not real ML — a real, simple
 * success/failure weighting per plan template, so repeated outcomes can
 * bias which template is preferred when more than one matches (Planner
 * integration is left to the caller; this module only tracks and reports).
 */

export interface TemplateStats {
  success: number;
  failure: number;
}

export class LearningTracker {
  private stats = new Map<string, TemplateStats>();

  record(templateName: string, outcome: "success" | "failure"): void {
    const current = this.stats.get(templateName) ?? { success: 0, failure: 0 };
    if (outcome === "success") current.success++;
    else current.failure++;
    this.stats.set(templateName, current);
  }

  successRate(templateName: string): number {
    const s = this.stats.get(templateName);
    if (!s || s.success + s.failure === 0) return 0.5; // no data — neutral prior
    return s.success / (s.success + s.failure);
  }

  /** Picks the candidate with the highest observed success rate; ties or no
   * data at all return undefined (caller should fall back to its own default). */
  bestTemplate(candidates: string[]): string | undefined {
    let best: string | undefined;
    let bestRate = -1;
    for (const name of candidates) {
      const rate = this.successRate(name);
      if (rate > bestRate) {
        bestRate = rate;
        best = name;
      }
    }
    return best;
  }

  snapshot(): Record<string, TemplateStats> {
    return Object.fromEntries(this.stats);
  }
}
