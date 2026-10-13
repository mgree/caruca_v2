---
name: caruca-grep-grammar-single-shape
description: grep's man page lists 3 synopsis shapes (pattern / -e / -f); all three v1 grep grammars (LLM, hand reference, PaSh subset) hold only the first, so v1 still adds a pattern word after -e (grep reads it as a file); the reference shares the gap, so scoring can't see it
metadata:
  type: project
---

Verified 2026-10-06 against v1 `d80324073`.

**The man page** (`caruca/src/caruca/doc_sources/man/grep.txt`, lines 8–10) lists three shapes:

```
grep [OPTION...] PATTERNS [FILE...]
grep [OPTION...] -e PATTERNS ... [FILE...]
grep [OPTION...] -f PATTERN_FILE ... [FILE...]
```

**The grammars:**

- `outputs/llm-dsl-generation/grep.py`, the LLM output (pattern typed `String`, 48 options).
- `caruca/src/caruca/syntax_specs/grep.py`, the hand reference used to score it (pattern typed `Regex`,
  48 options).
- `caruca/src/caruca/pash_syntax_specs/grep.py`, the 4-flag subset used for PaSh annotations.

Each has exactly one usage, `[options] [pattern EXACTLY_ONE, path ZERO_OR_MORE]`. The DSL allows several
usages per command (the paper's "set of possible grammars"), but none adds the `-e` or `-f` shape.

**State the consequence precisely.** It is not "v1 never runs `-e`". The LLM and reference grammars list
`-e` as an option but still require a positional pattern, so v1 writes lines like `grep -e a a relpath_1`,
and grep reads the second `a` as a *file name*. The `-e`/`-f` shapes are never tested as the
documentation describes them, and any tool reading the grammar takes `a.txt` in `grep -e foo a.txt` for
the pattern. The PaSh subset has no `-e` at all. The authors of PaSh's old JSON grep annotation flagged
the same hole in a comment ([[pash-grep-annotation-current-vs-json]]).

**Why:** grep is Greenberg's flagship example and syntax accuracy is v1's objective
([[project-greenberg-caruca-purpose]]). This is the clearest case of agreement-with-reference hiding an
error: the generated grammar and the reference share the gap, so v1's syntax comparison reports a match.

**How to apply:** if grep is used as a demonstration, either add the `-e`/`-f` usages or state the gap.
Before blaming a generated grammar for a disagreement, check whether the reference has the same gap.
Related: [[caruca-v1-grep-committed-annotation-stale-spec]] (a separate grep defect: the committed
annotation was built from an older grammar with no pattern argument at all).
