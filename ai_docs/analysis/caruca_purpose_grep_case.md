# What Caruca v1 Is For: Syntax, Behaviour, and the grep Case

> **Version 2.1, 6 October 2026.** Version 1.0, written earlier the same day, made
> parallelization (whether a command's input can be split) the centre of "what Caruca knows beyond the
> man page", and it mixed in v2 material. Tiran corrected both points while relaying Greenberg's view.
> First, v1's objective is **the overall syntax definition of a command**, and parallelization is a
> side topic. Second, the question is about **v1 only**. This version answers that question from the
> paper and v1's code alone. The verified facts about PaSh's grep annotation from version 1.0 are kept
> in a short section near the end, labelled as the side topic. The picture version is the explainer
> page https://claude.ai/artifact/3KyQ3VEiFq5o6VnrPzMrvC (version 4). It is private until shared.
> Version 2.1 adds two points: the coverage study's use of the grammars, and that dangerous-delete checks
> also depend on behaviour.

Every claim was checked on 6 October 2026 against the paper (`ai_docs/refs/caruca_white_paper.md`),
v1 at `binpash/caruca` commit `d80324073`, and `pash-annotations` 0.2.4. Sources are listed at the end.

## The question

Tiran first treated v1's job as producing annotations for a parallelizing shell tool (PaSh), and
judged v1 by how well PaSh could use them. Greenberg disagrees. In his view v1's objective is the
overall syntax definition of a command, and he keeps returning to grep as the example. That raised the
question this document answers: if the point is not parallelization, why does v1's understanding of a
command's syntax and behaviour matter, and what does it give beyond the man page plus some hand-written
notes?

## Short answer

1. **A shell script is thin glue around opaque commands.** In the paper's htmx example (`rm`, `cp`,
   `uglifyjs`, `gzip`), the shell itself only sets the order, expands `*` and handles `>`. Everything
   the script does happens inside commands that can be written in any language and come without
   source. Any tool that reasons about a script therefore needs a model of each command.
2. **v1 generates that model, in two parts.** The **syntax** part says what each word on the command
   line is (flag, option and its argument type, positional argument with type and count). The
   **behaviour** part says what the command does with those words: files read, written or deleted,
   filesystem conditions before and after, exit status, and properties derived from those. Together
   they are what Greenberg calls the "overall definition". Parallelizability is one derived property
   among several.
3. **The two parts come from different sources, by design.** The LLM reads only the documentation and
   writes only the syntax part. Every behaviour fact comes from running the command and recording its
   system calls. The paper says so directly.
4. **The syntax part is the ceiling on everything v1 can say.** v1 builds every command line it tests
   from that grammar (8,749,056 configurations for `rm` alone). A shape the grammar lacks is never
   tested as the documentation describes it. Tools also read the grammar directly: v1 generates
   ShellCheck argument checks from it.
5. **The paper's evidence doesn't match "the syntax definition is the objective".** This is why the
   question felt unclear. The evaluation leans on the parallelizers (69 of 88 reference
   specifications). The grammar is used on its own only in 6 ShellCheck checks. Grammar accuracy is
   measured only as agreement with hand-written grammars, and on grep those share the LLM's gap.

## Why tools need a model of each command

Program analysis already has this problem, and already solves it by hand.

| Tool | What it can't see into | What it relies on |
|---|---|---|
| KLEE (symbolic execution; reference 5 in the paper) | The operating system | Hand-written models of the POSIX environment |
| Taint analysers, such as FlowDroid | Framework and library methods | Hand-written lists of sources, sinks and method summaries |
| Shell tools: PaSh, POSH, ShellCheck, Shseer | Every command in a script | Hand-written annotations; v1 generates them |

The paper's introduction makes the same point. *"So far, the solution to this has been handwritten
annotations — partial specifications that are painstakingly written by the system authors to capture
important aspects of command behavior."* The earlier systems proposed crowd-sourcing them, and that
*"has not materialized."* For a shell script, the commands are the library.

## What v1 produces, and where each part comes from

```
man page ──LLM (GPT-4o)──▶ syntax spec ──▶ command lines × filesystem setups ──▶ run, trace system calls ──▶ behaviour spec ──▶ adapters ──▶ PaSh · POSH · ShellCheck · Shseer
          └─ the LLM's only job ─┘         └──────────────────── no LLM from here on ────────────────────┘
```

The design rule, in the paper's words: *"The LLM solely generates the syntax specification — it is not
involved in any remaining components that observe command execution and derive command
specifications."*

## Why the syntax spec matters so much in v1

**Job 1: it is the grammar v1 builds its test command lines from.** Command-line arguments are untyped
strings, and each command parses them its own way, so random strings almost never produce a valid run.
This is the paper's first challenge. The syntax spec tells v1 which command lines are valid. It is
combined with filesystem setups into configurations, 8,749,056 of them for `rm`. The consequence: what
the grammar leaves out, v1 never tests as documented. grep's man page lists three shapes in its first
three lines:

```
grep [OPTION...] PATTERNS [FILE...]
grep [OPTION...] -e PATTERNS ... [FILE...]
grep [OPTION...] -f PATTERN_FILE ... [FILE...]
```

All three of v1's grep grammars hold only the first:

- `outputs/llm-dsl-generation/grep.py`, the LLM's output
- `caruca/src/caruca/syntax_specs/grep.py`, the hand-made reference it is scored against
- `caruca/src/caruca/pash_syntax_specs/grep.py`, the subset used for PaSh annotations

The LLM grammar lists `-e` as an option but still requires a pattern word after the options, so v1
writes command lines like `grep -e a a relpath_1`. grep reads the second `a` as a file name, not a
pattern. The reference has the same gap, so comparing the two reports a match.

v1's coverage study also uses the grammars as a parser. `caruca oracle` reads 666,468 real command lines
from GitHub scripts against them to see which ones v1 tested (the paper's Comprehensiveness section).

**Job 2: tools read it directly.** The paper's bug-finding section says ShellCheck's "incorrect usage"
checks can be captured by the syntax spec. v1's adapter generates them. A missing-destination check is
derived for any command whose grammar requires at least two positional paths, and Path-typed options
such as `cp -t DIR` exempt the command. A dangerous-delete check is derived from which arguments
behaviour tracing shows get deleted, so it combines the grammar with behaviour. The paper reports new checks found this way: commands needing
two arguments (`chcon`, `comm`, `diff`) and a "catastrophic remove" check for `rmdir`.

## What the behaviour spec adds beyond the man page

The paper's own example. The man page describes each flag. v1 records every combination against every
kind of path.

| Command line | `p` is a file | `p` is a folder | `p` doesn't exist |
|---|---|---|---|
| `rm p` | deleted, exit 0 | unchanged, exit 1 | exit 1 |
| `rm -r p` | deleted, exit 0 | deleted with contents, exit 0 | exit 1 |
| `rm -f p` | deleted, exit 0 | unchanged, exit 1 | exit 0 |
| `rm -rf p` | deleted, exit 0 | deleted with contents, exit 0 | exit 0 |

Shseer reasons about a script's effect on the filesystem using exactly these before-and-after
conditions, to find scripts that *"might accidentally delete a system directory"*.

## Who reads v1's output

The paper names two families: tools that speed scripts up (PaSh, POSH) and tools that find bugs
(ShellCheck, Shseer). The properties v1 derives (paper section 6) map onto them as follows.

| Property v1 derives | PaSh | POSH | ShellCheck | Shseer |
|---|:-:|:-:|:-:|:-:|
| Argument syntax and types | | | ● | |
| Which arguments get deleted | | | ● | |
| Filesystem before/after conditions, exit status | | | | ● |
| Inputs and outputs | ● | | | |
| Can the input be split (parallelizability class) | ● | ● | | |
| Can the arguments be split | | ● | | |
| Output smaller than input | | ● | | |
| Depends on the current directory | | ● | | |

Five of the eight properties serve the speed-up family. The paper doesn't name other families, but
they could use the same output: other script checkers, portability checks (GNU, BSD, busybox), tab
completion and "explain this command" tools, sandbox and permission rules, checking a command before
it runs, and translating scripts to another language.

## Where the v1 paper is thin

- **The evaluation leans on the side topic.** 69 of the 88 reference specifications come from PaSh (52)
  and POSH (17).
- **The grammar on its own is barely shown in use.** Outside v1's own test generation and coverage
  study, it appears only in 6 ShellCheck checks.
- **Grammar accuracy means agreement with people.** The paper reports 116 of 120. v1's own comparison
  tool gives 78 of 116 on the shipped files (`memory/caruca_v1_stage1_baseline.md`). Both compare
  against hand-written grammars, and on grep the reference shares the LLM's gap (1 of 3 shapes).
- **The cross-platform motivation is untested, though v1 has the material.** The introduction cites
  differences between Linux, macOS and BSD. v1 already holds 87 BSD man pages and a 240-command busybox
  reference set from 2024 (`memory/caruca_v1_cross_platform_assets.md`), and the paper uses neither.

## Questions for Greenberg (all about v1's intent)

1. **Which family of tools was v1 built to serve?** If parallelization is a side topic, which consumer
   best shows what v1 is for: bug finders like Shseer, checkers like ShellCheck, or a family the paper
   doesn't name? The evaluation's weighting (69 of 88) points the other way.
2. **Does "the overall syntax definition" mean the grammar alone, or the grammar plus observed
   behaviour?** v1 produces both. The LLM writes only the grammar.
3. **What makes v1's grammar accurate?** Matching the hand-written reference, or covering every shape
   the documentation lists? On grep the two give different answers.

## Side topic: PaSh's hand-written grep annotation

These facts were verified while answering version 1.0's parallelization framing. They stay correct and
are recorded so they are not re-derived or misquoted.

- **Old JSON annotation** (PaSh's format until 2022-09-08; v1's copy is
  `benchmarks/annotations/pash/grep.json`, last changed upstream by PaSh pull request 192 on
  2021-04-06, which added the `-c` rule). It has 4 rules for about 50 options. Author comments admit
  three holes: the pattern given with `-e`/`-f`, the pattern counted as an input file, and the need for
  `-h` when splitting across files. As written, its catch-all marks `grep -n` and `grep -m` as
  splittable.
- **Current annotation** (the class `ParallelizabilityInfoGeneratorGrep` in `pash-annotations` 0.2.4)
  handles `-q`, `-A/-B/-C`, `-m`, `-c`, `-l/-L`, `-n` and `-b` correctly. It records how pieces would be
  recombined (sum counts, merge names, shift line numbers), marked not implemented, so PaSh leaves
  those invocations unsplit. That is more than v1 can state, since the paper puts building those
  recombining steps outside its scope.
- Of the nine commands in task 012's PaSh study, current PaSh has a hand-written splitting annotation
  only for `uniq`.
- v1's only fresh grep annotation (experiment E0) labels all 44 cases "pure but not splittable",
  because it used the default input mode, which never splits input. Producing a matching split-mode
  run needs 5,504 traced executions. See `memory/caruca_v1_grep_committed_annotation_stale_spec.md`.

## Sources

| Claim | Where it was checked |
|---|---|
| htmx script; handwritten annotations; crowd-sourcing "has not materialized" | The paper, Introduction and Overview (Fig. 2) |
| The LLM writes only the syntax spec; 8,749,056 configurations for `rm`; the `rm` behaviours | The paper, Overview (challenges, system overview) |
| Properties and which tool uses each; Shseer's conditions | The paper, section 6 |
| 88 reference specifications by tool; 6 ShellCheck checks; new checks for `chcon`, `comm`, `diff`, `rmdir`; 116 of 120 | The paper, Evaluation |
| Missing-destination and dangerous-delete check derivation | v1 `caruca/src/caruca/annotator/__init__.py`, `annotator/shellcheck.py` |
| grep's three synopsis shapes; three grammars with one shape | v1 `caruca/src/caruca/doc_sources/man/grep.txt` lines 8–10; the three grammar files above |
| 78 of 116 | `memory/caruca_v1_stage1_baseline.md` |
| BSD and busybox material | v1 `benchmarks/bsd/man/`, `benchmarks/busybox/` |
| PaSh grep annotation history and current class | v1 `benchmarks/annotations/pash/grep.json`; [`e0_artifact_pinning.md`](e0_artifact_pinning.md) Claim 1; `pash-annotations` 0.2.4 |
| Only `uniq` of nine | [`../docs/pash_vm_setup.md`](../docs/pash_vm_setup.md) |
| KLEE and FlowDroid models | Public, widely documented |
