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

## Step 2 runs from the console use a different bound than the v1 pane (observed 2026-10-13)

Established by reading `console/src/components/LiveConsole.tsx` (`startFree`) and
`console/src/server/startRun.ts`, and the manifest of run `2026-10-13T170439Z_cat_143b659b`:

- The console starts a **v1** run with `bounds: { maxCount: 1 }` unless "full" is chosen, and
  the v1 pane of the "Command lines and file setups" diff reads `eval/v1_configs/<cmd>.configs.json`,
  which for `cat` is a max-count-1 file (35 setups, 17 distinct command lines, dated 2026-09-14).
- The console starts a **v2** step-2 run with **no bounds at all**, so the CLI default applies:
  `V1_DEFAULT_MAX_COUNT = 4` in `src/caruca_v2/stages/generate.py`. The prompt told the model
  "at most 4 optional flags", and the built-in comparison scored it against v1 at max-count 4
  (1,392 distinct command lines). The two panes are therefore at different bounds.
- At max-count 4 the model cannot finish: every turn after the first hit the 4,096-token output
  cap, the 4-turn cap stopped it mid-line (3 partial lines dropped), 173 command lines out,
  recall 173/1,392, precision 173/173. Stopping point was inside the three-flag combinations.
- v2's flag nodes use v1's `Flag` model (`node_type: "flag"`, `ir/environment.py:348`), which is
  in the schema the prompt shows but which v1's own serialised output never uses for `cat`
  (v1 writes flags as `args` nodes with `arg_type: "no_env"`). v2 also leaves `string` as `{}`
  and omits `true_string`/`symbol`. Not a scoring issue (comparison is by command line) but a
  shape difference any v1-consuming step would notice.
- v2 emits one setup per path operand (`file`), v1 five (file, empty dir, non-empty dir,
  missing with parent, missing without parent). Expected under the current arm: task 014
  decision 1 makes the five-variant request a *second* arm, not yet built.
