---
name: feedback_readme_is_prompt_variant_log
description: 2026-10-13 — Tiran wants the README in `naive_llm_caruca` (formerly "naive_llm_caruca") continuously updated to annotate every prompt version and how the sessions behave differently; update it in the same turn as any prompt change or run
metadata:
  type: feedback
---

On 2026-10-13, while prompt version 2 was being added to the naive Claude Code arm
(`naive_llm_caruca/`), Tiran said: "continuously update the README file in this working
folder to annotate and describe what the different prompts do and how they behave differently."

**Why:** the folder is the experiment's own record. Tiran reads the README, not the task document, to
see what each prompt variation is for and what happened when it ran. The variants only mean something
relative to each other, so the comparison has to live in one place.

**How to apply:**
- The README's "Prompt versions" section has one entry per `PROMPT_v<n>.md` with four parts: what it
  contains or adds, why it exists, what we expect, what was observed. Keep that shape.
- Any turn that adds or edits a prompt file updates its entry (and the summary table) in the same
  turn. Any turn that runs a session, or learns the result of one, fills in or extends "Observed" for
  that version in the same turn.
- Task 016's revision log still gets its one-line entry; the README carries the description and the
  behaviour, the task document carries the decision history.

Related: [[project_naive_claude_code_arm]].
