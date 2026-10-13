"use client";

/**
 * The side-by-side popup: v1's artifact on the left, v2's on the right, for one step.
 *
 * A native <dialog>, opened modally so Escape and the backdrop close it. The text is fetched
 * when the button is pressed, not with the page, because a traces file can be megabytes and
 * four steps' worth of them would slow the home screen for nothing.
 */
import { useRef, useState, useTransition } from "react";
import { loadStepArtifacts } from "../app/actions.js";
import type { StepArtifacts, ArtifactText } from "../data/stepArtifacts.js";
import type { Stage } from "../data/schema.js";

function bytes(value: number): string {
  if (value < 1024) return `${value} B`;
  if (value < 1024 * 1024) return `${(value / 1024).toFixed(1)} KB`;
  return `${(value / (1024 * 1024)).toFixed(1)} MB`;
}

function CopyButton({ text, truncated }: { text: string; truncated: boolean }) {
  const [state, setState] = useState<"idle" | "copied" | "failed">("idle");
  const copy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      setState("copied");
    } catch {
      setState("failed");
    }
    setTimeout(() => setState("idle"), 1800);
  };
  return (
    <button
      type="button"
      className="btn btn--small"
      onClick={copy}
      title={truncated ? "Copies the part shown here; the file on disk is longer." : "Copies the whole file."}
    >
      {state === "copied" ? "Copied" : state === "failed" ? "Could not copy" : truncated ? "Copy shown part" : "Copy"}
    </button>
  );
}

function Pane({ side, artifact }: { side: "v1" | "v2"; artifact: ArtifactText | null }) {
  return (
    <section className="artifact-pane" aria-label={`${side}'s output`}>
      <header className="artifact-pane__head">
        <span className="side__name" style={{ margin: 0 }}>
          {side === "v1" ? "v1 · caruca" : "v2 · caruca-v2"}
        </span>
        {artifact ? (
          <>
            <span className="artifact-pane__source" title={artifact.path}>
              {artifact.source} · {bytes(artifact.bytes)}
              {artifact.truncated ? ` · first ${bytes(artifact.text.length)} shown` : ""}
            </span>
            <span className="spacer">
              <CopyButton text={artifact.text} truncated={artifact.truncated} />
            </span>
          </>
        ) : null}
      </header>
      {artifact ? (
        <pre className="artifact-pane__text mono">{artifact.text}</pre>
      ) : (
        <p className="side__empty" style={{ padding: 16 }}>
          Nothing on this side yet for this step.
        </p>
      )}
    </section>
  );
}

export function ArtifactCompare({
  command,
  stage,
  stepName,
  disabled = false,
}: {
  command: string;
  stage: Stage;
  stepName: string;
  /** True when neither side has anything to show, so the button says so instead of opening. */
  disabled?: boolean;
}) {
  const dialog = useRef<HTMLDialogElement>(null);
  const [data, setData] = useState<StepArtifacts | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [pending, startTransition] = useTransition();

  const open = () => {
    setError(null);
    startTransition(async () => {
      try {
        const loaded = await loadStepArtifacts(command, stage);
        setData(loaded);
        dialog.current?.showModal();
      } catch (cause) {
        setError((cause as Error).message);
      }
    });
  };

  return (
    <>
      <button
        type="button"
        className="btn"
        onClick={open}
        disabled={disabled || pending}
        title={disabled ? "Neither side has produced this step yet." : undefined}
      >
        {pending ? "Reading…" : "Side by side"}
      </button>
      {error ? <span className="side__meta">{error}</span> : null}
      <dialog
        ref={dialog}
        className="artifact-dialog"
        aria-label={`${stepName} for ${command}: v1 and v2 side by side`}
        onClick={(event) => {
          // A click on the backdrop lands on the dialog itself, not on its content.
          if (event.target === dialog.current) dialog.current?.close();
        }}
      >
        <div className="artifact-dialog__frame">
          <header className="artifact-dialog__head">
            <h2 style={{ margin: 0 }}>
              <span className="mono">{command}</span> · {stepName}
            </h2>
            <span className="artifact-dialog__hint">
              v1 on the left, v2 on the right. Each pane is the file the step wrote.
            </span>
            <button
              type="button"
              className="btn"
              onClick={() => dialog.current?.close()}
              autoFocus
            >
              Close
            </button>
          </header>
          {data ? (
            <div className="artifact-dialog__panes">
              <Pane side="v1" artifact={data.v1} />
              <Pane side="v2" artifact={data.v2} />
            </div>
          ) : null}
        </div>
      </dialog>
    </>
  );
}
