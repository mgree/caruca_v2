/**
 * Every run directory that belongs to one command, on both sides, for deleting them together.
 *
 * Three sources, because a command's traces are in three places: v2's runs with a manifest,
 * v2's directories that recorded nothing (a run that died before its manifest), and the v1
 * runs this console started. Run ids carry the command (`<time>_<command>_<hash>`), which is
 * how the empty shells are matched; the other two are matched on their records.
 */
import { listRuns } from "./runs.js";
import { listV1Runs } from "./v1Runs.js";

export interface CommandRunIds {
  readonly v2: string[];
  readonly v2Empty: string[];
  readonly v1: string[];
  readonly all: string[];
}

export function runIdsForCommand(command: string): CommandRunIds {
  const marker = `_${command.replace(/\s+/g, "_")}_`;
  const v2All = listRuns();
  const v2 = v2All.runs.filter((run) => run.command === command).map((run) => run.runId);
  const v2Empty = v2All.startedWithoutRecord.filter((name) => name.includes(marker));
  const v1 = listV1Runs()
    .runs.filter((run) => run.manifest.command === command)
    .map((run) => run.runId);
  return { v2, v2Empty, v1, all: [...v2, ...v2Empty, ...v1] };
}
