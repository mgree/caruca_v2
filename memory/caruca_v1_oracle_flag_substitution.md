---
name: caruca-v1-oracle-flag-substitution
description: v1's coverage matcher (caruca.oracle) accepts any word as the flag of any value-taking option, so a syntax file missing an option still "reads" lines using it; established 2026-10-26 by code read + runs
metadata:
  type: project
---

**Fact (read in v1 `caruca/src/caruca/ir/syntax.py`, `ValueArgument.__flag_match`, lines 187–212, commit
`d80324073`; confirmed by running `caruca.oracle.oracle` on the Mac, 2026-10-26).** When the word does not
equal the option's flag, one of its aliases, or start with the flag, the final `else` appends
`StringAgnosticism(word, flag)` and returns True. So any word can be consumed as any value-taking option,
and options are tried in list order (greedy).

Observed with v1's own reference files: `cut -c1-3 --bogus a` is read in full (`-c1-3` matched to `-b`,
`--bogus` to `-c`); `sort -k 2,2n file.txt` records `-k` as StringAgnosticism, not Exact. With the shipped
GPT-4o `sort` file (no `-k`), the matcher still reads 5,011/5,011 real `sort` lines, substituting in 2,343;
with v1's `cut` reference, 5,812 of the 5,890 lines read involve a substitution. Flag-level substitutions
are told apart from value-level ones by `matched_with`: a flag string vs the printed choices tuple
(starts with "(").

**Consequence.** The paper's coverage measure (section 7.3, 97.78% with normalisation) cannot detect a
missing option. Task 018 (`ai_docs/tasks/018_naive_vs_caruca_syntax_scoring.md`) reports it beside a
strict GNU-getopt reader of its own (`naive_llm_caruca/scoring/score_t018.py`, `strict_reach`).

**Not established:** how much of the paper's 97.78% rests on substitutions (a corpus run over all 120
references would answer it); whether the `else` branch is intended normalisation or a bug — ask before
calling it either in anything stakeholder-facing ([[feedback-v1-v2-framing]]).
