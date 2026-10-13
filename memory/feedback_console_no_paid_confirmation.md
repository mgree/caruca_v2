---
name: feedback_console_no_paid_confirmation
description: 2026-10-13 — the console must not prompt before a paid model call; show the estimate on the button and start the run on click (supersedes task 010's confirmation acceptance item)
metadata:
  type: feedback
---

**What Tiran said (2026-10-13), after a "Run step 1 on v2 · grep" click appeared to do
nothing because the Run page was waiting for a second click and a cost confirmation:**
"No need to prompt me for a paid model — remove that step."

**Why:** he runs single commands deliberately; a per-run dialog for a cent or two is friction,
not protection. The ceiling that matters is the task-level one ($40 for task 014, $20 for
task 015), tracked in the task documents, not a click per run.

**How to apply:**
- In the console, a v2 step (and v1's live step 1) starts as soon as its button is pressed, and
  arriving from a step's button on the pipeline page starts it at once. The estimate stays
  visible on the button; the server still refuses a run whose carried estimate is stale.
- Task 010 §10's acceptance item "one paid live run happens only with Tiran's go-ahead" and the
  "paid-call confirmation" item are superseded for the console UI by this decision. Campaigns
  (many commands × samples) are a different scale and still get their cost line in the task
  document before they run ([[project_pipeline_fidelity_decisions]]).
- Don't reintroduce a confirmation for single runs without asking him.
