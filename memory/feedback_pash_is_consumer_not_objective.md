---
name: feedback_pash_is_consumer_not_objective
description: 2026-10-13 — PaSh is a consumer of Caruca's output, not the objective; the goal is a strong, repeatable, reproducible syntax description any downstream tool can read, and the immediate job is making the pipeline run and diagnosing execution problems
metadata:
  type: feedback
---

**What Tiran said (2026-10-13, mid-session, while caruca-v2-03 was coordinating the Caruca sessions):**
PaSh is not an objective. Caruca is not designed to optimise for parallel execution. All it needs
to do is generate a very strong, repeatable, reproducible syntax description of a command that
PaSh *can* consume — for the purpose of understanding how the command runs and executes, not how
it can be optimised. Other tools need to consume it too (the ones the paper names: POSH, SaSh /
Shseer, ShellCheck). The immediate-term goal is to get the pipeline to work properly and diagnose
any issues in executing it.

**Why:** this matches Greenberg's 2026-10-06 statement that v1's objective is the overall syntax
definition ([[project_greenberg_caruca_purpose]]) and the near-term scope in
[[caruca_v2_baseline_scope]]. Work that measures PaSh speed-ups (the scheduling sweep in
[[pash_work_scheduling]], width × slice tuning) is a side topic, not the deliverable.

**How to apply:**
- When prioritising, put "all four stages run end to end on both sides, and every failure is
  diagnosed" ahead of any downstream-tool experiment. Task 012's PaSh phases and task 013's
  PaSh-first ordering are *consumers* of a working pipeline, not the reason to build one.
- Frame downstream tools as a *test that the output is consumable* (PaSh first because it is set
  up), not as the thing being optimised. Don't propose PaSh performance work as a v2 objective.
- Measure the syntax description on repeatability and reproducibility (dimension 4) as a
  first-class property, since "repeatable, reproducible" is in the stated goal.
