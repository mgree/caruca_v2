import Link from "next/link";
import {
  commandOverview,
  knownCommands,
  runDate,
  CONFIRMATION_COMMANDS,
  PINNED_COMMANDS,
  type StepOverview,
} from "../data/commandOverview.js";
import { estimateCost } from "../data/preflight.js";
import type { Stage } from "../data/schema.js";
import { Badge, usd, count } from "../components/ui.js";
import { ArtifactCompare } from "../components/ArtifactCompare.js";
import { CommandSelect } from "../components/CommandSelect.js";
import { CommandCleanup } from "../components/CommandCleanup.js";
import { v1SupportedCommands } from "../data/v1Commands.js";

// Every page reads the run directories at request time, so a run that finishes while the page
// is open shows up on reload. Nothing here is cached or pre-rendered.
export const dynamic = "force-dynamic";

/**
 * The home screen: one command's pipeline, four steps, v1 beside v2.
 *
 * The three things a person comes here to do, in the order they do them: see where this
 * command stands step by step, run the next step on either side, and open a step's result or
 * its comparison. Everything else — the full run list, the matrix across commands, the
 * findings — is one link away, not on this page.
 */

const STEP: Record<Stage, { name: string; does: string; v1: string; v2: string }> = {
  syntax_spec: {
    name: "Syntax description",
    does: "the man page in; the flags, their aliases and the types of their values out",
    v1: "syntax-spec",
    v2: "naive-llm",
  },
  generate: {
    name: "Command lines and file setups",
    does: "the description in; every command line to test, and the files each one needs, out",
    v1: "generate",
    v2: "generate",
  },
  trace: {
    name: "Run and trace",
    does: "each command line runs in a prepared folder; what it touched is recorded",
    v1: "trace",
    v2: "trace",
  },
  annotate: {
    name: "Consumer description",
    does: "the traces in; the description a tool such as PaSh reads out",
    v1: "annotate",
    v2: "annotate",
  },
};

const STEP_NUMBER: Record<Stage, number> = {
  syntax_spec: 1,
  generate: 2,
  trace: 3,
  annotate: 4,
};

function Picker({ current }: { current: string }) {
  const all = knownCommands();
  const supported = v1SupportedCommands();
  const pinned = new Set<string>([...PINNED_COMMANDS, ...CONFIRMATION_COMMANDS]);
  const others = all.filter((c) => !pinned.has(c));
  const group = (title: string, commands: readonly string[]) => (
    <div className="picker__group">
      <span className="picker__title">{title}</span>
      {commands.map((candidate) => (
        <Link
          key={candidate}
          className={`picker__item mono${candidate === current ? " picker__item--current" : ""}`}
          href={candidate === current ? "/" : `/?command=${encodeURIComponent(candidate)}`}
          aria-current={candidate === current ? "page" : undefined}
        >
          {candidate}
        </Link>
      ))}
    </div>
  );
  return (
    <nav className="picker" aria-label="Command">
      {group("the study's nine", PINNED_COMMANDS)}
      {group("the six confirmation commands", CONFIRMATION_COMMANDS)}
      {others.length > 0 ? group("others with runs", others) : null}
      <div className="picker__group picker__form">
        <span className="picker__title">every command v1 supports</span>
        <CommandSelect
          current={current}
          groups={[
            { label: "the study's nine", commands: PINNED_COMMANDS },
            { label: "the six confirmation commands", commands: CONFIRMATION_COMMANDS },
            {
              label: `all ${supported.length} in v1's syntax_specs/`,
              commands: supported,
            },
          ]}
        />
        <span className="picker__hint">read from v1&apos;s checkout; choosing one opens its pipeline</span>
      </div>
    </nav>
  );
}

function ScoreCell({ step, command }: { step: StepOverview; command: string }) {
  const cell = step.score;
  if (!cell) {
    return (
      <div className="side side--score">
        <div className="side__name">v1 against v2</div>
        <p className="side__empty">Not scored yet. A campaign scores both sides by one instrument.</p>
        <div className="side__actions">
          <ArtifactCompare
            command={command}
            stage={step.stage}
            stepName={STEP[step.stage].name}
            disabled={!step.v1.complete && step.v2.latestOk === null}
          />
        </div>
      </div>
    );
  }
  const verdictTone =
    cell.verdict === "replicates"
      ? "ok"
      : cell.verdict === "improves"
        ? "info"
        : cell.verdict === "diverges"
          ? "warn"
          : "muted";
  const verdictWord = cell.verdict === "unscoreable" ? "not scoreable" : cell.verdict;
  return (
    <div className="side side--score">
      <div className="side__name">v1 against v2</div>
      <div className="score">
        <span className="score__value mono">
          {cell.pooledCounts
            ? `${cell.pooledCounts.top} of ${cell.pooledCounts.bottom}`
            : cell.value === null
              ? "—"
              : cell.value.toFixed(3)}
        </span>
        <Badge tone={verdictTone}>{verdictWord}</Badge>
      </div>
      <div className="side__meta">
        {cell.headline.label} · {cell.samples} sample{cell.samples === 1 ? "" : "s"}
        {cell.spread !== null && cell.spread > 0 ? ` · moved ${cell.spread.toFixed(3)} between samples` : ""}
      </div>
      <div className="side__actions">
        <ArtifactCompare command={command} stage={step.stage} stepName={STEP[step.stage].name} />
        <Link href={`/compare/${step.stage}/${encodeURIComponent(command)}`}>
          How it was scored →
        </Link>
      </div>
    </div>
  );
}

function V1Cell({ step, command }: { step: StepOverview; command: string }) {
  const { v1 } = step;
  const latest = v1.latestRun;
  return (
    <div className="side side--v1">
      <div className="side__name">
        v1 · <span className="mono">caruca {STEP[step.stage].v1} {command}</span>
      </div>
      <ul className="artifacts">
        {v1.artifacts.map((artifact) => (
          <li key={artifact.path} className={artifact.present ? "artifact" : "artifact artifact--absent"}>
            <span className="artifact__mark" aria-hidden="true">
              {artifact.present ? "✓" : "–"}
            </span>
            <span>
              {artifact.label}
              {artifact.summary && artifact.summary !== "present" ? (
                <span className="artifact__summary mono"> {artifact.summary}</span>
              ) : null}
              {!artifact.present ? <span className="artifact__summary"> not on disk</span> : null}
            </span>
          </li>
        ))}
      </ul>
      {latest ? (
        <div className="side__meta">
          Last run from here: {latest.manifest.started_at.slice(0, 10)} ·{" "}
          <span className="mono">{latest.manifest.where === "lima" ? "VM" : "this Mac"}</span> ·{" "}
          {latest.manifest.outcome}
          {v1.runCount > 1 ? ` · ${v1.runCount} runs` : ""}
        </div>
      ) : null}
      <div className="side__actions">
        {step.score ? (
          <Link href={`/compare/${step.stage}/${encodeURIComponent(command)}`}>
            View v1&apos;s output →
          </Link>
        ) : null}
        <Link href={`/live?command=${encodeURIComponent(command)}&stage=${step.stage}&side=v1`}>
          Run v1 <span className="mono">{STEP[step.stage].v1} {command}</span> →
        </Link>
      </div>
    </div>
  );
}

function V2Cell({
  step,
  command,
  isNext,
  estimate,
}: {
  step: StepOverview;
  command: string;
  isNext: boolean;
  estimate: { usd: number | null; basis: string };
}) {
  const { v2 } = step;
  const latest = v2.latestOk ?? v2.latest;
  const runHref = `/live?command=${encodeURIComponent(command)}&stage=${step.stage}&side=v2`;
  return (
    <div className="side side--v2">
      <div className="side__name">
        v2 · <span className="mono">caruca-v2 {STEP[step.stage].v2} {command}</span>
      </div>
      {latest ? (
        <>
          <div className="row" style={{ gap: 8 }}>
            {latest.status === "ok" ? <Badge tone="ok">result</Badge> : <Badge tone="bad">failed</Badge>}
            <span className="side__meta" style={{ marginTop: 0 }}>
              {runDate(latest)} · <span className="mono">{latest.model}</span> ·{" "}
              <span className="mono">{usd(latest.costUsd)}</span> ·{" "}
              <span className="mono">{count(latest.promptTokens + latest.completionTokens)}</span> tokens
            </span>
          </div>
          <div className="side__meta">
            {v2.okCount} with a result
            {v2.failedCount > 0 ? `, ${v2.failedCount} failed` : ""} ·{" "}
            <Link href={`/runs?command=${encodeURIComponent(command)}&stage=${step.stage}`}>all runs of this step</Link>
          </div>
        </>
      ) : (
        <p className="side__empty">No v2 run of this step yet.</p>
      )}
      <div className="side__actions">
        {latest ? (
          <>
            <Link href={`/runs/${latest.runId}`}>View v2&apos;s output →</Link>
            <Link href={`/runs/${latest.runId}/inspect`}>Inside the run →</Link>
          </>
        ) : null}
        {isNext ? (
          <Link className="btn btn--primary" href={runHref}>
            Run step {STEP_NUMBER[step.stage]} on v2 · <span className="mono">{command}</span>
            {estimate.usd !== null ? <span className="btn__hint">~{usd(estimate.usd)}</span> : null}
          </Link>
        ) : (
          <Link href={runHref}>
            Run v2 <span className="mono">{STEP[step.stage].v2} {command}</span> again →
          </Link>
        )}
      </div>
    </div>
  );
}

export default async function HomePage({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const params = await searchParams;
  const raw = params["command"];
  const command = (Array.isArray(raw) ? raw[0] : raw) ?? "cat";
  const model = "openai/gpt-4o";

  const overview = commandOverview(command);
  const nextStep = overview.steps.find((step) => step.stage === overview.nextStage);

  return (
    <main className="page page--wide">
      <div className="accent-bar" />
      <div className="page__head">
        <h1 className="mono">{command}</h1>
        <Badge tone="muted" mono>
          --max-arity 1 --max-count 1
        </Badge>
        <span className="spacer">
          <Link href={`/pipeline?command=${encodeURIComponent(command)}`}>
            What each step would run, and cost →
          </Link>
        </span>
      </div>
      <p className="page__sub">
        Four steps, v1 on the left and v2 on the right. Each step reads the one before it.{" "}
        {nextStep ? (
          <>
            Next for v2: <strong>step {STEP_NUMBER[nextStep.stage]}, {STEP[nextStep.stage].name.toLowerCase()}</strong>.
          </>
        ) : (
          <>v2 has a result at every step.</>
        )}
      </p>

      <Picker current={command} />

      {overview.campaignsAbsent.length > 0 ? (
        <p className="side__meta" style={{ marginBottom: 16 }}>
          No campaign has been scored since the clean slate of 13 October 2026, so the middle
          column has no verdicts yet. A verdict appears once a campaign (
          <span className="mono">caruca-v2 sweep</span>) scores both sides by one instrument; the
          September ledgers are in <span className="mono">eval/_archive/2026-10-13_parity/</span>.
        </p>
      ) : null}

      <ol className="steps">
        {overview.steps.map((step) => {
          const isNext = step.stage === overview.nextStage;
          const estimate = estimateCost(step.stage, model);
          return (
            <li key={step.stage} className={`step${isNext ? " step--next" : ""}`}>
              <div className="step__title">
                <span className="step__n" aria-hidden="true">
                  {STEP_NUMBER[step.stage]}
                </span>
                <h2>
                  <span className="sr-only">Step {STEP_NUMBER[step.stage]}: </span>
                  {STEP[step.stage].name}
                </h2>
                <span className="step__does">{STEP[step.stage].does}</span>
              </div>
              <div className="step__grid">
                <V1Cell step={step} command={command} />
                <ScoreCell step={step} command={command} />
                <V2Cell
                  step={step}
                  command={command}
                  isNext={isNext}
                  estimate={{ usd: estimate.usdPerRun, basis: estimate.basis }}
                />
              </div>
            </li>
          );
        })}
      </ol>

      <p className="page__foot">
        Across every command: <Link href="/compare">the comparison matrix</Link> ·{" "}
        <Link href="/runs">all runs</Link> · <Link href="/findings">findings</Link>
      </p>

      <section className="housekeeping" aria-label="Housekeeping">
        <h2>Start <span className="mono">{command}</span> over</h2>
        <p className="side__meta" style={{ margin: "4px 0 10px", maxWidth: "72ch" }}>
          Removes every run of this command on both sides — v2&apos;s run folders, any that
          recorded nothing, the v1 runs started from here — and their database rows. v1&apos;s own
          files and its checkout are never touched. You see what would go before anything does.
        </p>
        <CommandCleanup command={command} />
      </section>
    </main>
  );
}
