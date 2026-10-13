---
name: project_naive_claude_code_arm
description: Third, simplest arm created 2026-10-13 — a fresh Claude Code CLI session gets only a problem statement, two format docs and four verbatim v1 samples (tee, bc, grep, rm); folder "Caruca via Claude Code CLI" at repo root; must run from a copy outside any checkout
metadata:
  type: project
---

**The arm.** On 2026-10-13 Tiran asked for a deliberately naive experiment that is neither v2 nor a
replication of v1's pipeline: hand a fresh Claude Code CLI session only a description of the objective
(produce the two files v1 produces per command, `<cmd>.py` syntax description and `<cmd>.json` PaSh
annotation, for downstream consumers such as PaSh), a plain-language description of each file's format,
and samples of finished output. No method hints, no guardrails, no mention of how v1 works. The research
question is how an unguided session solves it (does it read docs, run the binary, isolate it, trace it?).

**Where.** Repo-root folder `Caruca via Claude Code CLI/` (name chosen by Tiran, spaces included):
`PROMPT_v1.md` and `PROMPT_v2.md` (each with a `{{COMMAND}}` placeholder), `formats/`, `samples/`, `output/`, and an operator
`README.md` the session must not see. Design record: `ai_docs/tasks/016_naive_claude_code_arm.md`.

**Decisions (Tiran, 2026-10-13).**
- Samples are **tee, uniq, grep and rm** — so those four **cannot be test commands** for this arm.
  (Originally tee, bc, grep, rm; `bc` dropped the same day because PaSh has no annotation for it.)
- **Review feedback applied 2026-10-13** (from Prof. Michael Greenberg, inline comments on Discord, relayed by Tiran; summarised in the README section "Michael's feedback and what changed"): the behaviour
  annotation is PaSh's current Python form — parser table `<cmd>.json` + `InputOutputInfoGenerator<Cmd>.py`
  + `ParallelizabilityInfoGenerator<Cmd>.py`, as in github.com/binpash/annotations (`pash_annotations`
  0.2.4, MIT, installed in the pash VM; samples copied from there) — not v1's JSON; the prompt names
  `{{PATH}}` and `{{MANPAGE_PATH}}`; uses "argument syntax (options, option argument types, operand
  types)"; closes with "generate a correct spec without my intervention… test the binary against the
  spec". The syntax deliverable stays v1's Python DSL.
- The session runs from a copy placed outside any checkout (e.g. `~/naive-arm` in the Lima VM) because
  Claude Code auto-loads `CLAUDE.md` from the cwd and every parent, and caruca_v2's CLAUDE.md describes
  v1's whole pipeline.
- Headless runs use `claude -p ... --output-format stream-json --verbose`; verified against Claude Code
  2.1.293 on the Mac that stream-json requires `--verbose` in print mode.

**Prompt versions (2026-10-13).** Tiran wants graded variations. v1 = objective + formats + samples
only. v2 = v1 plus one guidance section: derive parameters and behaviour by executing the command
across its variations (not from memory); treat probing as an experiment (repeatability,
reproducibility); establish and report the OS and command version because core utilities differ
across Unix flavours and versions. Later versions get the next number and a line in task 016's
revision log; each run records which version it used.

**Claude Code in the VM (2026-10-13).** Installed in Lima `caruca` with the native installer
(`curl -fsSL https://claude.ai/install.sh | bash`), version 2.1.296, at `~/.local/bin/claude` in the
guest home (on PATH via `.profile`, so use `bash -lc`). Tiran signed in on 2026-10-13 with the claude.ai account (Max
subscription; `claude auth status` confirms), so runs bill the subscription, not an API key. Package copy lives at `~/naive-arm` (guest home), written by
`Caruca via Claude Code CLI/sync_to_vm.sh`, README excluded. No CLAUDE.md exists above it. Residual
hazard: the Mac home (both checkouts) is mounted at `/Users/tirandagan` inside the VM.

**Golden image (2026-10-13).** Runs use a clone of Lima VM `naive-golden`, not the caruca VM: created
with `limactl create --name=naive-golden template:ubuntu-24.04 --mount-none --cpus 4 --memory 4 --disk 20`;
Claude Code 2.1.296 installed (native installer); package at `~/naive-arm` (guest home
`/home/tirandagan.guest`); no mounts, no `/Users` inside. Stock image already has `strace` and
`unshare`; `kernel.apparmor_restrict_unprivileged_userns=1` left as stock. Reset = `limactl clone
naive-golden <run>` then `limactl delete -f <run>`; `limactl snapshot` is **unimplemented on vz**
(verified) and qemu is not installed. `sync_to_vm.sh [vm]` copies the package with `limactl copy`. Run flow (scripts in the folder,
tested 2026-10-13): `./new_run_vm.sh <name>` → `limactl shell <name>` (welcome lands in `~/naive-arm`)
→ `naive-run [-i] <cmd> [PROMPT_vN.md]` → `./collect_run.sh <name>` (results to the package's
`runs/<date>_<name>/`, clone deleted). `limactl clone` needs the source stopped;
`new_run_vm.sh` stops the golden image itself.
Sign-in to the golden image was pending when this was written; check `claude auth status` there.

**Command rules in `naive-run` (Tiran, 2026-10-13).** No hard blocks: any installed command runs. The
**core nine** of the parity study (`cat grep pwd rm tac tail tee uniq wc`, confirmed from
`ai_docs/analysis/v1_v2_parity_study.md` and task 012) run without a question; anything else warns
and asks y/N; the four samples (tee uniq grep rm) print a note and run. Tiran first asked to be able
to enter grep (a sample) after the helper refused it, then asked for the confirmation on non-core
commands.

**Tool-call logging (2026-10-13).** No CLI flag logs tool calls for an interactive session. Verified:
Claude Code 2.1.29x writes every session to `~/.claude/projects/<cwd-slug>/<session-id>.jsonl`
(`assistant` records with `tool_use` blocks carrying name + full input; `user` records with
`tool_result`; timestamps). Headless `-p --output-format stream-json --verbose` has the same blocks
plus a final `result` event. `naive-run` copies the newest transcript to `runs/<tag>.transcript.jsonl`;
`collect_run.sh` copies `~/.claude/projects`; `tool_log.py` renders either file. `--debug-file` is an
internal debug log, not a tool log.

**Watch mode (2026-10-13).** Tiran wants to see progress on screen with tool names, inputs and
results (not thinking) and a complete action log; interactive `claude "<prompt>"` only prefills the
input box (his sed session sat until he typed something). So `naive-run` defaults to watch mode:
`claude -p … --output-format stream-json --verbose --permission-mode bypassPermissions | naive-watch.py`,
rendering live and writing `<tag>.jsonl` + `<tag>.actions.log`. In `-p` mode tools needing
permission are denied unless allowed, hence bypass in the throwaway VM (recorded in `<tag>.env`).

**Layout leak found by run 1 (2026-10-13).** Run 1 (sed, v1, interactive, clone `naive-run-grep`,
45 tool calls, ~8 min, all four files produced) read `PROMPT_v2.md` and `runs/sed_PROMPT_v1.env`
from its cwd, searched the filesystem for caruca/pash_annotations, and queried the GitHub API for
"caruca". Fix: prompts in `~/prompts`, logs in `~/runs`; `~/naive-arm` holds only formats/, samples/,
output/. Run 1 was collected and then **deleted by Tiran** on 2026-10-13 evening (leaky layout, old helper);
only the README's Observed summary survives. Tiran's call: all deliverables, scripts and collected
runs stay in the package folder; `runs/` is never copied into a VM because `sync_to_vm.sh` stages
only prompts, formats/, samples/.

**Per-run packaging (Tiran, 2026-10-13 evening).** Every `naive-run` invocation gets its own
`~/runs/<date>_<time>_<vm>_<cmd>_<version>/` with prompt.md, output/, stream.jsonl, stream.actions.log,
transcript_<session>.jsonl, run.env (incl. `run_number_in_this_clone`); output/ is emptied after each
run; `collect_run.sh <vm> [--keep]` copies each run folder into the package's `runs/` unchanged and
saves the clone's session store once. Tested 2026-10-13 with a stand-in `claude` (two runs in one
clone → two folders). Tiran also wants no accumulation of several runs in one folder.

**Status.** Package built 2026-10-13; run 1 done the same day (see above). Related: [[caruca_v2_baseline_scope]] (the naive
single-prompt control, task 001) and task 007 (agentic SDK arm) are the other two LLM arms.
