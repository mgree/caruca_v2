/**
 * One command's pipeline, step by step, v1 beside v2.
 *
 * This is what the home screen reads. For each of the four steps it answers three questions
 * from files already on disk — never by running anything:
 *
 *   1. What does v1 have for this step? (its committed artifacts, and any run this console
 *      started)
 *   2. What does v2 have? (its runs under `eval/runs/`, newest first)
 *   3. How do they compare? (the parity campaign's scored cell, where one exists)
 *
 * The fourth answer — which step to do next — is the first step where v2 has no run that
 * finished with a result. That is the one action the page puts first.
 */
import { existsSync, readdirSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";
import { buildMatrix, matrixKey, type MatrixCell } from "./compare.js";
import { loadCampaignSet, PARITY_CAMPAIGNS } from "./parityCampaigns.js";
import { repoPaths, v1Root } from "./paths.js";
import { STAGE_ORDER } from "./pipelinePlan.js";
import { listRuns, type RunSummary } from "./runs.js";
import { listV1Runs, type LoadedV1Run } from "./v1Runs.js";
import type { Stage } from "./schema.js";

/** The parity study's nine, always offered even before anything has run on them. */
export const PINNED_COMMANDS = [
  "cat",
  "pwd",
  "rm",
  "sha256sum",
  "tac",
  "tail",
  "tee",
  "uniq",
  "wc",
] as const;

/** Task 014's six confirmation commands, chosen 2026-10-13 before any run. */
export const CONFIRMATION_COMMANDS = ["rmdir", "nl", "du", "dirname", "split", "bc"] as const;

/** A file v1 holds for a step: where it is and what it contains, in one line. */
export interface V1Artifact {
  readonly label: string;
  readonly path: string;
  /** e.g. "35 configurations", "960 executions". Null when the file is absent. */
  readonly summary: string | null;
  readonly present: boolean;
}

export interface V1Side {
  readonly artifacts: V1Artifact[];
  /** The newest run of this step that the console started for v1, if any. */
  readonly latestRun: LoadedV1Run | null;
  readonly runCount: number;
  /** True when every artifact this step needs on v1's side exists. */
  readonly complete: boolean;
}

export interface V2Side {
  readonly runs: RunSummary[];
  /** The newest run, whatever its status. */
  readonly latest: RunSummary | null;
  /** The newest run that finished with a result. */
  readonly latestOk: RunSummary | null;
  readonly okCount: number;
  readonly failedCount: number;
}

export interface StepOverview {
  readonly stage: Stage;
  readonly v1: V1Side;
  readonly v2: V2Side;
  /** The parity campaign's cell for this command and step, where the ledger is on disk. */
  readonly score: MatrixCell | null;
}

export interface CommandOverview {
  readonly command: string;
  readonly steps: StepOverview[];
  /** The first step v2 has not finished with a result; null when all four have one. */
  readonly nextStage: Stage | null;
  /** Campaign ledgers not on this machine, so no score column can be shown. */
  readonly campaignsAbsent: string[];
}

function fileSummary(path: string, describe: (json: unknown) => string | null): string | null {
  try {
    if (!existsSync(path)) return null;
    const text = readFileSync(path, "utf8");
    return describe(JSON.parse(text));
  } catch {
    return "present";
  }
}

function plural(n: number, word: string): string {
  return `${n.toLocaleString("en-US")} ${word}${n === 1 ? "" : "s"}`;
}

/** v1's committed and generated files for one step. Paths only; nothing is executed. */
function v1Artifacts(command: string, stage: Stage, root: string): V1Artifact[] {
  const slug = command.replace(/\s+/g, "_");
  const paths = repoPaths();
  const outputs = join(root, "caruca", "outputs");
  switch (stage) {
    case "syntax_spec": {
      const committed = join(root, "caruca", "src", "caruca", "syntax_specs", `${slug}.py`);
      const archived = join(root, "outputs", "llm-dsl-generation", `${slug}.py`);
      return [
        {
          label: "committed, hand-checked grammar",
          path: committed,
          summary: existsSync(committed) ? "present" : null,
          present: existsSync(committed),
        },
        {
          label: "v1's own LLM output, archived",
          path: archived,
          summary: existsSync(archived) ? "present" : null,
          present: existsSync(archived),
        },
      ];
    }
    case "generate": {
      const path = join(paths.v1Configs, `${slug}.configs.json`);
      const summary = fileSummary(path, (json) =>
        Array.isArray(json) ? plural(json.length, "configuration") : "present",
      );
      return [
        {
          label: "v1's configuration expansion at the study's bound",
          path,
          summary,
          present: summary !== null,
        },
      ];
    }
    case "trace": {
      const path = join(outputs, `${slug}.parity.json`);
      const summary = fileSummary(path, (json) => {
        if (!Array.isArray(json)) return "present";
        // v1's traces file is one group per invocation, each holding one entry per
        // configuration it was executed under (`configs`).
        let executions = 0;
        for (const group of json) {
          const configs = (group as { configs?: unknown })?.configs;
          executions += Array.isArray(configs) ? configs.length : 0;
        }
        return `${plural(json.length, "invocation")} · ${plural(executions, "execution")}`;
      });
      return [
        {
          label: "v1's traces at the study's bound, from the VM",
          path,
          summary,
          present: summary !== null,
        },
      ];
    }
    case "annotate": {
      const path = join(outputs, `${slug}.parity.pash.json`);
      const summary = fileSummary(path, (json) => {
        const cases = (json as { cases?: unknown })?.cases;
        return Array.isArray(cases) ? plural(cases.length, "PaSh case") : "present";
      });
      return [
        {
          label: "v1's PaSh annotation of those traces",
          path,
          summary,
          present: summary !== null,
        },
      ];
    }
  }
}

const V1_SUBCOMMAND: Record<Stage, string> = {
  syntax_spec: "syntax-spec",
  generate: "generate",
  trace: "trace",
  annotate: "annotate",
};

/** Every command that has anything on disk, pinned ones first, then alphabetical. */
export function knownCommands(): string[] {
  const found = new Set<string>([...PINNED_COMMANDS, ...CONFIRMATION_COMMANDS]);
  for (const run of listRuns().runs) found.add(run.command);
  for (const run of listV1Runs().runs) found.add(run.manifest.command);
  try {
    for (const name of readdirSync(repoPaths().v1Configs)) {
      if (name.endsWith(".configs.json")) found.add(name.replace(/\.configs\.json$/, ""));
    }
  } catch {
    // No expansions on disk yet; the pinned list stands.
  }
  const pinned = [...PINNED_COMMANDS, ...CONFIRMATION_COMMANDS] as readonly string[];
  const rest = [...found].filter((c) => !pinned.includes(c)).sort();
  return [...pinned, ...rest];
}

export function commandOverview(command: string): CommandOverview {
  const root = v1Root();
  const v2All = listRuns().runs.filter((run) => run.command === command);
  const v1All = listV1Runs().runs.filter((run) => run.manifest.command === command);

  const campaigns = loadCampaignSet(PARITY_CAMPAIGNS);
  const cells = buildMatrix(campaigns.rows);
  const byKey = new Map(cells.map((cell) => [matrixKey(cell.command, cell.stage), cell]));

  const steps: StepOverview[] = STAGE_ORDER.map((stage) => {
    const artifacts = v1Artifacts(command, stage, root);
    const v1Runs = v1All.filter((run) => run.manifest.subcommand === V1_SUBCOMMAND[stage]);
    const v2Runs = v2All.filter((run) => run.stage === stage);
    const ok = v2Runs.filter((run) => run.status === "ok");
    return {
      stage,
      v1: {
        artifacts,
        latestRun: v1Runs[0] ?? null,
        runCount: v1Runs.length,
        complete: artifacts.every((artifact) => artifact.present),
      },
      v2: {
        runs: v2Runs,
        latest: v2Runs[0] ?? null,
        latestOk: ok[0] ?? null,
        okCount: ok.length,
        failedCount: v2Runs.length - ok.length,
      },
      score: byKey.get(matrixKey(command, stage)) ?? null,
    };
  });

  const next = steps.find((step) => step.v2.latestOk === null);
  return {
    command,
    steps,
    nextStage: next ? next.stage : null,
    campaignsAbsent: campaigns.absent,
  };
}

/** True when `dir` holds the file a v2 run of `stage` writes for `command`. */
export function v2ArtifactPresent(run: RunSummary): boolean {
  const slug = run.command.replace(/\s+/g, "_");
  try {
    const names = readdirSync(run.dir);
    switch (run.stage) {
      case "syntax_spec":
        return names.includes(`${slug}.py`);
      case "generate":
        return names.includes(`${slug}.configs.json`);
      case "trace":
        return names.includes(`${slug}.traces.json`);
      case "annotate":
        return names.some((name) => name.endsWith(".annotation"));
    }
  } catch {
    return false;
  }
}

/** When a run directory was written, for the "last run" line. */
export function runDate(run: RunSummary): string {
  try {
    return statSync(run.dir).mtime.toISOString().slice(0, 10);
  } catch {
    return run.runId.slice(0, 10);
  }
}
