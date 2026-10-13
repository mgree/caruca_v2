---
name: project-dual-objectives
description: "caruca_v2 serves two objectives: near-term feasibility proof, and materials for resubmitting the rejected Caruca white paper"
metadata: 
  node_type: memory
  type: project
  originSessionId: e55744e3-d1dd-487a-99ca-6aa32eb049d4
  modified: 2026-08-29T14:42:57.008Z
---

caruca_v2 has two objectives, not one:

1. **Near-term:** prove that an LLM-based approach can do Caruca-style specification mining at all, and
   demonstrate efficacy (this is what the Master Idea Document's evaluation criteria and MVP components
   are scoped around right now).
2. **Longer-term:** the Caruca white paper (arXiv:2510.14279, see [[caruca_v2_project_overview]]) was
   rejected from its original submission venue. The plan is to revise and resubmit it incorporating v2's
   findings, with explicit documentation of what was adjusted between v1 and v2 and why.

**Why:** Tiran shared this while defining usage scenarios for the Master Idea Document (2026-08-29). It
reframes v2's deliverable from "an internal comparison" to "material for an academic paper resubmission,"
which raises the bar on rigor and documentation, and means the white paper's co-authors (listed in
`ai_docs/prep/master_idea.md`, Stakeholders section) are prospective co-authors on the resubmission, not
just outside evaluators of the approach.

**How to apply:** Any evaluation write-up, methodology description, or results summary produced for v2
should be written at a standard suitable for inclusion in a paper (precise methodology, reproducible
numbers, clear v1-vs-v2 delta documentation), not just informal internal notes. This also raises the
stakes on [[feedback_v1_v2_framing]] — paper reviewers are exactly the audience where framing v2 as
extending v1's capabilities, rather than critiquing v1, matters most.

**Greenberg's guidance, as Tiran restated it to him on 2026-10-05:** the hard part of the
resubmission is not the code engineering but finding the "gold nugget" that makes the paper
interesting. Weigh proposed directions by whether they could be that result, not by how much
engineering they demonstrate. Tiran's current candidate is "how to divide the work" as a
downstream quality measure ([[pash-work-scheduling]]), pending Greenberg's answer.

**The paper's own reviews are not on file (checked 2026-10-13).** `ai_docs/docs/Caruca v1 submission
reviews.md` is NSF's review of Greenberg's 2023 *grant proposal*, not of the paper, and Tiran is not
sure the paper's reviews can be obtained. See [[project-proposal-reviews-vision]].
