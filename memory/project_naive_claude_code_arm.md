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
- Samples are **tee, bc, grep and rm**, copied byte-for-byte from v1 — so those four **cannot be test
  commands** for this arm.
- `pipe:[N]` entries in the sample annotations stay verbatim; the format doc explains them as pipe
  identifiers from the recorded run with no meaning outside it.
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

**Status.** Package built 2026-10-13; no run yet. Related: [[caruca_v2_baseline_scope]] (the naive
single-prompt control, task 001) and task 007 (agentic SDK arm) are the other two LLM arms.
