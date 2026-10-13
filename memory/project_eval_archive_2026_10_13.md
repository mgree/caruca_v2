---
name: project_eval_archive_2026_10_13
description: 2026-10-13 — every pre-task-014 run, the metrics db, the parity campaign ledgers, parity diffs and the 12 finding files were MOVED to eval/_archive/2026-10-13_parity/ for a clean slate; nothing deleted; CARUCA_EVAL_ROOT points the console (and its tests) at the archive
metadata:
  type: project
---

**Decision (Tiran, 2026-10-13):** clear the console's runs and findings so new v1 and v2 runs
start from a clean slate — in particular runs from earlier iterations of the console that did
not track the current telemetry fields or have no terminal recording.

**What was done (2026-10-13, coordinator session):** moved, never deleted, into
`eval/_archive/2026-10-13_parity/` (see its README for the table):
- `eval/runs/` (139 runs + 28 empty shells), `eval/v1_runs/` (24), `eval/metrics.db`,
  `eval/parity_diffs/`, `ai_docs/analysis/findings/` (12 files) — via `git mv`;
- `eval/campaigns/` (the c0_* and p1_* ledgers; **never in git**, still ignored inside the
  archive via `.gitignore: eval/_archive/**/campaigns/`) — via `mv`.
- `eval/metrics.db` rebuilt empty with `caruca-v2 metrics rebuild`. Empty `eval/runs/`,
  `eval/v1_runs/`, `eval/campaigns/`, `ai_docs/analysis/findings/` kept with `.gitkeep`.

**Not moved:** `eval/v1_configs/` (v1's expansions are *inputs*), `eval/e0/`,
`eval/pash_scheduling/`, and v1's own `outputs/*.parity*.json` in v1's checkout.

**How to apply:**
- The parity study's run ids (`2026-09-14T…`) now resolve only under the archive. Set
  `CARUCA_EVAL_ROOT=eval/_archive/2026-10-13_parity` to make the console read them; the
  console's vitest config does this so its reader tests keep running against real directories.
- The home page and Compare show no scores until a new campaign ledger exists in
  `eval/campaigns/`; "Not scored yet" there is expected, not a defect.
- Any new finding goes in the (now empty) `ai_docs/analysis/findings/`.
