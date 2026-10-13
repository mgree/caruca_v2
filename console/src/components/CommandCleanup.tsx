"use client";

/**
 * Delete every run of one command, from the pipeline page.
 *
 * The same three steps as the Runs page's deletion, because the thing worth protecting is the
 * same: see what would go — including anything a campaign result or a finding rests on — then
 * type the word, then delete. Directories and database rows go together; v1's own checkout is
 * out of reach by construction.
 */
import { useState, useTransition } from "react";
import { useRouter } from "next/navigation";
import { confirmCommandDeletion, previewCommandDeletion } from "../app/actions.js";
import type { DeletionAnalysis, DeletionResult } from "../data/deleteRuns.js";
import type { CommandRunIds } from "../data/commandRuns.js";
import { Callout, count } from "./ui.js";

const CONFIRM_WORD = "delete";

function bytes(value: number): string {
  if (value < 1024) return `${value} B`;
  if (value < 1024 * 1024) return `${(value / 1024).toFixed(1)} KB`;
  return `${(value / (1024 * 1024)).toFixed(1)} MB`;
}

export function CommandCleanup({ command }: { command: string }) {
  const router = useRouter();
  const [preview, setPreview] = useState<{ ids: CommandRunIds; analysis: DeletionAnalysis } | null>(null);
  const [typed, setTyped] = useState("");
  const [result, setResult] = useState<DeletionResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [pending, startTransition] = useTransition();

  const open = () => {
    setError(null);
    setResult(null);
    startTransition(async () => {
      try {
        setPreview(await previewCommandDeletion(command));
      } catch (cause) {
        setError((cause as Error).message);
      }
    });
  };

  const run = () => {
    startTransition(async () => {
      try {
        const deletion = await confirmCommandDeletion(command, `every run of ${command}, from the pipeline page`);
        setResult(deletion);
        setPreview(null);
        setTyped("");
        router.refresh();
      } catch (cause) {
        setError((cause as Error).message);
      }
    });
  };

  const total = preview?.ids.all.length ?? 0;

  return (
    <div className="cleanup">
      {!preview && !result ? (
        <button type="button" className="btn" onClick={open} disabled={pending}>
          Delete every run of <span className="mono">{command}</span>…
        </button>
      ) : null}
      {error ? (
        <Callout title="That did not work" tone="warn">
          <p className="mono">{error}</p>
        </Callout>
      ) : null}

      {preview ? (
        <Callout title={`What would go for ${command}`} tone="warn">
          {total === 0 ? (
            <p>Nothing: no run of <span className="mono">{command}</span> is on disk on either side.</p>
          ) : (
            <>
              <p>
                {count(preview.ids.v2.length)} v2 run{preview.ids.v2.length === 1 ? "" : "s"}
                {preview.ids.v2Empty.length > 0
                  ? `, ${count(preview.ids.v2Empty.length)} that recorded nothing`
                  : ""}
                , {count(preview.ids.v1.length)} v1 run{preview.ids.v1.length === 1 ? "" : "s"} —{" "}
                {count(preview.analysis.totalFiles)} files, {bytes(preview.analysis.totalBytes)},{" "}
                {count(preview.analysis.totalMetricsRows)} database row
                {preview.analysis.totalMetricsRows === 1 ? "" : "s"}. Directories and rows go
                together; the deletion is logged. Nothing in v1&apos;s checkout is touched.
              </p>
              {preview.analysis.cited.length > 0 ? (
                <p>
                  <strong>{count(preview.analysis.cited.length)}</strong> of these are cited by a
                  campaign result or a finding; deleting them makes that number uncheckable.
                  They go too if you confirm.
                </p>
              ) : null}
              {preview.analysis.problems.length > 0 ? (
                <p className="mono">
                  {preview.analysis.problems.map((p) => `${p.runId}: ${p.reason}`).join("; ")}
                </p>
              ) : null}
            </>
          )}
          <div className="row" style={{ marginTop: 10 }}>
            {total > 0 ? (
              <>
                <label className="side__meta" style={{ marginTop: 0 }} htmlFor={`cleanup-${command}`}>
                  Type {CONFIRM_WORD} to confirm
                </label>
                <input
                  id={`cleanup-${command}`}
                  className="picker__input mono"
                  value={typed}
                  onChange={(event) => setTyped(event.target.value)}
                  autoComplete="off"
                />
                <button
                  type="button"
                  className="btn btn--primary"
                  disabled={typed.trim() !== CONFIRM_WORD || pending}
                  onClick={run}
                >
                  Delete {count(total)} run{total === 1 ? "" : "s"}
                </button>
              </>
            ) : null}
            <button type="button" className="btn" onClick={() => setPreview(null)} disabled={pending}>
              {total > 0 ? "Keep them" : "Close"}
            </button>
          </div>
        </Callout>
      ) : null}

      {result ? (
        <Callout title="Deleted" tone="neutral">
          <p>
            Removed {count(result.deleted.length)} run{result.deleted.length === 1 ? "" : "s"},{" "}
            {count(result.filesRemoved)} files ({bytes(result.bytesRemoved)}) and{" "}
            {count(result.metricsRowsRemoved)} database row{result.metricsRowsRemoved === 1 ? "" : "s"}.
            Logged at <span className="mono">{result.logPath}</span>.
            {result.failed.length > 0
              ? ` ${count(result.failed.length)} could not be removed: ${result.failed
                  .map((f) => `${f.runId} (${f.reason})`)
                  .join("; ")}.`
              : ""}
          </p>
          <div className="row" style={{ marginTop: 8 }}>
            <button type="button" className="btn" onClick={() => setResult(null)}>
              Close
            </button>
          </div>
        </Callout>
      ) : null}
    </div>
  );
}
