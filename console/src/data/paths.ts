/**
 * Where everything lives, resolved once.
 *
 * The console is local-only (decision 1), so paths are real absolute paths on this Mac rather
 * than anything configurable per deployment. The repo root is found by walking up for the
 * markers that only caruca_v2's root has, so tests and the server agree without either being
 * told where they are.
 */
import { existsSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

export class RepoNotFoundError extends Error {}

/**
 * Markers that together identify caruca_v2's root and nothing else.
 *
 * Note `src/caruca_v2/harness`, not `harness`: task 010 refers to the scorers as
 * `harness/methods.py` and `harness/rescore.py`, but there is no top-level `harness/` - the
 * package lives inside `src/caruca_v2/`. Using the doc's path as a marker made every lookup
 * walk to the filesystem root.
 */
const ROOT_MARKERS = [
  "pyproject.toml",
  "eval",
  "prompts",
  "src/caruca_v2/harness",
] as const;

function looksLikeRepoRoot(candidate: string): boolean {
  return ROOT_MARKERS.every((marker) => existsSync(join(candidate, marker)));
}

/**
 * Walk up from `start` until the markers appear.
 *
 * `CARUCA_V2_ROOT` overrides the search, but is still checked: an override pointing somewhere
 * wrong should fail loudly here rather than produce an empty run list later that reads as
 * "there are no runs".
 */
export function findRepoRoot(start?: string): string {
  const override = process.env.CARUCA_V2_ROOT;
  if (override) {
    const resolved = resolve(override);
    if (!looksLikeRepoRoot(resolved)) {
      throw new RepoNotFoundError(
        `CARUCA_V2_ROOT is set to ${resolved}, which is not a caruca_v2 checkout ` +
          `(expected all of: ${ROOT_MARKERS.join(", ")}).`,
      );
    }
    return resolved;
  }

  let current = resolve(start ?? dirname(fileURLToPath(import.meta.url)));
  for (;;) {
    if (looksLikeRepoRoot(current)) return current;
    const parent = dirname(current);
    if (parent === current) {
      throw new RepoNotFoundError(
        `No caruca_v2 checkout found above ${start ?? "this file"}. ` +
          `Set CARUCA_V2_ROOT to point at one.`,
      );
    }
    current = parent;
  }
}

export interface RepoPaths {
  readonly root: string;
  /** v2's run directories. One per run, named by run_id. */
  readonly v2Runs: string;
  /** v1's run directories, written by this console only (task 010 §7). */
  readonly v1Runs: string;
  readonly campaigns: string;
  readonly metricsDb: string;
  readonly findings: string;
  readonly prompts: string;
  readonly parityDiffs: string;
  /** v1's own configuration expansions, used when v2 runs on v1's input. */
  readonly v1Configs: string;
}

/**
 * Where the run data lives.
 *
 * Normally `eval/` and `ai_docs/analysis/findings/`. On 2026-10-13 everything recorded before
 * task 014 was moved to `eval/_archive/2026-10-13_parity/` for a clean slate; setting
 * `CARUCA_EVAL_ROOT` to that folder makes the console read the archive instead — which is how
 * the test suite keeps running against real run directories. v1's configuration expansions
 * are inputs, not results, so they stay under `eval/v1_configs/` either way.
 */
export function repoPaths(root = findRepoRoot()): RepoPaths {
  // The override is a reading aid. It applies only where the archive actually exists under
  // this root, so a throwaway root made by a test (which has an `eval/` and no archive) keeps
  // its own folders. Writes never go through it: see `v1RunDir`.
  const requested = process.env.CARUCA_EVAL_ROOT;
  const override =
    requested && existsSync(resolve(root, requested)) ? resolve(root, requested) : null;
  const evalRoot = override ?? join(root, "eval");
  return {
    root,
    v2Runs: join(evalRoot, "runs"),
    v1Runs: join(evalRoot, "v1_runs"),
    campaigns: join(evalRoot, "campaigns"),
    metricsDb: join(evalRoot, "metrics.db"),
    findings: override ? join(evalRoot, "findings") : join(root, "ai_docs", "analysis", "findings"),
    prompts: join(root, "prompts"),
    parityDiffs: join(evalRoot, "parity_diffs"),
    v1Configs: join(root, "eval", "v1_configs"),
  };
}

/**
 * v1's checkout, which the console reads and runs but must never write into (decision 7).
 *
 * Two machines are in play and neither path is canonical (`memory/dev_machine_paths.md`), so
 * this resolves rather than hardcodes. v2's own manifests record the root they used, which is
 * why `inputs.caruca_v1_root` exists.
 */
export function v1Root(): string {
  const fromEnv = process.env.CARUCA_V1_ROOT;
  if (fromEnv) return resolve(fromEnv);
  for (const candidate of [
    join(process.env.HOME ?? "", "dev", "stevens", "caruca"),
    join(process.env.HOME ?? "", "stevens", "caruca"),
  ]) {
    if (existsSync(join(candidate, "caruca"))) return candidate;
  }
  throw new RepoNotFoundError(
    "No v1 checkout found. Set CARUCA_V1_ROOT to the directory containing caruca/.",
  );
}

/**
 * The one folder v1 must never be pointed at: its own working output directory.
 *
 * `$CARUCA_V1_ROOT/caruca/outputs/` holds the parity study's traces and annotations. It is
 * gitignored in v1, so anything overwritten there is gone for good. The pre-flight guard in
 * Phase 4 refuses any v1 command line whose output would land inside it.
 */
export function v1ProtectedOutputs(root = v1Root()): string {
  return join(root, "caruca", "outputs");
}
