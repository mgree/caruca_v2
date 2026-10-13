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
→ `naive-run [-i] <cmd> [PROMPT_vN.md]` → `./collect_run.sh <name>` (results to
`eval/naive_claude_code/<date>_<name>/`, clone deleted). `limactl clone` needs the source stopped;
`new_run_vm.sh` stops the golden image itself.
Sign-in to the golden image was pending when this was written; check `claude auth status` there.

**Status.** Package built 2026-10-13; no run yet. Related: [[caruca_v2_baseline_scope]] (the naive
single-prompt control, task 001) and task 007 (agentic SDK arm) are the other two LLM arms.
