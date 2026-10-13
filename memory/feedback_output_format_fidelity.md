---
name: feedback_output_format_fidelity
description: 2026-10-13 — at every pipeline step v2's output must replicate v1's file format precisely (then equal or better precision); the prompt must show the LLM the exact JSON structure expected, with a filled example; bookkeeping fields v1 derives mechanically are re-emitted through v1's own model
metadata:
  type: feedback
---

**What Tiran said (2026-10-13), after comparing step 2's output in the console's side-by-side
popup and finding v2's configurations carried `"string": {}` where v1 fills the invocation's
structure:** "You need to compare the output for each step in the pipeline and adjust the
prompts until we replicate the format precisely with identical or improved precision. Give the
LLM (in the prompt) the structure of the JSON output we expect."

**Why:** the artifacts are what downstream tools and the comparison read; a file that differs
in shape from v1's cannot be compared like with like, and a reviewer reading the two side by
side should see the same document with different contents, not two formats.

**How to apply (every step, task 014 phase 2):**
1. Compare v1's file and v2's for the same command field by field (the popup, or
   `stepArtifacts`). Record each difference and whether v1 reads the field back (most
   bookkeeping it does not: `tracer/data.py:67` recomputes `true_string` from the model).
2. Put v1's **exact structure** in the prompt: the schema v1's model defines *and* one filled
   example taken from v1's own output for an exemplar command, with each field named and its
   meaning stated (what `string`, `true_string`, `symbol`, `arg_type` are). This is a request
   repair (task 011 kind B): v1's schema alone under-specifies what v1 expects.
3. Fields v1 derives mechanically (`true_string`, `string`, `symbol`) are **also re-emitted
   through v1's own model** after the model answers, so the on-disk file is byte-for-byte in
   v1's shape regardless of what the model wrote; the raw model output is kept beside it.
   The deviation ledger (`v2_fidelity_to_v1.md`) records this as alignment.
4. Only then compare precision. "Identical or improved" is the bar; a prompt change not tied to
   a named format difference or v1 issue is still tuning and is not made
   ([[feedback_improve_v1_prompt_when_tied_to_issue]]).
- Step 2's gap found 2026-10-13 on `cat`: v2 173 entries vs v1 35 (the flag-limit rule, task
  011 §3) and the three missing bookkeeping fields above.
