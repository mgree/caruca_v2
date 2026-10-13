import Link from "next/link";
import { listRuns } from "../../data/runs.js";
import { listV1Runs } from "../../data/v1Runs.js";
import { indexedRunIds } from "../../data/metricsDb.js";
import { Badge, count } from "../../components/ui.js";
import { RunsTable } from "../../components/RunSelection.js";

// Every page reads the run directories at request time, so a run that finishes while the page
// is open shows up on reload. Nothing here is cached or pre-rendered.
export const dynamic = "force-dynamic";

const STAGE_LABEL: Record<string, string> = {
  syntax_spec: "1 · syntax description",
  generate: "2 · command lines and setups",
  trace: "3 · run and trace",
  annotate: "4 · consumer description",
};

/**
 * Every run on disk, as a list.
 *
 * The home screen shows one command's latest runs per step; this is the place to find any run
 * at all, filter by command or step, and delete the ones nothing depends on. The three ways of
 * counting runs disagree, and the note under the heading says how — but it is a note, not the
 * headline, because the list is what people come here for.
 */
export default async function RunsPage({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const params = await searchParams;
  const one = (key: string): string | undefined => {
    const value = params[key];
    return Array.isArray(value) ? value[0] : value;
  };
  const command = one("command");
  const stage = one("stage");

  const { runs, startedWithoutRecord, unreadable } = listRuns();
  const v1 = listV1Runs();
  const indexed = indexedRunIds();
  const orphaned = [...indexed].filter((id) => !runs.some((run) => run.runId === id)).length;

  const shown = runs.filter(
    (run) => (!command || run.command === command) && (!stage || run.stage === stage),
  );
  const filtered = Boolean(command || stage);

  return (
    <main className="page page--wide">
      <div className="accent-bar" />
      <div className="page__head">
        <h1>All runs</h1>
        <Badge mono>{count(shown.length)} v2</Badge>
        <Badge tone="muted" mono>
          {count(v1.runs.length)} v1
        </Badge>
        {filtered ? (
          <span className="spacer">
            <Link href="/runs">Show every run</Link>
          </span>
        ) : null}
      </div>
      <p className="page__sub">
        {filtered ? (
          <>
            v2 runs of{" "}
            {stage ? <span className="mono">{STAGE_LABEL[stage] ?? stage}</span> : "every step"} on{" "}
            {command ? <span className="mono">{command}</span> : "every command"}. Newest first.
          </>
        ) : (
          <>Every v2 run with a record, newest first. v1&apos;s runs appear on each command&apos;s page.</>
        )}
      </p>

      <details className="note">
        <summary>How these are counted, and what is not in the list</summary>
        <p>
          Three sources, three counts: {count(runs.length + startedWithoutRecord.length)} run
          directories on disk, {count(runs.length)} holding a manifest, {count(indexed.size)} known to{" "}
          <span className="code-inline">eval/metrics.db</span>
          {orphaned > 0 ? ` (${count(orphaned)} of those have no directory left)` : ""}.
        </p>
        {startedWithoutRecord.length > 0 ? (
          <p>
            {count(startedWithoutRecord.length)} directories are empty: a run directory is created
            when a run starts and its manifest is written only when it ends, so a run that dies in
            between leaves a shell. They are listed at the bottom of the table and are safe to
            delete — nothing depends on them.
          </p>
        ) : null}
        {orphaned > 0 ? (
          <p>
            {count(orphaned)} runs have rows in the database but no directory. Their per-turn
            tokens, cost and timing survive; their prompts, responses and outputs do not.
          </p>
        ) : null}
        {unreadable.length > 0 ? (
          <p>
            {unreadable.length} directories hold data that could not be parsed. That is a defect to
            investigate, not a run that died.
          </p>
        ) : null}
        {v1.runs.length === 0 ? (
          <p>
            v1 writes no run record of its own, so one exists only for a run this console started.
          </p>
        ) : null}
      </details>

      <RunsTable
        runs={shown.map((run) => ({
          runId: run.runId,
          stage: run.stage,
          command: run.command,
          model: run.model,
          turns: run.turns,
          promptTokens: run.promptTokens,
          completionTokens: run.completionTokens,
          costUsd: run.costUsd,
          status: run.status,
          hasRecording: run.hasRecording,
        }))}
        emptyRunIds={filtered ? [] : startedWithoutRecord}
      />
    </main>
  );
}
