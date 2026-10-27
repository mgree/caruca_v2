<!-- ATTRIBUTION-NOTICE:START -- required by LICENSE-TEMPLATES.md, do not remove -->
<!-- caruca_v2 analysis document. Created by Tiran Dagan. Copyright (c) 2026 Tiran Dagan.
     Licensed under the PolyForm Noncommercial License 1.0.0
     https://polyformproject.org/licenses/noncommercial/1.0.0
     Noncommercial use only. Commercial use is prohibited. -->
<!-- ATTRIBUTION-NOTICE:END -->

# Observations: naive LLM vs Caruca

**27 October 2026.** Four commands: `cut`, `sort`, `rm` and `binwalk`. Each has one agent run, scored
the same day by [task 018](../tasks/018_naive_vs_caruca_syntax_scoring.md). Back to the
[directory](README.md).

## The three kinds of syntax file compared

A syntax file is a short Python file saying which options a command takes, what kind of value each one
needs, and which files the command works on. Caruca uses it to write the test command lines it runs, and
to read real shell scripts.

| Name here | What it is | How it was made |
|---|---|---|
| **Answer key** | Caruca's curated reference (`syntax_specs/<cmd>.py`) | Written and corrected by hand from the manual pages over many commits. The paper puts the whole set at 80 person-hours for 120 commands, about 40 minutes per command |
| **Caruca's GPT-4o** | Caruca's own model output (`outputs/llm-dsl-generation/<cmd>.py`) | One prompt to GPT-4o with the bundled manual page; the model never runs the command. Shipped with Caruca; its date, settings and cost were not recorded |
| **Agent** | The naive approach (`naive_llm_caruca/runs/…/output/<cmd>.py`) | A Claude Code session (Claude Fable 5.1) given the goal, two format descriptions and four finished examples. It reads the manual, runs the command, and decides its own method |

`binwalk` is not one of Caruca's 120 commands, so it has only the agent's file. `rm` was one of the
agent's four examples (it was shown Caruca's answer key for `rm`), so for `rm` the agent's score shows
what it changed, not what it found unaided.

## The short answer

- **Quality, checked against the real program: about level, with the agent slightly ahead.** The agent's
  file gets 89% of the checkable facts right on `cut` (answer key 85%, Caruca's GPT-4o 83%), 79% on
  `sort` (78%, 77%) and 97% on `rm` (98%, 98%). It gets 97% (326 of 337) on `binwalk`, where no
  Caruca file exists. Each command had one agent run, so these gaps are observations, not a verdict.
- **Where the agent is better:** it describes what the installed program does rather than what the
  manual says. It lists every real `sort` option spelling (53 of 53; the answer key misses `-y`, Caruca's
  GPT-4o misses five spellings of four options, including the sort-key option `-k`/`--key`). It knows that `-` means "read standard input" for
  `cut` and `sort`, which neither Caruca file says. It encodes `cut`'s rule that only one of `-b`, `-c`
  and `-f` may be given, which neither Caruca file does.
- **Where the agent is worse:** its files fit Caruca's own test-line generator badly. It writes `=` after
  short options (`cut -b=1`), a habit copied from one of Caruca's own example files, which the program
  rejects. So none of the 240 `cut` lines Caruca generates from it does real work, against 15 of 29 for
  the answer key. For `rm` it made the file optional (correct with `rm -f`), and Caruca's generator then
  writes `rm` lines with no file: 3 of 21 do real work, against 26 of 32.
- **Reading real scripts: the agent and the answer key both read 100%** of the real `cut`, `sort` and
  `rm` lines checked; Caruca's GPT-4o reads 83% of `sort` lines, because it lacks `-k`.
- **Speed and cost: the agent takes minutes and a few dollars per command.** These four took 60 to 304
  seconds and $0.80 to $2.46 at list price. The answer key averages about 40 minutes of expert time per
  command. Caruca's GPT-4o step is a single model call, but its time and cost were never recorded.

## Scores

### Headline: facts checked against the real program

Every fact is settled by running the installed program (GNU coreutils 9.4; binwalk package 2.3.4, which
reports itself as v2.3.3), never by
Caruca's answer key, and the list of facts was fixed before scoring. Read each cell as "right / checked".

| Command | File | **Right** | Real options listed | Listed options real | Takes a value or not | Sample values accepted | `=` works as written | Repeats | File operands | Rules between options |
|---|---|---|---|---|---|---|---|---|---|---|
| `cut` | Answer key | **61/72 (85%)** | 17/17 | 17/18 | 17/17 | 4/5 | 0/0 | 3/3 | 3/4 | 0/8 |
| `cut` | Caruca's GPT-4o | **63/76 (83%)** | 17/17 | 17/17 | 17/17 | 5/5 | 1/5 | 3/3 | 3/4 | 0/8 |
| `cut` | Agent | **68/76 (89%)** | 17/17 | 17/17 | 17/17 | 5/5 | 1/5 | 3/3 | 4/4 | 4/8 |
| `sort` | Answer key | **172/220 (78%)** | 52/53 | 54/54 | 54/54 | 7/11 | 1/4 | 0/0 | 3/4 | 1/40 |
| `sort` | Caruca's GPT-4o | **157/204 (77%)** | 48/53 | 49/49 | 49/49 | 6/8 | 1/1 | 0/0 | 3/4 | 1/40 |
| `sort` | Agent | **181/230 (79%)** | 53/53 | 53/53 | 52/53 | 10/12 | 6/12 | 2/2 | 4/4 | 1/41 |
| `rm` | Answer key | **59/60 (98%)** | 17/17 | 17/17 | 17/17 | 2/2 | 1/2 | 0/0 | 4/4 | 1/1 |
| `rm` | Caruca's GPT-4o | **59/60 (98%)** | 17/17 | 17/17 | 17/17 | 2/2 | 1/2 | 0/0 | 4/4 | 1/1 |
| `rm` | Agent | **58/60 (97%)** | 17/17 | 17/17 | 17/17 | 2/2 | 1/2 | 0/0 | 3/4 | 1/1 |
| `binwalk` | Agent (the only file) | **326/337 (97%)** | 102/102 | 102/102 | 102/102 | 11/21 | 0/0 | 5/5 | 3/4 | 1/1 |

What the columns check:
- **Real options listed:** every option spelling the program accepts appears in the file.
- **Listed options real:** every spelling in the file is one the program accepts.
- **Takes a value or not:** the file agrees with the program on whether each option needs a value.
- **Sample values accepted:** the example values the file gives are values the program accepts.
- **`=` works as written:** where the file says "value after `=`", the program accepts that form.
- **Repeats:** the file and the program agree on whether an option may be given twice.
- **File operands:** the file agrees with the program on whether 0, 1 or 2 files are allowed and on
  whether `-` means standard input.
- **Rules between options:** the file and the program agree on which options cannot be used together,
  and on whether a line with no options at all is valid.

The totals differ between files because a file that lists more options has more facts checked. Most of
`sort`'s missed rules (for example, `--debug` cannot be combined with `-c`) are ones Caruca's file format
can express only by splitting the file into several alternative layouts. None of the three files does
that for `sort`.

### Fit with Caruca's current programs

These two figures mix the file's quality with Caruca's own conventions. The `=` convention, for example,
costs the agent here and nowhere else.

| Command | File | Real-world lines read correctly | Generated test lines doing real work |
|---|---|---|---|
| `cut` | Answer key / Caruca's GPT-4o / Agent | 5,856 / 5,856 / 5,856 of 5,856 | 15 of 29 / 0 of 30 / 0 of 240 |
| `sort` | Answer key / Caruca's GPT-4o / Agent | 5,010 / 4,179 / 5,010 of 5,010 | 41 of 56 / 38 of 47 / 33 of 56 |
| `rm` | Answer key / Caruca's GPT-4o / Agent | 24,195 / 24,195 / 24,195 of 24,195 | 26 of 32 / 26 of 32 / 3 of 21 |
| `binwalk` | Agent | no real-world lines in Caruca's collection | too many to trace: 65,659 lines, 65,536 of them from the port option; leaving that option out, 72 of 72 distinct lines are accepted (but on Caruca's test files binwalk finds nothing to report) |

How these were counted:
- **Real-world lines:** the lines in Caruca's collection of real shell scripts that GNU itself accepts,
  read with GNU's own option rules and the option list from the file.
- **Caruca's own matcher** counts nearly every line as read whatever the file says, because it lets any
  word stand in for any option that takes a value. Its figures are in the
  [scores table](../../naive_llm_caruca/scoring/results/summary.md), not here.
- **Generated lines:** Caruca's generator at one option per line, each line traced by Caruca's own tracer.
  A line counts as doing real work when the command accepts it and it isn't `--help` or `--version`.

### Agreement with Caruca's answer key (the paper's measure)

| Command | File | Answer-key options matched | Extra options | Exact by Caruca's own check |
|---|---|---|---|---|
| `cut` | Caruca's GPT-4o / Agent | 11 of 12 / 11 of 12 | 0 / 0 | no / no |
| `sort` | Caruca's GPT-4o / Agent | 28 of 31 / 31 of 31 | 0 / 2 (`-y`, `--check`, both real) | no / no |
| `rm` | Caruca's GPT-4o / Agent | 12 of 12 / 12 of 12 | 0 / 0 | yes / no |

This is the paper's way of scoring, and it has blind spots. Caruca's own check (`eval/cmp_specs.py`)
noticed 1 of 8 deliberately planted differences. And the agent's departures count against it even where
the program shows the agent is right: the 12th `cut` option both files "miss" is `-w`, which GNU `cut`
rejects.

### Time and cost of making each file

| File | `cut` | `sort` | `rm` | `binwalk` |
|---|---|---|---|---|
| Agent: session time | 104 s | 304 s | 60 s | 193 s |
| Agent: cost at list price | $1.25 | $2.46 | $0.80 | $2.12 |
| Agent: tool calls | 17 | 23 | 5 | 18 |
| Answer key | about 40 minutes of expert time per command on average (80 person-hours for 120 commands, the paper) | | | |
| Caruca's GPT-4o | one model call per command; time and cost not recorded | | | |

## Samples side by side

The same option in each kind of file, excerpted from the files themselves. Comments starting with `←`
are ours; every other comment is in the file.

**`cut`, the byte-list option.** The answer key puts the value after a space (correct). Caruca's GPT-4o
and the agent both mark "value after `=`" (`flag_followed_by_equals=True`), which Caruca's generator
writes as `cut -b=1`, and `cut` rejects that. Only the agent splits the file into three layouts, one per
selector, so that `-b`, `-c` and `-f` can never appear together, which is `cut`'s real rule.

```python
# Answer key (syntax_specs/cut.py)
Range(flag="-b", alias=["--bytes"]),

# Caruca's GPT-4o (outputs/llm-dsl-generation/cut.py)
Range(flag="-b", alias=["--bytes"], flag_followed_by_equals=True),

# Agent (run 7)   ← one layout per selector; each selector required exactly once
# cut -b LIST ...
[[Range(flag="-b", alias=["--bytes"], flag_followed_by_equals=True, arity=Arity.EXACTLY_ONE),
  *_common_options()], _operands()],
```

**`rm`, the prompt-before-deleting option and the files.** The agent lists the 6 values `rm` itself
reports when given a wrong one; the answer key and Caruca's GPT-4o list the manual's 3. The agent makes the
file optional, which is right when `rm -f` is used and wrong otherwise.

```python
# Answer key (syntax_specs/rm.py); Caruca's GPT-4o is identical here
Selection(flag="--interactive", choices=["never", "once", "always"], flag_followed_by_equals=True),
[Path(arity=Arity.AT_LEAST_ONE)],          # ← at least one file

# Agent (run 5)
Selection(flag="--interactive", choices=["never", "no", "none", "once", "always", "yes"],
          flag_followed_by_equals=True),
[Path(arity=Arity.ZERO_OR_MORE)],          # ← zero or more files
```

**`sort`, the sort key and two edge options.** Caruca's GPT-4o has no `-k` at all, so it cannot describe
`sort -k 2,2n`. The answer key has it. The agent has it, may repeat it (as `sort` allows), but again marks
"value after `=`" on a short option. The agent also adds `-y`, a real but obsolete option, and lists it as
taking no value. That fails for a bare `sort -y`, which `sort` refuses ("option requires an argument").
But no description in Caruca's format fits `-y` exactly: `sort -y 5 f` ignores the 5, and `sort -y abc
f` reads `abc` as a file.

```python
# Answer key (syntax_specs/sort.py)
Other(flag="-k", alias=["--key"], choices=("1", "1.2", "1.2n", "1.2nr", "1n", "1nr")),

# Caruca's GPT-4o (outputs/llm-dsl-generation/sort.py): no -k / --key entry

# Agent (run 9)
String(flag="-k", alias=["--key"], flag_followed_by_equals=True, arity=Arity.ZERO_OR_MORE),  # KEYDEF
Integer(flag="--batch-size", flag_followed_by_equals=True, min=2),   # ← a minimum and no maximum: Caruca writes no value
Flag("-y"),  # obsolete, accepted and ignored
```

**`binwalk`, agent only.** The agent took binwalk's options from binwalk's own Python source. A correct
port range turns into 65,536 generated test lines in Caruca's generator. An option that runs another
program (`-D`) is typed as plain text, not as Caruca's "command" type, and the agent never mentions what
it does.

```python
# Agent (run 6)
Integer(flag="-s", alias=["--status"], min=0, max=65535),   # ← every value becomes a test line
String(flag="-D", alias=["--dd"], arity=Arity.ZERO_OR_MORE), # <type[:ext[:cmd]]>   ← runs cmd for each match
Integer(flag="-l", alias=["--length"]),                     # ← no range: Caruca tries -1, 0, 1; binwalk rejects -1
```

## How the two approaches are alike and different

| | Caruca (v1) | Naive agent |
|---|---|---|
| Input | The bundled manual page only | The manual page, `--help`, the installed program, and (for `binwalk`) its source code |
| Who decides the method | Hand-written code; the model only writes the syntax file | The agent, with no method given |
| Checks the syntax against the program? | No; told not to add anything the manual doesn't mention | Yes; runs the command dozens to thousands of times before writing |
| Accuracy is measured against | Its own hand-made answer key, written from the same manuals | (here) the installed program |
| Safety while running commands | Every test line runs in an isolated sandbox, with every file access recorded | One scratch folder; nothing recorded; dangerous options sometimes skipped silently |
| Self-check | Deterministic code; same answer every run | Its reports overstated its own testing in all six runs analysed |
| Output format | Both write the same Python format and PaSh's three files | (same) |
| What it extends | | Wrote a merge step for `sort` that the paper leaves out of Caruca's scope (it failed silently inside PaSh) |

## What these numbers do not say

- **One agent run per command.** The planned rule calls one file "better" only when it leads by more than
  the spread across three agent runs; with one run there is no spread, so no verdicts are given.
- **Option values count once per option.** The agent's six `rm --interactive` values score the same as
  the manual's three, because the headline checks that sample values are accepted, not that the list is
  complete.
- **Three faults in the scoring tool were repaired on 2026-10-27 before these numbers were kept:** it
  misread Caruca's name for "one or more"; it wrote optional values after a space, which GNU never
  accepts; and it counted a refused sample value as a rule between two options. Before the repair, all
  three `rm` files showed 56 of 60. The repairs apply to every file alike. See
  [task 018](../tasks/018_naive_vs_caruca_syntax_scoring.md).

## Where the details are

- Every count, file by file: [`scoring/results/<cmd>.json`](../../naive_llm_caruca/scoring/results/)
  and the [scores table](../../naive_llm_caruca/scoring/results/summary.md)
- Every difference between the three syntax files, checked on the program:
  [Syntax files vs v1](../analysis/naive_llm_syntax_files_vs_v1.md)
- What each run did: the run table in the [directory](README.md#3-the-runs)
- The write-up for the paper's co-authors: [Naive LLM addendum](../analysis/white_paper_addendum_naive_llm.md)
