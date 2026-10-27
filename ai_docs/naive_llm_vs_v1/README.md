<!-- ATTRIBUTION-NOTICE:START -- required by LICENSE-TEMPLATES.md, do not remove -->
<!-- caruca_v2 analysis document. Created by Tiran Dagan. Copyright (c) 2026 Tiran Dagan.
     Licensed under the PolyForm Noncommercial License 1.0.0
     https://polyformproject.org/licenses/noncommercial/1.0.0
     Noncommercial use only. Commercial use is prohibited. -->
<!-- ATTRIBUTION-NOTICE:END -->

# Naive LLM vs Caruca: start here

**The project's current focus (since 20 October 2026).** A general-purpose coding agent (Claude Code,
model Claude Fable 5.1), given only the goal, two format descriptions and four finished examples, writes
the same syntax files Caruca (v1) produces. This page is the single entry point: what to read first, where
every piece of evidence is, every chart, and which older material is dated. Updated 2026-10-27.

**Words used throughout.** A *syntax file* is the Python file describing a command's options, the kind of
value each takes, and the files it works on. Caruca keeps three kinds: its **answer key** (hand-curated
reference files, `syntax_specs/`), its **GPT-4o output** (what Caruca's own language-model step wrote,
`outputs/llm-dsl-generation/`), and, from this project, **the agent's** file from each naive run.

## 1. Read first

| Document | What it gives you |
|---|---|
| [**Observations: naive LLM vs Caruca**](observations.md) | The short answer: which is better in quality, which is faster, the score of every file, samples side by side, how the approaches are alike and different |
| [Latest findings](../analysis/latest_findings.md) | Every finding of the project, dated, newest first, each linked to its evidence |
| [The three findings in one picture](../diagrams/003_naive_llm_three_findings.png) | Ask the command, not only its manual · many generated test lines do nothing · inventive but a poor judge of its own work |

![The three naive-LLM findings](../diagrams/003_naive_llm_three_findings.png)

## 2. Where each answer lives

| Question | Document | Status |
|---|---|---|
| How was the agent set up (prompt, formats, examples, VM), and what did each run do? | [`naive_llm_caruca/README.md`](../../naive_llm_caruca/README.md) (one "Observed, run N" entry per run) · design record [task 016](../tasks/016_naive_claude_code_arm.md) | current |
| What scores does each syntax file get? | [Task 018](../tasks/018_naive_vs_caruca_syntax_scoring.md) (method) · [scores table](../../naive_llm_caruca/scoring/results/summary.md) · one JSON per command with every count in [`scoring/results/`](../../naive_llm_caruca/scoring/results/) | current, 2026-10-27 |
| Exactly how do the three syntax files differ, checked on the program? | [Syntax files vs v1](../analysis/naive_llm_syntax_files_vs_v1.md) (`rm`, `cut`, `sort`, `convert`) · scripts and raw results in [`comparisons/2026-10-26_syntax_files_vs_v1/`](../../naive_llm_caruca/comparisons/2026-10-26_syntax_files_vs_v1/README.md) | current, 2026-10-26 |
| What should the Caruca paper add? (written for the co-authors) | [Naive LLM addendum](../analysis/white_paper_addendum_naive_llm.md) ([PDF](../analysis/white_paper_addendum_naive_llm.pdf)), version 0.5 | current, 2026-10-27 |
| What did one run do, call by call? | the run's `analysis/analysis.md` (table below) | current |

## 3. The runs

One command per run, one run per command, prompt version 1, no web access from run 4 on. Times and costs
are the agent session's own figures (list price, billed to the subscription).

| Run | Date | Command | Time | Cost | Analysis | PDF | Diagrams |
|---|---|---|---|---|---|---|---|
| 3 | 2026-10-13 | `grep` (Claude Haiku 5.5, web on: context only) | 739 s | $0.96 | [analysis](../../naive_llm_caruca/runs/2026-10-13_193448_naive-run-grep_grep_PROMPT_v1/analysis/analysis.md) | — | [session](../../naive_llm_caruca/runs/2026-10-13_193448_naive-run-grep_grep_PROMPT_v1/analysis/session_workflow.png) · [information flow](../../naive_llm_caruca/runs/2026-10-13_193448_naive-run-grep_grep_PROMPT_v1/analysis/information_flow.png) |
| 4 | 2026-10-20 | `grep` (an example the agent was shown) | 322 s | $2.54 | [analysis](../../naive_llm_caruca/runs/2026-10-20_112956_naive-run-grep-noweb_grep_PROMPT_v1/analysis/analysis.md) | [PDF](../../naive_llm_caruca/runs/2026-10-20_112956_naive-run-grep-noweb_grep_PROMPT_v1/analysis/analysis.pdf) | [session](../../naive_llm_caruca/runs/2026-10-20_112956_naive-run-grep-noweb_grep_PROMPT_v1/analysis/session_workflow.png) · [information flow](../../naive_llm_caruca/runs/2026-10-20_112956_naive-run-grep-noweb_grep_PROMPT_v1/analysis/information_flow.png) · [Caruca's design vs agent](../../naive_llm_caruca/runs/2026-10-20_112956_naive-run-grep-noweb_grep_PROMPT_v1/analysis/v1_design_vs_agent.png) · [run 3 vs run 4](../../naive_llm_caruca/runs/2026-10-20_112956_naive-run-grep-noweb_grep_PROMPT_v1/analysis/run3_vs_run4.png) |
| 5 | 2026-10-20 | `rm` (an example the agent was shown) | 60 s | $0.80 | [analysis](../../naive_llm_caruca/runs/2026-10-20_121932_naive-run-rm_rm_PROMPT_v1/analysis/analysis.md) | [PDF](../../naive_llm_caruca/runs/2026-10-20_121932_naive-run-rm_rm_PROMPT_v1/analysis/analysis.pdf) | [session](../../naive_llm_caruca/runs/2026-10-20_121932_naive-run-rm_rm_PROMPT_v1/analysis/session_workflow.png) · [information flow](../../naive_llm_caruca/runs/2026-10-20_121932_naive-run-rm_rm_PROMPT_v1/analysis/information_flow.png) · [Caruca's design vs agent](../../naive_llm_caruca/runs/2026-10-20_121932_naive-run-rm_rm_PROMPT_v1/analysis/v1_design_vs_agent.png) |
| 6 | 2026-10-20 | `binwalk` (not a Caruca command) | 193 s | $2.12 | [analysis](../../naive_llm_caruca/runs/2026-10-20_133813_naive-run-binwalk_binwalk_PROMPT_v1/analysis/analysis.md) | [PDF](../../naive_llm_caruca/runs/2026-10-20_133813_naive-run-binwalk_binwalk_PROMPT_v1/analysis/analysis.pdf) | [session](../../naive_llm_caruca/runs/2026-10-20_133813_naive-run-binwalk_binwalk_PROMPT_v1/analysis/session_workflow.png) · [information flow](../../naive_llm_caruca/runs/2026-10-20_133813_naive-run-binwalk_binwalk_PROMPT_v1/analysis/information_flow.png) · [Caruca's design vs agent](../../naive_llm_caruca/runs/2026-10-20_133813_naive-run-binwalk_binwalk_PROMPT_v1/analysis/v1_design_vs_agent.png) |
| 7 | 2026-10-20 | `cut` | 104 s | $1.25 | [analysis](../../naive_llm_caruca/runs/2026-10-20_135253_naive-run-cut_cut_PROMPT_v1/analysis/analysis.md) | [PDF](../../naive_llm_caruca/runs/2026-10-20_135253_naive-run-cut_cut_PROMPT_v1/analysis/analysis.pdf) | [session](../../naive_llm_caruca/runs/2026-10-20_135253_naive-run-cut_cut_PROMPT_v1/analysis/session_workflow.png) · [information flow](../../naive_llm_caruca/runs/2026-10-20_135253_naive-run-cut_cut_PROMPT_v1/analysis/information_flow.png) · [Caruca's design vs agent](../../naive_llm_caruca/runs/2026-10-20_135253_naive-run-cut_cut_PROMPT_v1/analysis/v1_design_vs_agent.png) |
| 8 | 2026-10-20 | `convert` (ImageMagick) | 1,291 s | $6.04 | [analysis](../../naive_llm_caruca/runs/2026-10-20_135842_naive-run-convert_convert_PROMPT_v1/analysis/analysis.md) | [PDF](../../naive_llm_caruca/runs/2026-10-20_135842_naive-run-convert_convert_PROMPT_v1/analysis/analysis.pdf) | [session](../../naive_llm_caruca/runs/2026-10-20_135842_naive-run-convert_convert_PROMPT_v1/analysis/session_workflow.png) · [information flow](../../naive_llm_caruca/runs/2026-10-20_135842_naive-run-convert_convert_PROMPT_v1/analysis/information_flow.png) · [Caruca's design vs agent](../../naive_llm_caruca/runs/2026-10-20_135842_naive-run-convert_convert_PROMPT_v1/analysis/v1_design_vs_agent.png) |
| 9 | 2026-10-20 | `sort` | 304 s | $2.46 | [analysis](../../naive_llm_caruca/runs/2026-10-20_160340_naive-run-sort_sort_PROMPT_v1/analysis/analysis.md) | [PDF](../../naive_llm_caruca/runs/2026-10-20_160340_naive-run-sort_sort_PROMPT_v1/analysis/analysis.pdf) | [session](../../naive_llm_caruca/runs/2026-10-20_160340_naive-run-sort_sort_PROMPT_v1/analysis/session_workflow.png) · [information flow](../../naive_llm_caruca/runs/2026-10-20_160340_naive-run-sort_sort_PROMPT_v1/analysis/information_flow.png) · [Caruca's design vs agent](../../naive_llm_caruca/runs/2026-10-20_160340_naive-run-sort_sort_PROMPT_v1/analysis/v1_design_vs_agent.png) |
| 10 | 2026-10-26 | `dirname` (task 018 pilot) | 57 s | $0.88 | not analysed | — | — |

Runs 1 and 2 (`sed`, `grep`, 2026-10-13) used an earlier layout and their records no longer exist.

## 4. Charts and diagrams

Every diagram belongs to one of five kinds. Each run's diagrams sit in that run's `analysis/` folder,
linked in the table above, beside the `.excalidraw` source and the `.spec.json` it was built from.

| Diagram | What it shows | Where |
|---|---|---|
| The three findings | The project's three main naive-LLM findings on one page | [`ai_docs/diagrams/003_…png`](../diagrams/003_naive_llm_three_findings.png) |
| Session workflow | One run as a timeline: each phase of the agent's session, how long it took, how many tool calls | each run, `session_workflow.png` |
| Information flow | What the agent read or ran, and which of its output files each source fed | each run, `information_flow.png` |
| Caruca's design vs the agent | Caruca's five jobs as the paper designs them, beside what the agent did for each | runs 4 to 9, `v1_design_vs_agent.png` |
| Run 3 vs run 4 | The same command with and without web access | run 4, `run3_vs_run4.png` |
| v2 system architecture (dated) | The September plan for the step-by-step rebuild, not the naive approach | [`001_…png`](../diagrams/001_caruca_v2_system_architecture.png), [`002_…png`](../diagrams/002_architecture_widescreen.png) |

## 5. Tools and raw data

| What | Where |
|---|---|
| Scoring tools (task 018): binary probe, program-checked facts, real-world reading, generator use | [`naive_llm_caruca/scoring/`](../../naive_llm_caruca/scoring/) (`score_t018.py` runs everything) |
| Comparison scripts (syntax files vs v1) | [`naive_llm_caruca/comparisons/2026-10-26_syntax_files_vs_v1/scripts/`](../../naive_llm_caruca/comparisons/2026-10-26_syntax_files_vs_v1/README.md) |
| Each run's full record (prompt, transcript, the agent's output files) | `naive_llm_caruca/runs/<run>/` |
| How to run one more command through the naive approach | [`naive_llm_caruca/README.md`, "Running a command with Claude"](../../naive_llm_caruca/README.md#running-a-command-with-claude) |

## 6. Background that still holds (facts about Caruca itself)

| Document | Last changed | What it establishes |
|---|---|---|
| [E0: artifact pinning](../analysis/e0_artifact_pinning.md) | 2026-10-13 | 82.7% of Caruca's generated test lines are repeats; the paper's three divergence claims checked |
| [What Caruca is for, and the grep case](../analysis/caruca_purpose_grep_case.md) | 2026-10-13 | Caruca's purpose (Greenberg); `grep`'s three pattern forms, one held by all of Caruca's grammars |
| [PaSh VM setup](../docs/pash_vm_setup.md) · [PaSh work scheduling](../analysis/pash_work_scheduling.md) | 2026-10-13 | How PaSh reads descriptions today; its speedups and their limits |
| [Caruca v1 pipeline instructions](../docs/caruca_v1%20pipeline%20instructions.md) | 2026-09-03 | How to run Caruca itself (Lima VM) |
| [The Caruca paper, transcribed](../refs/caruca_white_paper.md) | reference | The paper the comparison is measured against |

## 7. Dated: the step-by-step rebuild (September to early October 2026)

Before the naive approach, the project rebuilt Caruca's four steps one by one with GPT-4o (the "v2
pipeline"). Its findings still stand as recorded and several are in [Latest findings](../analysis/latest_findings.md),
but it is no longer the focus, and some of its plans were overtaken. Read these only for that history.

| Document | Last changed | What it was |
|---|---|---|
| [Parity study](../analysis/v1_v2_parity_study.md) | 2026-10-13 | v2 pipeline vs Caruca, step by step, nine commands |
| [v2 fidelity to v1](../analysis/v2_fidelity_to_v1.md) | 2026-10-13 | How the rebuild matched Caruca's code |
| [Status report 2026-10-13](../analysis/status_reports/status_report_2026-10-13.md) · [2026-09-22](../analysis/status_reports/status_report_2026-09-22.md) | 2026-10-13 | Where the rebuild stood |
| [Addendum (rebuild)](../analysis/white_paper_addendum.md) | 2026-09-29 | Proposals for the paper from the rebuild; superseded in focus by the naive-LLM addendum |
| [Experiment designs](../analysis/experiment_designs.md) · [implementation plan](../analysis/experiment_implementation_plan.md) | 2026-09-29 | Planned experiments for the rebuild; most never ran |
| [Evaluation gaps](../analysis/evaluation_gaps.md) · [Scientific vs engineering contributions](../analysis/scientific_vs_engineering_contributions.md) | 2026-10-13, 2026-09-29 | Early framing of what the paper leaves unmeasured |
| [Reflections on the 2023 proposal reviews](../analysis/reflections_on_caruca_v1_submission_reviews.md) | 2026-10-13 | The NSF grant-proposal reviews (not the paper's reviews) |
| [v2 chain vs v1](../docs/v2_chain_vs_v1.md) · [v2 pipeline usage guide](../docs/caruca_v2_pipeline_usage_guide.md) · [v2 prompts inventory](../docs/caruca_v2_llm_prompts.md) · [console walkthrough](../docs/console_walkthrough_grep_rm.md) | 2026-09-13 to 2026-10-13 | Operating the rebuild |
| [Planning documents](../prep/) (master idea, roadmap, architecture, data schema, component functionality) and [the September handouts](../docs/presentations/) | 2026-09-29 | The August–September project plan |
