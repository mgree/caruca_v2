---
name: project-greenberg-caruca-purpose
description: Greenberg's position (relayed by Tiran 2026-10-06) — v1's objective is the OVERALL SYNTAX DEFINITION of a command (grammar + observed behaviour), parallelization is a side topic, grep is his flagship example; the final v1-only answer and where the paper's evidence doesn't match
metadata:
  type: project
---

**Greenberg's position, as Tiran relayed it on 2026-10-06:** Caruca v1 is not a PaSh-annotation
generator. Its objective is the **overall syntax definition** of a command, and parallelization is at
most a side topic. He keeps using **grep** as the example. Tiran had built the PaSh downstream study
([[project-pash-downstream-study]]) on the parallelization reading. That work is valid as one consumer
test, but it is not v1's objective.

**The answer Tiran's question needed** ("if not parallelization, what does v1's syntax and behaviour
understanding give beyond man pages plus hand-written notes?"), from the paper and v1's code only. It is
written up in `ai_docs/analysis/caruca_purpose_grep_case.md` version 2.1, and the picture version is
https://claude.ai/artifact/3KyQ3VEiFq5o6VnrPzMrvC version 4:

- A shell script is thin glue around opaque commands. In the paper's htmx example the shell only sets
  order, `*` and `>`. Any tool reasoning about scripts needs a model of each command. This is the shell
  analogue of the library models program analysers depend on (KLEE's POSIX models, FlowDroid's
  source/sink lists). v1 generates the model: **syntax** (the LLM reads the man page; nothing else) plus
  **behaviour** (observed only by running and tracing). The paper: "The LLM solely generates the syntax
  specification".
- The syntax spec is the **ceiling**. Job 1: v1 builds every test command line from it (8,749,056
  configurations for `rm`), so a shape the grammar lacks is never tested as documented
  ([[caruca-grep-grammar-single-shape]]). Job 2: tools read it directly. v1's ShellCheck adapter derives
  argument checks from it ([[caruca-v1-pipeline-reference]]).
- Behaviour beyond the man page: the paper's `rm` table, 4 flag combinations × file / folder / missing,
  giving what is deleted and the exit code. That is what Shseer consumes.
- **Where the paper's evidence doesn't match that objective.** This is the source of Tiran's unease.
  69 of 88 reference specifications come from parallelizers (PaSh 52, POSH 17), and 5 of the 8 derived
  properties serve them. Outside v1's own test generation and coverage study (`caruca oracle` over 666,468 real command lines), the grammar is shown in use only through 6 ShellCheck checks.
  Grammar accuracy means agreement with hand-written grammars (116/120 published, 78/116 by v1's own
  tool, [[caruca-v1-stage1-baseline]]), and on grep the reference shares the LLM's gap. The
  cross-platform motivation is untested even though v1 holds the material
  ([[caruca-v1-cross-platform-assets]]).
- Three v1 questions for Greenberg: (1) which family of tools v1 was built to serve, given the 69/88
  weighting; (2) whether "syntax definition" means the grammar alone or grammar plus behaviour; (3)
  whether grammar accuracy means matching the hand-written reference or covering every documented
  shape.

**How the answer evolved, so it isn't repeated.** The first answer and explainer (version 1) centred on
"tear the book" input splitting, which is the wrong emphasis. The second version mixed in v2
objectives and proposed experiments, which was the wrong scope ([[feedback-v1-questions-stay-v1]]). Only
the third version is v1-only and syntax-centred.

**Why:** this changes the yardstick for judging v1 from "does PaSh go faster" to "is the command model
right and complete, and who can use it". It also bears on the resubmission ([[project-dual-objectives]]).

**How to apply:** in anything Greenberg will read, frame v1's purpose as the command model (syntax plus
behaviour) for tools that reason about scripts, and treat parallelization as one derived property. When
grep comes up, lead with the syntax shapes, not splitting. For PaSh's grep annotation facts, see
[[pash-grep-annotation-current-vs-json]].
