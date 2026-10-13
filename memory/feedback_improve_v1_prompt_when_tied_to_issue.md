---
name: feedback_improve_v1_prompt_when_tied_to_issue
description: 2026-10-13 — v2 may improve v1's prompt when the change resolves a v1 issue that is documented or that we discovered; the goal is to replicate the pipeline with an LLM, not to be byte-identical
metadata:
  type: feedback
---

**What Tiran said (2026-10-13, answering whether v1's exact prompt should be step 1's default):**
"It's ok to improve v1's prompt — if it resolves issues v1 has (documented or discovered by us).
The goal is to replicate the pipeline with an LLM, but it's ok not to be identical."

**Why:** replication is of the *pipeline* (the four steps, their inputs and outputs), not of
every word. v1's prompt has known defects (for example `tail -c`/`-n` typed wrongly by both
systems, task 011 §3; the `String` type absent from the December 2024 prompt, task 009). Fixing
those is an improvement over v1 that the comparison should show, not hide.

**How to apply:**
- Start from v1's prompt verbatim (allowed since [[project_v1_prompt_licensing]]). Each change
  must name the v1 issue it resolves — a finding file, a task-011 diagnosis line, or a v1 code
  reference — and is recorded in `v2_fidelity_to_v1.md`'s deviation ledger as an improvement.
- A change with no named v1 issue behind it is still tuning (task 011 kind E) and is not made.
- Keep the unchanged-v1-prompt arm measured beside the improved one, so the effect of each
  change is a number. The naive paraphrase (task 001) stays as the control.
- This complements, not replaces, [[feedback_instrument_defect_vs_tuning]] and
  [[feedback_never_modify_v1_source]]: v1 itself is never edited; v2's copy of its prompt is.
