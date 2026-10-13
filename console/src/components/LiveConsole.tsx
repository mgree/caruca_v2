"use client";

/**
 * Starting runs and watching them (§6.3).
 *
 * v1 on the left, v2 on the right (decision 4). Each side is a real terminal fed by the
 * server, so what appears is what the program actually shows a person: v1's progress bar
 * redraws in place, and neither program switches to its non-terminal output mode.
 *
 * **Every paid step is confirmed by name before it starts.** v2's four stages always call a
 * model; v1's stage 1 does when it is run live. The confirmation carries the estimate that was
 * shown, and the server refuses the run if that figure has moved — so nobody agrees to one
 * number and is charged against another.
 */
import { useCallback, useEffect, useState, useTransition } from "react";
import {
  liveRuns,
  startV1Run,
  startV2Run,
  startV2ToolRun,
  stopRun,
  type LiveRunSummary,
  type StartedRunSummary,
} from "../app/actions.js";
import { LiveTerminal } from "./LiveTerminal.js";
import { Badge, Callout, Card, usd } from "./ui.js";
import type { Stage } from "../data/schema.js";

const STAGE_LABEL: Record<Stage, string> = {
  syntax_spec: "1 · syntax description",
  generate: "2 · command lines and setups",
  trace: "3 · run and trace",
  annotate: "4 · consumer description",
};
const STAGE_NAME: Record<Stage, string> = {
  syntax_spec: "syntax description",
  generate: "command lines and file setups",
  trace: "run and trace",
  annotate: "consumer description",
};
const STEP_NUMBER: Record<Stage, number> = { syntax_spec: 1, generate: 2, trace: 3, annotate: 4 };

export interface LiveConsoleProps {
  readonly command: string;
  readonly model: string;
  readonly cols: number;
  readonly rows: number;
  /** Per-stage estimates, computed on the server from measured runs. */
  readonly estimates: Record<string, { usd: number | null; basis: string }>;
  /**
   * When set, only this step's controls are shown, for both sides. The home screen links
   * here from a step, so the person arrives with one decision to make, not fourteen buttons.
   */
  readonly focus?: { readonly stage: Stage; readonly side: "v1" | "v2" } | null;
}

interface PendingConfirmation {
  readonly side: "v1" | "v2";
  readonly stage: Stage;
  readonly estimateUsd: number | null;
  readonly basis: string;
}

export function LiveConsole({ command, model, cols, rows, estimates, focus = null }: LiveConsoleProps) {
  const [runs, setRuns] = useState<LiveRunSummary[]>([]);
  const [started, setStarted] = useState<StartedRunSummary[]>([]);
  const [confirming, setConfirming] = useState<PendingConfirmation | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [pending, startTransition] = useTransition();

  /**
   * Reattach on load.
   *
   * The server owns the processes, so a reload finds whatever is still going. This is what
   * makes closing the page harmless.
   */
  const refresh = useCallback(() => {
    startTransition(async () => {
      try {
        setRuns(await liveRuns());
      } catch (cause) {
        setError((cause as Error).message);
      }
    });
  }, []);

  useEffect(refresh, [refresh]);

  /**
   * Runs the server still holds, not only the ones still going.
   *
   * A run can finish in a couple of hundred milliseconds — v1's `generate` does — and showing
   * only running ones means the output flashes past and disappears. The server keeps a
   * finished run's recording and backlog until it is forgotten, so a finished terminal still
   * has something worth reading in it.
   */
  const shown = runs.slice().sort((a, b) => b.startedAt - a.startedAt);
  const active = shown;

  const startFree = (side: "v1" | "v2", stage: Stage, options: { full?: boolean } = {}) => {
    setError(null);
    setMessage(null);
    startTransition(async () => {
      try {
        const summary =
          side === "v1"
            ? await startV1Run({
                stage,
                command,
                // At v1's own defaults this can run for minutes on a wide command, which is
                // what makes it useful for checking that stopping works.
                ...(options.full ? {} : { bounds: { maxCount: 1 } }),
                stage1Mode: "fetch",
              })
            : await startV2Run({
                stage,
                command,
                model,
                confirmation: { acceptedUsd: estimates[stage]?.usd ?? null, confirmed: true },
              });
        setStarted((current) => [summary, ...current]);
        if (summary.concurrentWith.length > 0) {
          setMessage(
            `Started alongside ${summary.concurrentWith.length} other run. Wall-clock times from overlapping runs are not comparable.`,
          );
        }
        refresh();
      } catch (cause) {
        setError((cause as Error).message);
      }
    });
  };

  const startTool = (tool: "score-self-test" | "metrics-rebuild") => {
    setError(null);
    setMessage(null);
    startTransition(async () => {
      try {
        const summary = await startV2ToolRun(tool);
        setStarted((current) => [summary, ...current]);
        refresh();
      } catch (cause) {
        setError((cause as Error).message);
      }
    });
  };

  const confirmAndStart = () => {
    if (!confirming) return;
    const request = confirming;
    setConfirming(null);
    setError(null);
    startTransition(async () => {
      try {
        const summary =
          request.side === "v2"
            ? await startV2Run({
                stage: request.stage,
                command,
                model,
                confirmation: { acceptedUsd: request.estimateUsd, confirmed: true },
              })
            : await startV1Run({
                stage: request.stage,
                command,
                stage1Mode: "live",
                confirmation: { acceptedUsd: request.estimateUsd, confirmed: true },
              });
        setStarted((current) => [summary, ...current]);
        refresh();
      } catch (cause) {
        setError((cause as Error).message);
      }
    });
  };

  const doStop = (runId: string) => {
    startTransition(async () => {
      try {
        const result = await stopRun(runId);
        setMessage(
          result.survivingInVm.length > 0
            ? `${result.detail}. Still running in the VM: ${result.survivingInVm.join("; ")}`
            : result.detail,
        );
        refresh();
      } catch (cause) {
        setError((cause as Error).message);
      }
    });
  };

  /**
   * v1's start buttons, one list so the focused view can filter it by step. Each names what
   * it does in the words the CLI uses, and says when it runs for a long time.
   */
  const v1Buttons: {
    stage: Stage;
    label: string;
    title?: string;
    paid?: boolean;
    onClick: () => void;
  }[] = [
    {
      stage: "syntax_spec",
      label: "syntax-spec --fetch",
      title: "Reads v1's committed grammar. Free.",
      onClick: () => startFree("v1", "syntax_spec"),
    },
    {
      stage: "syntax_spec",
      label: "syntax-spec, live model call",
      title: "v1's one LLM step, through the console. Paid.",
      paid: true,
      onClick: () =>
        setConfirming({
          side: "v1",
          stage: "syntax_spec",
          estimateUsd: null,
          basis: "v1's LLM step has never been metered",
        }),
    },
    {
      stage: "generate",
      label: "generate",
      title: "Prints the command lines; runs nothing. Free.",
      onClick: () => startFree("v1", "generate"),
    },
    {
      stage: "generate",
      label: "generate at v1's defaults (long)",
      title: "The same, at --max-count 4. Minutes on a wide command.",
      onClick: () => startFree("v1", "generate", { full: true }),
    },
    {
      stage: "trace",
      label: "trace in the VM",
      title: "Runs every command line under strace inside the Lima VM. Free.",
      onClick: () => startFree("v1", "trace"),
    },
    {
      stage: "trace",
      label: "trace at v1's defaults (long)",
      title: "The same, at --max-count 4.",
      onClick: () => startFree("v1", "trace", { full: true }),
    },
  ];

  return (
    <div className="stack">
      {error ? (
        <Callout title="That did not work" tone="warn">
          <p className="mono">{error}</p>
        </Callout>
      ) : null}

      {message ? (
        <Callout title="Note" tone="neutral">
          <p>{message}</p>
        </Callout>
      ) : null}

      {confirming ? (
        <Callout title="This calls a paid model" tone="warn">
          <p>
            {confirming.side === "v1" ? "v1" : "v2"} {STAGE_LABEL[confirming.stage]} on{" "}
            <span className="mono">{command}</span> with{" "}
            <span className="mono">{model}</span>.
          </p>
          <p>
            {confirming.estimateUsd === null ? (
              <>
                There is no estimate: nothing comparable has been measured, so the cost is
                genuinely unknown rather than small.
              </>
            ) : (
              <>
                Estimated <span className="mono">{usd(confirming.estimateUsd)}</span> —{" "}
                {confirming.basis}.
              </>
            )}
          </p>
          {confirming.side === "v1" ? (
            <p>
              v1 does not meter its own LLM step, so v1 itself will record no tokens and no
              cost. The console&apos;s meter records what the provider reports, which is the
              first time this step has been costed.
            </p>
          ) : null}
          <div className="row" style={{ marginTop: 10 }}>
            <button className="btn btn--primary" type="button" onClick={confirmAndStart}>
              Start it
            </button>
            <button className="btn" type="button" onClick={() => setConfirming(null)}>
              Cancel
            </button>
          </div>
        </Callout>
      ) : null}

      <Card
        title={
          focus
            ? `Step ${STEP_NUMBER[focus.stage]} on ${command} · ${STAGE_NAME[focus.stage]}`
            : `Start a step on ${command}`
        }
        aside={
          focus ? (
            <a href={`/live?command=${encodeURIComponent(command)}`}>Show every step</a>
          ) : null
        }
      >
        <div className="split">
          <div>
            <div className="side__name">v1 · caruca</div>
            <div className="row" style={{ gap: 8 }}>
              {v1Buttons
                .filter((button) => !focus || button.stage === focus.stage)
                .map((button) => (
                  <button
                    key={button.label}
                    className="btn"
                    type="button"
                    disabled={pending}
                    onClick={button.onClick}
                    title={button.title}
                  >
                    {button.label}
                    {button.paid ? <span className="faint"> paid</span> : null}
                  </button>
                ))}
              {focus?.stage === "annotate" ? (
                <p className="side__empty">
                  v1&apos;s annotate cannot be started from here yet: it needs the trace run to
                  read, and that control is task 014, phase 3. Until then, run it in the VM by hand.
                </p>
              ) : null}
            </div>
            {!focus ? (
              <p className="event__detail faint">
                Free unless marked paid. <span className="mono">generate</span> prints command
                lines and runs nothing; <span className="mono">--fetch</span> reads v1&apos;s
                committed grammar; <span className="mono">trace</span> runs the command lines under
                strace inside the VM and writes into this run&apos;s own folder, never v1&apos;s.
              </p>
            ) : null}
          </div>

          <div>
            <div className="side__name">v2 · caruca-v2</div>
            <div className="row" style={{ gap: 8 }}>
              {(Object.keys(STAGE_LABEL) as Stage[])
                .filter((stage) => !focus || stage === focus.stage)
                .map((stage) => (
                  <button
                    key={stage}
                    className={focus && focus.side === "v2" ? "btn btn--primary" : "btn"}
                    type="button"
                    disabled={pending}
                    onClick={() =>
                      setConfirming({
                        side: "v2",
                        stage,
                        estimateUsd: estimates[stage]?.usd ?? null,
                        basis: estimates[stage]?.basis ?? "no measured runs",
                      })
                    }
                  >
                    {focus ? `Run step ${STEP_NUMBER[stage]} on v2` : STAGE_LABEL[stage]}
                    {estimates[stage]?.usd != null ? (
                      <span className="btn__hint"> ~{usd(estimates[stage]!.usd!)}</span>
                    ) : null}
                  </button>
                ))}
            </div>
            <p className="event__detail faint">
              Every v2 step calls a paid model. The button opens a confirmation with the estimate
              and what it is based on.
            </p>

            {!focus ? (
              <>
                <div className="side__name" style={{ margin: "14px 0 8px" }}>
                  v2 · free tools
                </div>
                <div className="row" style={{ gap: 8 }}>
                  <button
                    className="btn"
                    type="button"
                    disabled={pending}
                    onClick={() => startTool("score-self-test")}
                  >
                    score --self-test
                  </button>
                  <button
                    className="btn"
                    type="button"
                    disabled={pending}
                    onClick={() => startTool("metrics-rebuild")}
                  >
                    metrics rebuild
                  </button>
                </div>
                <p className="event__detail faint">
                  Neither calls a model. <span className="mono">--self-test</span> scores each
                  committed exemplar against itself, so every cell must come out perfect.
                </p>
              </>
            ) : null}
          </div>
        </div>
      </Card>

      {active.length === 0 ? (
        <Callout title="Nothing has run yet" tone="neutral">
          <p>
            Start a step above. A run belongs to the server, not to this page — closing or
            reloading the tab leaves it running, and coming back reattaches to it.
          </p>
        </Callout>
      ) : null}

      {/* v1 on the left, v2 on the right. */}
      <div className="split">
        {(["v1", "v2"] as const).map((side) => {
          const forSide = active.filter((run) => run.side === side);
          return (
            <div key={side} className="stack">
              {forSide.length === 0 ? (
                <div className="terminal">
                  <div className="terminal__head">
                    <span className="label">
                      {side === "v1" ? "v1 · caruca" : "v2 · caruca-v2"}
                    </span>
                    <span className="terminal__where">idle</span>
                  </div>
                  <div className="terminal__empty">
                    <div className="label" style={{ color: "var(--term-dim)" }}>
                      Nothing has run on this side
                    </div>
                  </div>
                </div>
              ) : (
                forSide.map((run) => (
                  <div key={run.runId}>
                    <LiveTerminal
                      runId={run.runId}
                      side={run.side}
                      cols={cols}
                      rows={rows}
                      onFinished={refresh}
                    />
                    <div className="row" style={{ marginTop: 8 }}>
                      <span className="mono faint" style={{ fontSize: "var(--text-caption)" }}>
                        {run.runId}
                      </span>
                      {run.state === "running" ? (
                        <button
                          className="btn"
                          type="button"
                          disabled={pending}
                          onClick={() => doStop(run.runId)}
                        >
                          Stop
                        </button>
                      ) : (
                        <Badge
                          tone={
                            run.state === "exited" ? "ok" : run.state === "stopped" ? "warn" : "bad"
                          }
                        >
                          {run.state}
                          {run.exitCode === null || run.exitCode === 0 ? "" : ` (${run.exitCode})`}
                        </Badge>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          );
        })}
      </div>

      {started.length > 0 ? (
        <Card title="Started in this session" flush>
          <table className="table">
            <thead>
              <tr>
                <th>Run</th>
                <th>Side</th>
                <th>Where</th>
                <th>Paid</th>
                <th>Command</th>
              </tr>
            </thead>
            <tbody>
              {started.map((run) => (
                <tr key={run.runId}>
                  <td className="mono">{run.runId}</td>
                  <td>{run.side}</td>
                  <td>{run.where === "lima" ? "lima vm" : "this mac"}</td>
                  <td>{run.paid ? <Badge tone="warn">paid</Badge> : <Badge tone="ok">free</Badge>}</td>
                  <td className="mono faint" style={{ fontSize: "var(--text-caption)" }}>
                    {run.commandLine}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      ) : null}
    </div>
  );
}
