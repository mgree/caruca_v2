# PaSh test scripts

Scripts written on 5 October 2026 while standing up PaSh for task 012 (the PaSh downstream
study) and investigating how PaSh divides work among its workers. They run inside the Lima VM
`pash`, not on the Mac. The VM mounts the Mac's files read-only, so these tracked copies are the
originals. Push a changed script into the VM with:

```sh
limactl copy scripts/pash/pash-workers.sh pash:/home/tirandagan.guest/pash-workers.sh
```

Don't overwrite a script in the VM while it is running: bash reads scripts as it goes, so a
script replaced mid-run can fail in odd ways.

Every script builds its input from copies of `/usr/share/dict/words` (one copy is 663,473 lines,
6.9 MB) in a throwaway directory on the VM's own disk, and deletes the directory afterwards.

| Script | What it does | Results it produced |
|---|---|---|
| `try-pash.sh [reps] [copies]` | Times a CPU-heavy `grep` under `bash` and under PaSh at 1, 2, 4 and 8 workers. One worker isolates PaSh's fixed cost from the gain parallelism buys. | Speedup table in `ai_docs/docs/pash_vm_setup.md` §5 (4.47x at 8 workers) |
| `pash-workers.sh [width] [copies] [batch-bytes]` | One run of the same `grep`, drawn as a timeline of when each worker ran, plus the answer check and whether PaSh parallelized. Has `--help`. | The worker charts in the 5 October email to Profs. Greenberg and Eiers |
| `pash-sweep.sh [reps] [copies] [widths] [batches]` | Times every combination of worker count and slice size, shuffled, as CSV. Has `--help`. | `eval/pash_scheduling/2026-10-05_width_batch_sweep.csv`; tables in `ai_docs/analysis/pash_work_scheduling.md` |

All three use the same pipeline, with the pattern in single quotes (see `repro/` for why):

```sh
cat in.txt | grep '\(.\).*\1\(.\).*\2\(.\).*\3\(.\).*\4' | wc -l
```

The `grep` annotation PaSh uses in all of them is PaSh's own, from the unmodified
`pash-annotations` 0.2.4 package. None of these results measures a Caruca annotation.

## repro/

One-line pipelines that each show one PaSh behaviour found during setup, and a runner that
executes a pipeline under `bash` and PaSh and reports both answers, whether they match, and
whether PaSh parallelized:

```sh
~/repro/run-repro.sh ~/repro/double_quoted_grep_wrong_answer.sh 8 2
```

Re-run on 5 October 2026 at width 8 with 2 copies:

| Pipeline | Shows | Re-run result |
|---|---|---|
| `double_quoted_grep_wrong_answer.sh` | PaSh returns a **wrong answer** when it parallelizes a `grep` whose back-reference pattern is in double quotes with single backslashes. Each worker's `grep` fails with "Invalid back reference". A PaSh bug, unrelated to annotations. | bash 928, PaSh **0**, parallelized |
| `single_quoted_grep_control.sh` | The same pattern in single quotes: the control for the line above. | 928 under both, parallelized |
| `redirect_cat_falls_back.sh` | A pipeline ending in `> out.txt` is not parallelized at all. | same output, not parallelized |
| `redirect_pipeline_falls_back.sh` | The same for a longer `tr \| sort \| uniq -c` pipeline. | same output, not parallelized |
| `head5_pipeline.sh` | Recorded earlier as crashing PaSh's compiler (`AssertionError` at `compilation.py:93`). | **Did not reproduce**: no error, same output, not parallelized. The conditions of the original crash weren't recorded. |
