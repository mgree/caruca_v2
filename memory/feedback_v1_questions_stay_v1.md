---
name: feedback-v1-questions-stay-v1
description: When Tiran asks what Caruca v1 is for or why it matters, answer strictly from v1 (the paper + binpash/caruca code) — no v2 objectives, proposed experiments, or resubmission plans mixed in
metadata:
  type: feedback
---

On 2026-10-06 Tiran asked twice, about Caruca **v1**, why its syntax and behaviour specifications
matter if parallelization is not the objective. Claude's answers and explainer pages kept drifting into
v2 material: LLM recall versus observation, "how to measure accuracy against the real program",
proposed demonstrations, and "what the resubmission should show". Tiran corrected it: "again — my
question focuses on caruca v1." Tiran already knows v2's added objectives (replace v1's hard-coded logic
with an LLM without losing fidelity; don't let the LLM's memory of well-known coreutils stand in for
observation).

**Why:** Tiran is trying to understand v1's original intent, as Greenberg describes it ("the overall
syntax definition"; parallelization a side topic). Mixing in v2 plans blurs exactly the distinction
Tiran is trying to get clear.

**How to apply:** for a v1 question, use only what the paper and v1's code and artifacts support: its
stated purpose, design, outputs, consumers, and where its own evaluation is thin. Leave out v2
comparisons, proposed experiments, and future framing unless asked. If a v2 point seems genuinely
relevant, offer it in one line at the end, labelled as v2. Related: [[project-greenberg-caruca-purpose]],
[[feedback-v1-v2-framing]].
