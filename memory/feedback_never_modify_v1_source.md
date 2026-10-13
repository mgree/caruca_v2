---
name: feedback_never_modify_v1_source
description: 2026-10-13 — v1's source is never modified (wrapper/console fixes only); v1 issues are captured as findings, improvements are made in v2 and noted as incremental differences
metadata:
  type: feedback
---

**What Tiran said (2026-10-13):** "We are not to touch V1 or change it. Whatever V1 does, unless
the wrapper needs to be fixed, the original Caruca is not to be touched. We are going to capture
issues with V1, but we have an opportunity to improve it with V2 and note what we're doing that is
incrementally different. We're not touching the source code for V1."

**Why:** v1 is the baseline being measured. A modified baseline is not the paper's system, and
co-authors (Greenberg) own it. The same rule already applies to PaSh ([[pash_work_scheduling]]:
"don't modify PaSh source").

**How to apply:**
- No edits under `~/stevens/caruca/` (Mac: `~/dev/stevens/caruca/`), including `llm.py`'s DSPy
  breakage, the `gpt-4o` hardcode, `tracer/data.py`'s macOS `/tmp` path, `cli/trace.py`'s
  `--output` help text, or `generate --number`. Redirect v1 from the *outside* only: environment
  variables (`OPENAI_BASE_URL`, `CARUCA_ISOLATION_METHOD`), a separate virtualenv (`.venv-llm`),
  running it inside the Lima VM, or the console wrapper.
- "Wrapper" = the console (`console/`) and v2's `v1.py` runner. Those may be fixed freely.
- Every v1 defect becomes a finding (`ai_docs/analysis/findings/`) and, where v2 does better, an
  entry in `v2_fidelity_to_v1.md`'s deviation ledger marked as a deliberate increment — never a
  patch to v1.
- This supersedes any earlier suggestion that task 005 would "instrument v1" by editing it; v1
  telemetry must come from the wrapper (the console's run records and the metering forwarder).
- Watch for accidental modification: on 2026-10-13 `caruca/save/ls.json` in v1's checkout showed
  as modified (mtime 2026-09-03, the Lima setup day) — report such things to Tiran, don't fix
  silently.
