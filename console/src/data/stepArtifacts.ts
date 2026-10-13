/**
 * The two artifacts a step produced, v1's and v2's, as text, for showing side by side.
 *
 * Read from disk at request time and never derived: what the popup shows is the file the
 * step wrote (or, for a v1 annotate run started from the console, the text v1 printed, taken
 * from the terminal recording, since v1's annotate writes to standard output). Large files —
 * traces can run to megabytes — are cut at `CAP_BYTES` and say so.
 */
import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";
import { outputText, readRecording } from "./asciicast.js";
import { repoPaths, v1Root } from "./paths.js";
import { listRuns, type RunSummary } from "./runs.js";
import { listV1Runs } from "./v1Runs.js";
import type { Stage } from "./schema.js";

export const CAP_BYTES = 160 * 1024;

export interface ArtifactText {
  /** Where it came from, in words: "v1's archived LLM output", "run 2026-…". */
  readonly source: string;
  readonly path: string;
  readonly text: string;
  readonly bytes: number;
  readonly truncated: boolean;
  /** `python`, `json` or `text`, for the viewer's own labelling only. */
  readonly kind: "python" | "json" | "text";
}

export interface StepArtifacts {
  readonly command: string;
  readonly stage: Stage;
  readonly v1: ArtifactText | null;
  readonly v2: ArtifactText | null;
}

const ANSI = /\u001b\[[0-9;?]*[A-Za-z]|\u001b\][^\u0007]*\u0007|\r/g;

function readCapped(path: string, source: string, kind: ArtifactText["kind"]): ArtifactText | null {
  if (!existsSync(path)) return null;
  const bytes = statSync(path).size;
  const text = readFileSync(path, "utf8");
  const truncated = text.length > CAP_BYTES;
  return {
    source,
    path,
    text: truncated ? text.slice(0, CAP_BYTES) : text,
    bytes,
    truncated,
    kind,
  };
}

function kindOf(stage: Stage): ArtifactText["kind"] {
  return stage === "syntax_spec" ? "python" : "json";
}

/** v1's artifact for the step: the newest console run where one exists, else the committed file. */
function v1Artifact(command: string, stage: Stage): ArtifactText | null {
  const slug = command.replace(/\s+/g, "_");
  const root = v1Root();
  const paths = repoPaths();
  const v1Runs = listV1Runs().runs.filter((run) => run.manifest.command === command);

  switch (stage) {
    case "syntax_spec": {
      // A live v1 syntax-spec run prints the grammar; the recording holds exactly that text.
      const live = v1Runs.find(
        (run) =>
          run.manifest.subcommand === "syntax-spec" &&
          run.manifest.outcome === "finished" &&
          run.manifest.venv === ".venv-llm" &&
          run.recordingPath,
      );
      if (live?.recordingPath) {
        const text = outputText(readRecording(live.recordingPath)).replace(ANSI, "");
        if (text.includes("_syntax_spec")) {
          return {
            source: `v1's live LLM run ${live.runId}`,
            path: live.recordingPath,
            text,
            bytes: Buffer.byteLength(text),
            truncated: false,
            kind: "python",
          };
        }
      }
      return readCapped(
        join(root, "outputs", "llm-dsl-generation", `${slug}.py`),
        "v1's archived LLM output (what the parity study used)",
        "python",
      );
    }
    case "generate":
      return readCapped(
        join(paths.v1Configs, `${slug}.configs.json`),
        "v1's configuration expansion at the study's bound",
        "json",
      );
    case "trace": {
      const run = v1Runs.find(
        (run) => run.manifest.subcommand === "trace" && existsSync(join(run.dir, `${slug}.json`)),
      );
      if (run) return readCapped(join(run.dir, `${slug}.json`), `v1 run ${run.runId}`, "json");
      return readCapped(
        join(root, "caruca", "outputs", `${slug}.parity.json`),
        "v1's traces at the study's bound",
        "json",
      );
    }
    case "annotate": {
      const run = v1Runs.find(
        (run) =>
          run.manifest.subcommand === "annotate" &&
          run.manifest.outcome === "finished" &&
          run.recordingPath,
      );
      if (run?.recordingPath) {
        const text = outputText(readRecording(run.recordingPath)).replace(ANSI, "");
        return {
          source: `v1 run ${run.runId} (what v1 printed)`,
          path: run.recordingPath,
          text,
          bytes: Buffer.byteLength(text),
          truncated: false,
          kind: "json",
        };
      }
      return readCapped(
        join(root, "caruca", "outputs", `${slug}.parity.pash.json`),
        "v1's PaSh annotation at the study's bound",
        "json",
      );
    }
  }
}

function v2File(run: RunSummary): string | null {
  const slug = run.command.replace(/\s+/g, "_");
  let names: string[];
  try {
    names = readdirSync(run.dir);
  } catch {
    return null;
  }
  const want =
    run.stage === "syntax_spec"
      ? `${slug}.py`
      : run.stage === "generate"
        ? `${slug}.configs.json`
        : run.stage === "trace"
          ? `${slug}.traces.json`
          : names.find((name) => name.endsWith(".annotation"));
  return want && names.includes(want) ? join(run.dir, want) : null;
}

/** v2's artifact for the step: the newest run that finished with a result and wrote its file. */
function v2Artifact(command: string, stage: Stage): ArtifactText | null {
  const runs = listRuns().runs.filter(
    (run) => run.command === command && run.stage === stage && run.status === "ok",
  );
  for (const run of runs) {
    const path = v2File(run);
    if (path) return readCapped(path, `v2 run ${run.runId}`, kindOf(stage));
  }
  return null;
}

export function stepArtifacts(command: string, stage: Stage): StepArtifacts {
  return { command, stage, v1: v1Artifact(command, stage), v2: v2Artifact(command, stage) };
}
