---
name: pash-grep-annotation-current-vs-json
description: PaSh's CURRENT grep annotation (pash-annotations 0.2.4 Python class) is careful — handles -n/-m/-c/-l/-L/-b/-A/-B/-C/-q and records how to recombine; only the OLD JSON copy in v1's benchmarks/ has the catch-all "stateless" rule. Don't cite the JSON as "PaSh's grep annotation"
metadata:
  type: project
---

Verified 2026-10-06 by reading the code: the cached wheel at
`~/.cache/uv/archive-v0/*/pash_annotations/annotation_generation/annotation_generators/ParallelizabilityInfoGeneratorGrep.py`,
version 0.2.4, the same version installed in the `pash` Lima VM.

- **Current class:** never splits `-q`. Does not split within a file for `-A/-B/-C/-m`. For `-c` it
  records a sum aggregator; for `-l/-L`, a merge; for `-n/-b`, a line-number or byte-offset mapper. All
  of those are marked `is_implemented=False`, so PaSh leaves the invocation unsplit. Only plain grep, and
  options that don't affect splitting, get parallelized. It says *more* than Caruca can (how to
  recombine), and the paper puts aggregator synthesis out of scope.
- **Old JSON** (PaSh format until 2022-09-08; v1's copy is `benchmarks/annotations/pash/grep.json`,
  last changed upstream by PR #192 on 2021-04-06): 4 rules, with author comments admitting the
  `-e`/`-f` hole, the pattern counted as an input file, and the need for `-h` when splitting across
  files. Its `len_args_eq 1` rule and its catch-all both say `stateless`. v1's `to_pash` confirms that
  `len_args_eq` counts non-option words only, so as written the JSON marks `grep -n foo` and
  `grep -m 1 foo` splittable. Whether any PaSh release actually split those was not checked.

**Why:** in the 2026-10-06 answer to Tiran, Claude first cited the JSON's catch-all as "PaSh's own grep
annotation" marking `-n`/`-m` safe, then found the current class and corrected it. The accurate version:
for grep, expert hand-writing is the standard to meet, not a weak baseline. The case for Caruca is
scale, since of task 012's nine commands only `uniq` has a splitting annotation, and checking a
hand-written annotation against the binary.

**How to apply:** always say which generation is meant. "PaSh's grep annotation" with no qualifier
means the current Python class. Related: [[project-greenberg-caruca-purpose]],
[[project-pash-downstream-study]], [[caruca-grep-grammar-single-shape]].
