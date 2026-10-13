# How PaSh Hands Out Work, and What Tuning It Buys

**Run 5 October 2026** in the Lima VM `pash` (8 virtual CPUs on an Apple M5 Pro, PaSh `42a8b87`).
This note records what was learned while watching PaSh's parallel workers. It came out of
task 012 (the PaSh downstream study) but is not part of that study's measurements. It also keeps,
for later, a comparison with OpenMP's scheduling options, which Tiran wants to use when designing
Caruca's annotations for parallelism. That design question is **not** answered here.

**Decision recorded the same day:** PaSh's source code is not modified. Everything below uses
PaSh as shipped. The only things varied are two settings PaSh already accepts on its command line:
the number of workers (`-w`, called the *width*) and the size of each slice of input a worker
receives (`--r_split_batch_size`, called the *batch size*).

## 1. The workload

One CPU-heavy pipeline, chosen so that the parallel part dominates:

```
cat in.txt | grep '\(.\).*\1\(.\).*\2\(.\).*\3\(.\).*\4' | wc -l
```

The input is the system word list repeated: 2 copies is 1,326,946 lines (13.8 MB), and 4 copies is
twice that. Every run's answer was compared with plain `bash`'s (928 for 2 copies). **All 430
timed runs gave the right answer.** The pattern is in single quotes on purpose: PaSh returns a
wrong answer when it parallelizes a double-quoted pattern (`ai_docs/docs/pash_vm_setup.md` §5).

## 2. How PaSh divides the input

Read from PaSh's source (`runtime/r_split.c`, `runtime/r_wrap.c`) and confirmed by a wrapper
that recorded every `grep` process and its parent:

1. A splitter program, `r_split`, reads the input and cuts it into slices of a fixed size
   (the batch size; default 1,000,000 bytes).
2. It deals the slices out in turn: slice 1 to worker 1, slice 2 to worker 2, …, slice 9 back to
   worker 1. Who gets which slice is fixed by position, not by who is free.
3. Each worker is a small program, `r_wrap`, that starts **a new `grep` process for every
   slice** it receives, waits for it to finish, and only then accepts its next slice.
4. A merge program, `r_merge`, puts the outputs back together. It is not a `grep` and never
   appears in the worker timings.

So the number of `grep` processes equals the number of slices, not the number of workers. With
the default settings, 13.8 MB in 1 MB slices gave 13 processes on 8 workers: a first wave of 8,
then a second wave of 5 that starts as each of workers 1–5 finishes its first slice. Workers 6, 7
and 8 sit idle for the second half. That idle tail is why the chart from
`scripts/pash/pash-workers.sh` reported 80% of the possible 8-way overlap rather than ~100%.

Step 3 has a side effect: because a hand-off waits for the receiving worker, one slow worker holds
up slices meant for workers that are already idle. In the default run, slice 12 started late
because the splitter was still waiting to hand slice 11 to worker 3, even though worker 4 had
finished.

## 3. Compared with OpenMP's scheduling options

OpenMP, a standard for parallel loops in C and Fortran, lets the programmer choose how loop
iterations are divided among threads with `schedule(...)`:

| OpenMP option | What it does | PaSh |
|---|---|---|
| `static` | one roughly equal piece per thread, decided before running | **Available, but not chosen by the user.** PaSh has a second splitter that cuts the input into W consecutive equal pieces (`runtime/auto-split.sh`), and picks it per command from that command's annotation. The same effect is obtained from `r_split` by setting the batch size to at least input size ÷ width. |
| `static, chunk` | fixed-size pieces dealt to threads in turn | **Available and tunable**: this is exactly `r_split` with `--r_split_batch_size`. |
| `dynamic, chunk` | a thread asks for the next piece when it finishes one | **Not available.** Section 2, steps 2–3: hand-out is by position, and a busy worker blocks hand-out to idle ones. |
| `guided, chunk` | like dynamic, but pieces start large and shrink as work runs out | **Not available.** It would also need the splitter to know how much input remains, which it cannot when reading a pipe. |

Adding `dynamic` would be a moderate change to `r_split` (send each slice to whichever worker can
take it). It was not done, by the decision above. One unchecked risk if it ever is: whether
`r_merge` restores output order by each slice's number or by reading workers in turn. If the
latter, out-of-turn hand-out would scramble the order of the output.

A difference that matters for any future comparison: in OpenMP, starting the next piece costs
almost nothing because the same thread carries on. In PaSh, every slice costs a new process
(`bash` plus `grep`). Very small slices therefore carry a real price that OpenMP's do not.

## 4. Measurements: width × batch size

`scripts/pash/pash-sweep.sh`, 5 timed repetitions per setting after one discarded warm-up pass,
all settings shuffled together in each repetition so that slow drift in the machine affects all of
them alike. The `caruca` VM was running but idle (load 0.00) throughout. Raw data:
`eval/pash_scheduling/2026-10-05_width_batch_sweep.csv`.

"Speedup" is `bash`'s median time ÷ PaSh's median time over the 5 repetitions. The "one slice per
worker" column is the batch size equal to input size ÷ width (OpenMP's plain `static`).

**2 copies (13.8 MB). `bash` median 2.441 s.**

| workers | 125 KB | 250 KB | 500 KB | 1 MB (default) | one slice per worker | 4 MB |
|---|---|---|---|---|---|---|
| 4 | 3.10x | 3.05x | 3.18x | 2.82x | 3.04x | 3.04x |
| 6 | 3.97x | 3.92x | 3.99x | 3.33x | 3.93x | 3.93x |
| 7 | 4.35x | 4.32x | 4.38x | 4.27x | 4.35x | 4.31x |
| **8** | 4.64x | **4.73x** | 4.39x | 4.29x | 4.56x | 4.61x |
| 10 | 4.43x | 4.49x | 4.47x | 3.85x | 4.28x | 4.19x |
| 12 | 4.44x | 4.43x | 4.14x | 3.59x | 4.47x | 4.43x |
| 16 | 4.41x | 4.42x | 4.27x | 4.42x | 4.47x (865 KB) | 4.44x |

**4 copies (27.7 MB). `bash` median 4.842 s.**

| workers | 125 KB | 250 KB | 500 KB | 1 MB (default) | one slice per worker | 4 MB |
|---|---|---|---|---|---|---|
| 4 | 3.26x | 3.29x | 3.33x | 3.37x | 3.43x | 3.06x |
| 6 | 4.42x | 4.44x | 4.33x | 4.15x | 4.27x | 3.09x |
| 7 | 4.90x | 4.89x | 4.81x | 4.73x | 4.76x | 4.88x |
| **8** | 5.29x | **5.37x** | 5.36x | 4.99x | 5.29x | 5.29x |
| 10 | 5.07x | 5.21x | 5.26x | 5.05x | 4.81x | 4.89x |
| 12 | 5.13x | 5.33x | 5.16x | 4.79x | 5.07x | 5.11x |
| 16 | 5.24x | 5.19x | 5.05x | 4.99x | 5.13x | 5.07x |

### What the numbers say

- **Tuning gains about 7–10%, no more.** The best setting in both cases is 8 workers with 250 KB
  slices: 4.73x against the default's 4.29x on 2 copies (0.516 s against 0.569 s; the five-run
  ranges, 0.508–0.522 s and 0.560–0.577 s, do not overlap), and 5.37x against 4.99x on 4 copies
  (0.902 s against 0.971 s).
- **The default 1 MB is close to the worst slice size here.** It is the lowest or near-lowest
  value in most rows. The reason is section 2's ragged second wave: 13.8 MB in 1 MB slices does
  not divide evenly among 8 workers. Settings that divide evenly — many small slices (the
  leftover at the end is small) or exactly one slice per worker — avoid it. The 4 MB column at 6
  workers with 4 copies (3.09x) is the same effect: 7 slices on 6 workers, so one worker does a
  second, full-length slice alone.
- **Width should match the CPUs available, and the VM has 8.** Fewer workers leave CPUs unused
  (4 workers: about 3.1–3.4x). More workers than CPUs do not help (10, 12 and 16 are all at or
  below 8). The best width is a property of the machine, not of the command.
- **Most of the remaining gap is fixed cost, not scheduling.** PaSh spends ~0.14 s outside the
  workers on every run (startup, compiling the script, merging). With perfect 8-way division, the
  2-copy run could at best take 2.441 ÷ 8 + 0.14 ≈ 0.445 s, a 5.5x speedup; the best measured is
  0.516 s. Larger inputs move the speedup up (4.7x → 5.4x from 2 to 4 copies) because the fixed
  cost is spread over more work.

## 5. What this means for later (recorded, not pursued)

- A parallelizability class says *whether* a command may be split. Sections 2–4 show that *how*
  it is split — how many workers, and slice size relative to input size — moves performance by a
  measurable but modest amount on this workload (7–10%), while the choice of width moves it a lot
  (3.1x at 4 workers against 4.7x at 8).
- The settings that mattered here depend on the machine (CPU count) and on the input size, not on
  anything a per-command annotation records today. Whether an annotation could usefully carry
  "how much work per byte" or "minimum worthwhile slice" information is the open design question
  Tiran wants to return to, with OpenMP's options as the reference point.
- Only one command (`grep`) with one fairly uniform workload was measured. Every line of input
  costs about the same here. Workloads whose cost varies a lot from line to line are where
  `dynamic` scheduling pays off in OpenMP, and are the case this sweep cannot speak to.

## 6. Tools

- `scripts/pash/pash-workers.sh [width] [copies] [batch-bytes]` draws one run's workers as a
  timeline (`--help` describes the arguments).
- `scripts/pash/pash-sweep.sh [reps] [copies] [widths] [batches]` produces the grid above as CSV.

Both live in the repo and are copied into the VM's home directory with `limactl copy`, because
the VM mounts the Mac's files read-only.
