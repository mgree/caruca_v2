import Link from "next/link";
import { estimateCost } from "../../data/preflight.js";
import { TERMINAL_COLS, TERMINAL_ROWS } from "../../server/processes.js";
import { STAGE_ORDER } from "../../data/pipelinePlan.js";
import { STAGES, type Stage } from "../../data/schema.js";
import { LiveConsole } from "../../components/LiveConsole.js";
import { Badge } from "../../components/ui.js";

export const dynamic = "force-dynamic";

/**
 * Live: run v1 and v2 and watch them (§6.3).
 *
 * Reached from a step on the home screen, in which case only that step's controls are shown
 * (`stage` and `side`), or on its own with every control. The estimates are computed here, on
 * the server, from measured runs — the client is handed figures rather than trusted to work
 * them out, so what the confirmation shows and what the server checks against are the same
 * number.
 */
export default async function LivePage({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const params = await searchParams;
  const one = (key: string) => {
    const value = params[key];
    return Array.isArray(value) ? value[0] : value;
  };

  const command = one("command") ?? "cat";
  const model = one("model") ?? "openai/gpt-4o";
  const stageParam = one("stage");
  const sideParam = one("side");
  const focus =
    stageParam && (STAGES as readonly string[]).includes(stageParam)
      ? { stage: stageParam as Stage, side: sideParam === "v1" ? ("v1" as const) : ("v2" as const) }
      : null;

  const estimates = Object.fromEntries(
    STAGE_ORDER.map((stage) => {
      const estimate = estimateCost(stage, model);
      return [stage, { usd: estimate.usdPerRun, basis: estimate.basis }];
    }),
  );

  return (
    <main className="page page--wide">
      <div className="accent-bar" />
      <div className="page__head">
        <h1>Run</h1>
        <Badge mono>{command}</Badge>
        <Badge tone="muted" mono>
          {model}
        </Badge>
        <span className="spacer row" style={{ gap: 18 }}>
          <Link href={`/?command=${encodeURIComponent(command)}`}>
            ← {command}&apos;s pipeline
          </Link>
          <Link href={`/pipeline?command=${encodeURIComponent(command)}`}>
            What it would run, and cost →
          </Link>
        </span>
      </div>
      <p className="page__sub">
        v1 on the left, v2 on the right, each in a real terminal. The server owns every process,
        so a run survives closing or reloading this page.
      </p>

      <LiveConsole
        command={command}
        model={model}
        cols={TERMINAL_COLS}
        rows={TERMINAL_ROWS}
        estimates={estimates}
        focus={focus}
      />
    </main>
  );
}
