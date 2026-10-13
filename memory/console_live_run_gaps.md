---
name: console-live-run-gaps
description: "2026-10-13: the console's live runs cover v1 stages 1-3 and v2 stages 1-4 only; v1 stage 4 has no button and its code path cannot resolve its input; decision 8's OpenRouter meter is not implemented"
metadata:
  type: project
---

Task 010 marks phase 5 (live runs) done, and its README repeats that. **Live coverage is
narrower than either says.** Established 2026-10-13 by reading the console's own source, after
`caruca-v2-03` reported it from its own reading and a live v1 trace run.

**What a live run can actually start**

- v1: `generate`, `generate` at v1's defaults, `syntax-spec`, `trace`, `trace` at v1's defaults.
- v2: all four stages (`startRun.ts` maps them to `naive-llm`, `generate`, `trace`, `annotate`).
- Free tools: `score --self-test`, `metrics rebuild`.

**Three gaps, each read from source**

1. **v1 stage 4 has no button.** `console/src/components/LiveConsole.tsx` calls its start
   function for generate, syntax_spec and trace only. `annotate` appears solely as a label in a
   stage-name map, which is how a reader can mistake the surface for complete — I did, in a
   status report earlier the same day.
2. **The v1 annotate code path could not work if a button existed.** `startRun.ts` builds the
   input as `join(runDir, "<command>.json")`, where `runDir` is the folder the console created
   for *this* run moments earlier, so the traces file would have to be inside a folder that was
   just made empty. `StartV1Options` has no field naming an earlier trace run.
3. **Decision 8's OpenRouter meter does not exist.** No `OPENAI_BASE_URL` anywhere in
   `console/src` or `server.ts`; `processes.ts` passes `env: process.env` unchanged and says so
   in its own comment. But `src/data/pipelinePlan.ts` tells the user on screen that "The
   console's forwarder records the tokens and cost OpenRouter reports". All five v1
   `syntax-spec` records in `eval/v1_runs/` carry null model, prompt tokens, completion tokens
   and cost; two exited 1, two are "stopped", one is "finished". Each lists only four
   environment variable names (PATH, HOME, SHELL, TERM).

**Not established:** whether an OpenAI key was present in those runs' real environment and the
record is filtering the names (task 010 §7 asks for the full list), or whether v1's stage 1 ran
with no credentials at all. The records cannot distinguish the two.

**One defaults question, not a defect.** `startRun.ts` passes `--isolation lima` only when the
chosen location is the VM, else `host`. A v2 stage-3 run left on `host` traces macOS's BSD
`cat` while v1 traces GNU `cat` in the VM, so such a pair would partly measure the platform.
The parity campaigns set isolation to `lima` explicitly, so no published figure is affected.

Also stale: the Pipeline page still says "Nothing here executes anything", untrue since phase 5.

**How to apply:** do not repeat a claim that the console runs all four stages on both sides.
Check `LiveConsole.tsx` for what is reachable and `startRun.ts` for whether the path resolves
its input — the presence of a `case` branch is not evidence of a working route. The full open-item
list belongs in `ai_docs/tasks/010_execution_console.md`; `caruca-v2-03` was writing it there.

Related: [[v1-llm-via-openrouter]] (what decision 8 was meant to achieve),
[[cost-not-reproducible]] (why metering v1's step matters),
[[feedback-never-modify-v1-source]] (fixes go in the wrapper, never v1).
