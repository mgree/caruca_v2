---
name: pash-work-scheduling
description: How PaSh hands input to its parallel workers (fixed-size batches dealt in turn; one process per batch), mapped onto OpenMP's static/dynamic/guided; PaSh has no dynamic or guided, and Tiran decided not to modify PaSh source; width×batch sweep 2026-10-05
metadata:
  type: project
---

Tiran asked on 2026-10-05, from the `~/pash-workers.sh` chart in the `pash` VM, why some workers
start later than others, then whether PaSh can schedule work like OpenMP's
`schedule(static|dynamic|guided)` (the question first said CUDA; Tiran then confirmed it is OpenMP).
Written up in `ai_docs/analysis/pash_work_scheduling.md`.

**The mechanism, verified from PaSh source and a parent-process shim:**
- `r_split` cuts the stream into fixed-size batches (`--r_split_batch_size`, default 1,000,000
  bytes) and deals them to the `-w` lanes in turn: batch k goes to lane k mod width.
- Each lane's `r_wrap` starts a **new** `bash -c 'grep …'` process for every batch. So the
  number of grep processes = number of batches, not the width. 13.8 MB at 1 MB = 13 processes
  on 8 lanes: one wave of 8, then 5. None of the extra processes is a merge step; merging is
  `r_merge`, a separate program.
- Writes to a lane wait until that lane is free, so a slow lane holds up batches meant for
  idle lanes. That is the opposite of dynamic scheduling.

**Mapping to OpenMP:** `static, chunk` = `r_split` with a batch size (supported, tunable).
Plain `static` = the "consecutive chunks" splitter (`runtime/auto-split.sh`, total lines ÷ W);
PaSh chooses it per command from the annotation, with no user flag, but a batch size ≥
input ÷ width makes `r_split` behave the same way. `dynamic` and `guided` do not exist.

**Tiran's decision (2026-10-05): do not modify PaSh source.** Keep its existing strategy;
record the findings. Tiran wants the OpenMP comparison kept for later, when designing Caruca's
annotations for parallelization and optimization, which is explicitly **not** this study's
subject. Batch size and width are run-time flags, so tuning them is allowed.

**Tooling:** `scripts/pash/` (README there): `try-pash.sh`, `pash-workers.sh [width] [copies]
[batch-bytes]` (chart, `--help`), `pash-sweep.sh` (width × batch grid, CSV), and `repro/` (one-line
pipelines for each PaSh behaviour, plus `run-repro.sh`). Re-running the reproducers showed the
double-quote bug needs *single* backslashes inside double quotes, and the `head -5` crash does not
reproduce; `pash_vm_setup.md` §5 corrected. The tracked copies
live in the repo; the VM copies in `~` are pushed with `limactl copy`, since the VM mounts the
Mac read-only. Don't overwrite a script in the VM while it is running.

**Sweep result (430 runs, 0 wrong answers; data `eval/pash_scheduling/`):** best is width 8 +
250 KB slices, 4.73x vs the default (8, 1 MB) 4.29x on 13.8 MB, 5.37x vs 4.99x on 27.7 MB, so
tuning gains 7-10%. Default 1 MB is near-worst because 13.8 MB doesn't divide evenly into 8
lanes (ragged second wave). Width matters far more (4 workers ≈ 3.1x); widths above the VM's 8
CPUs never help. ~0.14 s fixed overhead caps the 13.8 MB run at ~5.5x.

**Email sent 2026-10-05 21:14 to Greenberg and Eiers**, asking Greenberg whether "how to divide
the work" (worker count, chunk size), judged by downstream speedup, is a worthwhile direction.
**Awaiting the answer; until then nothing in task 012 changes.** Context Tiran gave in it: the
link came from course 810C (high-performance computing, Xiaodong Yu), which Eiers recommended;
Tiran made three OpenMP scheduling slides from the course material; dynamic/guided scheduling in
PaSh was framed as a possible *separate* paper. Sent charts: 300 KB slices → 46 slices, 92%
overlap, 4.59x; 1 MB → 13 slices, 79%, 4.18x.

**Not in the sent email** (don't assume the advisors know): the grep runs used PaSh's stock grep
annotation (`pash-annotations` 0.2.4, hash-verified unmodified), so they measure PaSh's work
division, not Caruca annotation quality; and the whole-script question (an annotation's value
depends on its neighbours, so single-command tests show only the best case; task 012 Tier B).
One slip in it: it calls 300 KB "PaSh's default"; the default is 1 MB.

**Host facts that matter for timing:** Mac is an M5 Pro with 18 cores (6 + 12 across two
performance levels); the `pash` VM has 8 vCPUs. Widths above 8 oversubscribe the VM.

Related: [[project-pash-downstream-study]] (task 012; Phase 0 measured a 4.47x speedup at width 8).
