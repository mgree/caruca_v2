# Analysis Index

Findings and evaluations produced *by this project* (as opposed to `ai_docs/refs/`, which holds
source material we didn't write — the paper, upstream docs, transcripts). Kept out of `CLAUDE.md`
itself so routine sessions don't load analysis content they don't need; link in from here instead.

| Document | What it is |
|---|---|
| [`v2_fidelity_to_v1.md`](v2_fidelity_to_v1.md) | Mechanism-by-mechanism account of how caruca_v2 works, each feature paired with the v1 mechanism it reproduces and marked IDENTICAL / DELIBERATE / DEFECT. Includes the consolidated deviation ledger and the commands to re-verify every claim. |
| [`evaluation_gaps.md`](evaluation_gaps.md) | 14 opportunities to broaden v1's / the paper's test & evaluation coverage (filesystem fixtures, content types, evaluation methodology), split into gaps the authors don't discuss vs. gaps they already flag themselves. |
| [`scientific_vs_engineering_contributions.md`](scientific_vs_engineering_contributions.md) | Which v2 directions are publishable science vs. product/engineering work, and why. Nine ranked candidate contributions (S1–S9), a table of necessary-but-uncountable work with salvage framings, and two proposed paper structures for the resubmission. Grounded in Shaw's ICSE result/validation acceptance data and the SIGPLAN empirical-evaluation checklist. |
| [`experiment_designs.md`](experiment_designs.md) | Protocol-level designs (E0-E6) for the candidates worth running, each with the infrastructure that already exists, what still needs building, an effort estimate, and the null result that would falsify it. E0 is a blocking reproducibility check on the paper's `grep`/`ps`/`cp` claims. |
| [`experiment_implementation_plan.md`](experiment_implementation_plan.md) | The E0-E6/S-candidate designs re-grounded in the implemented v2 (2026-09-06): per-experiment implementation + run plans, the evaluation-harness gap as a first-class finding (-> task 006), an adversarially-reviewed second cycle (observation-limited tracing promoted, per-stage fidelity study reframed, two new arms, demotions recorded), and the run matrix + cost estimate whose approval unblocks the result phases of tasks 001-004. |
| [`e0_artifact_pinning.md`](e0_artifact_pinning.md) | E0 results (2026-09-06): the paper's grep claim reproduces only against a pre-2021 PaSh revision (fixed 3.5 years before Caruca); the ps annotation is still wrong upstream today but ps is outside v1's shipped population; cp never had a hand-written annotation and 26 of 29 fresh cases contradict the paper's "pure" claim on main (the other 3 do not — see that document's 22 September corrections). Plus the population pin (120 vs 108) and the enumeration-redundancy sweep (82.7% duplicate invocations; --number wrong for 90/90 commands) — with the closed-form mechanism added 6 October 2026: an invocation using k of n optional positions is emitted C(n-k, max_count-k) times, so the duplicate rate is fixed by the bound alone and rises to 89% at v1's shipped --max-count 4. A cost finding in v1's favour, not a correctness one. |
| [`v1_v2_parity_study.md`](v1_v2_parity_study.md) | The v1-vs-v2 parity study (task 008, 2026-09-14): per-stage verdicts of replicates / diverges / improves on nine commands, with both sides measured by the same instrument at the same bound. Stage 1 replicates (identical flag recall); stage 2 diverges (0.878 invocation recall but 0.208 environment agreement, over the 24 cells where it is defined); stage 4 diverges and cannot process the two largest traces at all. Includes every confound, the places a disagreement pointed at v1 rather than v2, and why no figure is compared against a published one. **Confound 8, added 6 October 2026:** stage 3's 45 executions cover only 12 distinct command lines, and for six of the nine commands all five traced configurations were the same no-argument invocation, so no flag was exercised — the protocol finding stands, the recovery figures are bounded. |
| [`white_paper_addendum.md`](white_paper_addendum.md) | Proposed additions for the resubmission, written for the co-authors and following the paper's own section order. Eight proposals, two needing the authors' input: the shipped artifacts score 78/116 by Caruca's own cmp_specs against the published 116/120, and one specification defect that stands (grep --include is typed String where its siblings are Glob; a second, uniq's two-operand form, was listed in draft and has since been withdrawn inside that document). |
| [`pash_work_scheduling.md`](pash_work_scheduling.md) | How PaSh hands input to its parallel workers (fixed-size slices dealt in turn, one new process per slice), compared with OpenMP's `static` / `dynamic` / `guided` scheduling (PaSh has the first two forms of `static` only), and a 430-run sweep of worker count × slice size (5 October 2026): tuning gains 7-10% over the default, width matters far more than slice size, and the default 1 MB slice is close to the worst on this input. Recorded for later annotation design; PaSh's source is deliberately left unmodified. |
| [`caruca_purpose_grep_case.md`](caruca_purpose_grep_case.md) | **Version 2.1, 6 October 2026: what Caruca v1 is for**, answered from the paper and v1's code only, after Greenberg's correction that v1's objective is the overall syntax definition and parallelization is a side topic. A shell script is thin glue around opaque commands, and v1 generates a model of each: syntax (written by the LLM from the man page) plus behaviour (observed only by running the command). The syntax part is the ceiling, because v1 builds every test command line from it and ShellCheck checks are generated from it. The paper's evidence doesn't match that objective: 69 of 88 reference specifications come from parallelizers, the grammar is used on its own in only 6 checks, and accuracy means agreement with hand-written grammars, which on grep share the LLM's gap (1 of 3 synopsis shapes). Ends with three v1 questions for Greenberg, and keeps the verified PaSh grep-annotation facts as a side-topic section. Picture version: https://claude.ai/artifact/3KyQ3VEiFq5o6VnrPzMrvC (version 4, private). |
| [`reflections_on_caruca_v1_submission_reviews.md`](reflections_on_caruca_v1_submission_reviews.md) | **Version 1.0, 13 October 2026.** What the reviews Greenberg shared actually are: NSF's 2023 panel review of his grant proposal, not the paper's reviews. Also what they show of the vision behind Caruca (one model per command, in a "how it is called" half and a "what it does" half, used by many tools), and seven simple recommendations for a working v2 that downstream tools use, PaSh first. **Not a response to the reviewers**, by Tiran's direction. Includes four v1 facts checked in the source: v1 merges per-setup labels by keeping the most parallel-friendly one; failed runs never count; sed's test script is split into single characters; the paper's downstream results came from curated grammars, not the LLM's. The work is task 013. |
| [`status_reports/status_report_2026-09-22.md`](status_reports/status_report_2026-09-22.md) | Advisor status report for the 22 September 2026 meeting with Profs. Eiers and Greenberg: where the project stands, the parity-study findings in plain language, problems and solutions (Lima VM, schema repairs, self-corrections), what the work adds to the paper, proposed in-scope changes vs. follow-up study ideas, open questions, and what is left. PDF at `../docs/presentations/2026-09-22_status_report_v1.1.pdf` (the v1.0 PDF is in that folder's `archive/`). |
| [`status_reports/status_report_2026-10-13.md`](status_reports/status_report_2026-10-13.md) | Coordinator's report to Tiran across every Caruca session, 13 October 2026: per-step verdict on whether v2 reproduces v1 (step 1 yes; 2 half; 3 no; 4 diverges and capped), with the single cause and the kind of fix for each; repeatability measured and not yet achieved; the console verified to run v1 faithfully (trace of `cat` identical to the parity study's, v1's files untouched) but unable to start v1's step 4, with no metering forwarder in the code and phase 6 unstarted; the four sessions and their uncommitted work; eight decisions for Tiran; and the ordered close-out (console → free repairs → decisions → paid reruns → first chained run → downstream consumers). Written after Tiran's direction that PaSh is a consumer, not the objective, and that v1's source is never modified. |

See also [`../docs/v2_chain_vs_v1.md`](../docs/v2_chain_vs_v1.md): one command followed
through both pipelines stage by stage — what each step reads, what it writes, where the file
lives and what is inside it. The concrete counterpart to the parity study's scores.

**Corrections of 22 September 2026.** Six documents carry a dated corrections note from an audit run
that day: `v1_v2_parity_study` (stage-4 figures recomputed; four statements corrected),
`white_paper_addendum` (section 5 re-framed), `v2_fidelity_to_v1` (how the paper measured PaSh;
the split-mode note), `e0_artifact_pinning` (two reasoning defects, verdicts unchanged),
`status_report_2026-09-22` (version 1.1), and `experiment_implementation_plan`. The recurring error:
the paper's PaSh quality figure was described as an execution test when it is a hand comparison, and
v1's cautious parallelizability classes were blamed on the flag bound rather than the trace mode.

Add new analysis docs here as they're produced, with a one-line description — don't inline their
content in `CLAUDE.md`.

## findings/

**Archived 13 October 2026.** At Tiran's direction the twelve finding files, every run under
`eval/runs/` and `eval/v1_runs/`, the metrics database, the campaign ledgers and the parity
drill-downs were moved — not deleted — to `eval/_archive/2026-10-13_parity/` (its README lists
each). The folder below is empty until task 014's runs produce new findings; the archived ones
remain citable and the console can read them with `CARUCA_EVAL_ROOT` pointed at the archive.

Since 22 September 2026, each conclusion this project reaches also lives as its own file in
[`findings/`](findings/) — one claim per file, with the numbers behind it, what each is counted
over, the campaign or runs it came from, and any correction it has been through.

The point is that they can be re-checked. The execution console recomputes each number with
today's scorer and reports whether it still holds, which the prose documents above cannot do.
Eleven were backfilled from `v1_v2_parity_study.md`, `e0_artifact_pinning.md` and
`memory/caruca_v1_stage1_baseline.md`; the documents remain the place the reasoning is written
out at length.
