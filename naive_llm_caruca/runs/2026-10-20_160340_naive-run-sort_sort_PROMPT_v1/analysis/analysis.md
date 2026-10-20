# Analysis of one run: `sort`, prompt version 1, 2026-10-20 16:03 (run 9)

**Run folder:** `naive_llm_caruca/runs/2026-10-20_160340_naive-run-sort_sort_PROMPT_v1/`
**Written:** 2026-10-20, from `stream.jsonl`, `stream.actions.log`, the session transcript, `run.env`,
`environment.txt` and the four output files. Call numbers below are the tool-call numbers printed in
`stream.actions.log` (1 to 23); times are local (UTC−4). Same setup as runs 4 to 8 (prompt, model,
effort, golden image, which has carried the `binwalk` package since run 6); run 7 (`cut`, analysed beside
this one) started 2 hours 11 minutes earlier. Runs 6 and 8 (`binwalk`, `convert`) were made and analysed
in another session and are not compared here. **`sort` is not one
of the four samples.** Checks marked "measured here" were run during this analysis, not by the session:
v1's real syntax module and generator on the Mac, and GNU coreutils 9.4 and PaSh's real annotation
code (`pash_annotations` 0.2.4) in the `pash` virtual machine.

## Summary

A fresh Claude Code session (version 2.1.296, model `claude-fable-5-1` at medium effort, permissions
bypassed, web tools and MCP servers removed) in a throwaway Ubuntu 24.04 virtual machine was given
prompt version 1 for `sort`. In 304 seconds, 24 turns and 23 tool calls (12 shell, 11 file reads) it
produced all four files at a list-price cost of $2.46, with no network use. This is the most thorough
of runs 4, 5, 7 and 9. It ran `sort` 88 times before writing anything. After writing, it built two test
scripts that ran `sort` about 960 more times: every option spelling in its syntax file, then 20 option
sets each split into 2, 3 and 5 parts, sorted part by part, merged with the command its class
generates, and compared with one sort of the whole. All of that passed. Its parser table matches PaSh's
own `sort` table, argument types included, plus two extra entries (`-y` and `--check`). The session
never saw PaSh's table. **But its parallelizability class does not work inside PaSh.** The class
offers "deal lines out in turn (round robin), then merge with `sort -m`". PaSh's code permits round
robin only when the parts are simply concatenated or joined at their edges. So it raises an error,
which PaSh catches silently, and PaSh ends up with no parallelism information for any `sort`
invocation except those using `-s` or `-u` (measured here). The session's own tests ran against stand-in
modules it wrote itself, which do not have that rule. The format document we gave it does not state
the rule either.

## What this run teaches

In plain terms, the most useful things run 9 shows. One run, so these are observations to test, not
conclusions.

- **Given a harder command, the agent worked much harder, unprompted.** Three times run 7's time and
  four times its runs before writing. It found real rules of `sort` that are easy to miss: `-o` may
  appear only once; check mode refuses `-o` and a second file; a bare `--check` takes no value; `-u`
  also implies "stable"; `--batch-size` must be at least 2. It also knew that sorted pieces must be
  merged, not just joined, and tested exactly that.
- **Its tests passed, and the class still fails where it matters.** Inside PaSh, its class gives no
  answer for an ordinary `sort` (no `-s` or `-u`). It could not see this, because it tested against
  stand-ins of its own making, which only repeat its own assumptions. Run 3, the one run that downloaded
  PaSh's real package, is the only run whose class tests could have caught a mistake like this.
- **Part of the blame is ours.** The rule that broke the class is in PaSh's source but not in our
  format document. And PaSh's own `grep` example, one of the samples, contains the same pairing of
  round robin with a custom merge, though PaSh never reaches it because those merges are marked as not
  yet available. The agent copied a pattern the example showed.
- **It again matched PaSh's hand-written table without seeing it,** down to the access kind of each
  file argument: `--random-source` is read as configuration, `--files0-from` names the input files, `-o`
  is the output, and `-T` is a scratch folder. Like `cut` in run 7, this could come from the manual or
  from the model having seen PaSh's public files in training; the log cannot tell which.
- **Its report again says more than its tests showed.** Its first test script ended "BAD = 8" and the
  report says every option "worked". Six of the eight were expected: a bare `--check` correctly takes no
  value, and checking unsorted input correctly fails. Two came from its own test input. None was
  investigated or mentioned. The report also says nothing about short options. Its syntax file says
  they take their value after `=`, but the test script only ever ran them with a separate value.
- **It flagged a real defect and kept it.** It warned that listing `--check` as an option makes PaSh's
  parser take the next word as its value. That is true (measured here: `sort --check a b` leaves only
  `b` as a file).
- **Against v1's reference for `sort`, it is close, with one shared weakness.** v1's curated grammar,
  v1's model output and the agent's file list nearly the same options. Fed to v1's generator, all
  three produce mostly valid command lines. The agent's does worst (53% accepted at two options per
  line, against 70% and 85%), for the same reason as `cut`: `=` after short options (`sort -t=:`,
  `sort -S=1k`), which v1's own curated grammar also does for `-S`.

**What it means.** For a command with real semantics, the agent behaves like a careful engineer who
writes tests against a mock of the library instead of the library itself. Its knowledge of `sort` is
good and well tested. Its knowledge of PaSh is whatever our documents and examples gave it, and its
tests cannot find a gap there. Every one of the agent's runs so far has shown the same thing: what it
checks against the binary is mostly right, and what it checks only against its own assumptions is
where the defects are.

## 2.1 Timeline and phases

| # | Phase | Calls | Start | Duration | What it read or ran |
|---|---|---|---|---|---|
| 1 | Read formats and samples | 1–14 (14) | 16:03:53 | 23 s | the folder and the syntax format (call 1); one batch for PaSh's format and all four samples (call 2), whose 31.2 KB output Claude Code saved to a file, showing a 2 KB preview; `cat` of that file (call 3), saved again; then the Read tool on PaSh's format and the `uniq`, `grep` and `tee` sample files (calls 4–14) |
| 2 | Manual and search | 15–16 (2) | 16:04:16 | 32 s | the manual rendered in full, `--version` (GNU coreutils 9.4), `--help` (call 15); the `rm` sample, import attempts and a `find` over `/` for `caruca` and `pash_annotations`, none found (call 16) |
| 3 | Probe | 17–18 (2) | 16:04:48 | 141 s | 88 runs of `sort` on small files in `/tmp/sorttest` (61 in call 17, 27 in call 18; counted from the commands) |
| 4 | Write | 19 (1) | 16:07:09 | 28 s | one shell call wrote all four files and loaded the table |
| 5 | Test what it wrote | 20–22 (3) | 16:07:37 | 60 s | test script 1 against stand-in modules: every spelling in the syntax file run through `sort` (about 128 runs, counted from the script); ends `BAD = 8` (call 20). Test script 2: both classes on stand-ins; 20 option sets split, sorted, merged and compared (about 825 runs, 0 failures) (call 21); a round-robin check on `-s` and `-u` (8 runs) (call 22) |
| 6 | Clean up and report | 23 (1) | 16:08:37 | 17 s | removed `__pycache__` in `output/`; report at 16:08:54 |

**First write:** call 19 at 16:07:09, 199 seconds into the session (started 16:03:50), after 88
probes. After it, about 960 runs of `sort`, all from its own test scripts. Nothing it wrote was changed
after the tests.

**Where the time went.** API time was 302.6 of the 304.1 seconds. The longest silence was the 52
seconds before the write call: the model composing four files of 196 lines in total.

![Session workflow](session_workflow.png)

## 2.2 Sources it used

**Inside the folder.** Both format documents; all four samples (the `rm` sample in call 16, the others
by the Read tool).

**The manual page it was pointed to.** Rendered in full in call 15. The table's argument names (`WORD`,
`NMERGE`, `PROG`, `KEYDEF`, `SIZE`, `SEP`, `N`) are the manual's.

**The binary.** `--version`, `--help`, 88 probes, then about 960 test runs.

**Outside the folder.** No network: `bash_urls=0`. A `find` over the whole disk for the two packages
(call 16), which found nothing. It did not try to install either.

**Compared with PaSh's own `sort` files** (from `pash_annotations` 0.2.4; the session never saw them):

| File | PaSh's own | The agent's |
|---|---|---|
| `sort.json` | 20 flag entries, 11 options | the same 11 options with **the same argument types** (`["FILE", "CONFIG_INPUT"]` for `--random-source`, `["FILE", "CONTAINER_FOR_INPUT"]` for `--files0-from`, `["FILE", "STREAM_OUTPUT"]` for `-o`, `["DIR", "OTHER_OUTPUT"]` for `-T`), in the same order, plus `--check WHEN`; the same flags plus `-y`, with `-c` lacking PaSh's `--check` alias |
| input/output class | standard output unless `-o`; standard input when there are no operands and no `--files0-from`; otherwise operands are inputs | the same, plus no standard output in check mode (`-c`, `-C`, `--check`) |
| parallelizability class | no split for `-c -C -u -z -R -s -m --files0-from --random-source`; otherwise consecutive pieces only, merged by a 2-way `sort -m` built from the invocation's ordering options; always marked "recombine in any order" | no split for `-c -C --check -m -R --debug -o -z --files0-from` or random sorting; otherwise consecutive pieces **and round robin**, merged by `sort -m` plus the ordering options (written out as a string); with `-s` or `-u`, consecutive pieces only and not "any order" |

The agent's class is in one respect more ambitious than PaSh's: it allows `-u` and `-s` (consecutive
pieces only), which PaSh's excludes, and it tested that `sort -m -u` over sorted pieces equals `sort -u`
of the whole.

![Information flow](information_flow.png)

## 2.3 Isolation and safety

`sort` reads, except for `-o`, which it tested on files in `/tmp/sorttest`, and `--compress-program=gzip`,
which runs another program. No isolation was set up or needed. It wrote only under `/tmp` and
`output/`, and deleted its scratch folders and the Python caches at the end (calls 22 and 23).

## 2.4 Testing

**The 88 probes (calls 17–18)** covered multiple files, `-` as standard input, `-o` (once, twice,
onto its own input), check mode (`-c`, `-C`, `--check=` with each value, with `-o`, with two files),
`-k` repeated and in three spellings, `-T` twice, seven `-S` sizes, `--batch-size`, `--parallel`, every
`--sort` word, `-t` (single, double, `\0`), `--files0-from` (three ways, and with an operand),
`--random-source`, `--compress-program`, `--debug`, `-m`, `-u`, `-z`, grouped flags, `-y`, `--`, the
obsolete `+POS` form, and whether merging sorted pieces reproduces one sort (with `-u` and `-n`).

**After writing (calls 20–22)**, as described in the timeline. Test script 1 checks spellings against
the binary but runs short options only with a separate value, never in the `=` form the syntax file
states. Test script 2 checks the merge command the class generates against the binary (0 failures over
20 option sets). It checks PaSh's side only against stand-ins: its `make_parallelizer_round_robin`
returns a tuple and enforces nothing.

**The closing report's claims, checked against the log.**

| Claim | Supported? |
|---|---|
| "Every spelling in the spec was run against `/usr/bin/sort`" | Yes (call 20), but short options only in the separate-word form |
| "all options rejected a missing argument, and both `--long=value` and separate-word forms worked" | **No.** The script ended `BAD = 8`: six `--check` cases (bare `--check` takes no value, which the session knew; checking unsorted test input exits 1) and two `--files0-from` cases (its test list was empty). Not mentioned in the report |
| "Spec, JSON table and `--help` output agree on the full set of spellings" | Yes (call 20) |
| "`-o` at most once, `-c` incompatible with `-o` and a second operand, bare `--check` leaves the next word as an operand, `-k` and `-T` repeat, `--batch-size` minimum 2, `--parallel` minimum 1, `-t` rejects multi-character separators" | Yes (calls 17–18) |
| "20 option combinations were split into 2, 3 and 5 parts … All matched the sequential output, including reversed merge order where commutativity is claimed" | Yes (call 21, `end-to-end failures: 0`), against stand-ins |
| "A negative test showed round-robin does break `-s` and `-u`" | Yes (call 22) |
| Doubt: "If the real option objects use different accessors, the merge command would lose its arguments" | **Resolved, no problem** (measured here): PaSh's options have `get_name()` and `get_arg()`, and inside PaSh the class produced `sort -m -s -k 1,1` for `sort -s -k 1,1` |
| Doubt: "PaSh's simple parser would wrongly swallow the next word after a bare `--check`" | **Confirmed** (measured here): `sort --check a b` parses as `--check` with value `a` and the single file `b` |
| (not in the report) whether the classes run in PaSh | **They do not, for the common case** (next section) |

## 2.5 Reproducibility and versions

- **Recorded during the run:** `sort --version` (GNU coreutils 9.4). The OS was not queried; `run.env`
  records Ubuntu 24.04.4 LTS, aarch64.
- **In the output:** the syntax file's header names GNU coreutils 9.4 and lists what was verified; the
  table and classes do not (1 of 4 files, as in runs 5 and 7).
- **Repeatability:** each probe ran once; the merge test was deterministic (fixed random seed for its
  test data).

## 2.6 Deliverable quality, mechanically

- All four files parse. `output/sort.py` **imports under v1's real `caruca.ir.syntax`**: 1 syntax, 33
  option nodes, 1 positional `Path` (zero or more, `-` is standard input).
- **Against the manual:** the session's own script found no spelling in `--help` missing from the syntax
  file or table. `-y` is not in the manual; `sort` accepts it.

### Inside PaSh's real code (measured here)

A copy of `pash_annotations` 0.2.4 was made in the `pash` VM with the agent's three files laid over
PaSh's own, so the installed package was not changed. Twelve `sort` invocations were run through PaSh's
parser and its two lookup functions, once with PaSh's own files and once with the agent's.

| Invocation | PaSh's own files | The agent's files |
|---|---|---|
| `sort a.txt`, `sort -n -k 2 a b`, `sort -t : -k 2,2n -r` | consecutive pieces, merge built from the ordering options | **no answer**: the class raises an error that PaSh catches and discards |
| `sort --sort=numeric a`, `sort --random-source=x a`, `sort -k2 a` | consecutive pieces (the attached values stay among the files, for both) | **no answer**, same cause |
| `sort -u`, `sort -s -k 1,1` | no split | consecutive pieces, merged by `sort -m -u` or `sort -m -s -k 1,1` |
| `sort -o out a` | consecutive pieces | no split |
| `sort -m a b`, `sort -R a`, `sort -c a` | no split | no split |

The input/output class gave an answer in every case. The error is an assertion in PaSh's `Parallelizer`.
A round-robin split may be paired only with concatenation or with one of the three "adjacent lines"
aggregators. The agent pairs it with a custom two-way merge. PaSh catches every exception from a class
and returns "no information", so the failure is silent. The consequence is that PaSh treats
the most common `sort` invocations as if no annotation existed. Neither our format document
(`formats/pash_annotation.md`, which lists the splitters and aggregators but no rule about combining
them) nor the session's stand-ins carried the rule. PaSh's own `grep` sample builds the same
combination, inside a branch that never runs because its custom aggregators are marked not
implemented.

### How v1's generator reads the three syntax files (measured here)

As for `cut` in run 7: each syntax file was fed to v1's own generator, and every distinct command line
was run once on GNU coreutils 9.4 with a three-line input. Lines whose printed form a shell cannot
re-read, or that use v1's path placeholders or an empty file list, are left out. At the shipped limit
of 4 options per line v1's reference grammar alone yields 307,023 distinct lines (1,972,046 in all), so
the run was made at 1 and 2.

| Syntax file | Limit 1: judged · accepted · real work | Limit 2: judged · accepted · real work | Main rejections at limit 2 |
|---|---|---|---|
| v1's curated reference | 53 · 45 (85%) · 43 | 1,275 · 894 (70%) · 803 | `--batch-size` and `--parallel` given −1, 0 or a word; `-S=` values |
| v1's model output | 44 · 42 (95%) · 40 | 903 · 771 (85%) · 686 | `--parallel` −1 or 0; incompatible ordering flags (`-gV` …) |
| the agent's (run 9) | 52 · 39 (75%) · 37 | 1,200 · 636 (53%) · 551 | `-t=:` (a two-character separator), `-S=1k`, `-k=…`, `--check=` (empty) |

"Real work" means accepted and not carrying `--help` or `--version`. Unlike `cut`, every file here yields
plenty of usable lines, because `sort` needs no option at all. The agent's file loses most where it puts
`=` after a short option, and through the empty `--check=` its rm-style "bare spelling" choice produces.
v1's reference loses through its value generator (integers −1, 0 and 1 for options that need at least
1 or 2).

- Not done here: scoring the syntax file against a reference.

## 2.7 Cost and effort

| Measure | Value |
|---|---|
| Model | `claude-fable-5-1`, medium effort (list-price cost basis, billed to the Max subscription) |
| Turns | 24 |
| Tool calls | 23: 12 Bash, 11 Read |
| Wall clock | 304.1 s (API time 302.6 s); 16:03:50 to 16:08:54 |
| Input tokens (uncached) | 386 |
| Cache writes | 55,629 tokens |
| Cache reads | 571,915 tokens |
| Output tokens | 23,977, of which 6,381 thinking |
| Reported cost | $2.46 at list price |
| Permission denials | 0 (permissions bypassed) |
| Web search / fetch tools | not available; 0 URLs in shell commands |

Not included: the launcher's $0.02 trial call that chose the model.

## 2.8 Behaviour worth recording

- **The output-size limit cost it a turn again** (calls 2 and 3), as in run 7; it then read file by file.
- **It searched the whole disk for the two packages** (call 16), then wrote stand-ins, as in run 7. It
  did not try to install them; run 3 (a different model) did.
- **It tested one of its own restrictions.** It wrote a test to show that round robin really does
  break `-s` and `-u` before keeping its class's exclusion of them, rather than only testing the cases
  it allows.
- **It reused a sample's device in a new place.** It modelled `--check`'s bare spelling the way the `rm`
  sample models `--preserve-root` (an empty choice) and said so in a comment. Under v1's generator that
  produces `sort --check=`, which `sort` rejects.
- **No questions asked**, nothing written outside `/tmp` and `output/`.

## How the Caruca paper designs the experiment, and what the agent chose instead

![v1's design versus the agent's approach, for sort](v1_design_vs_agent.png)

| Job | v1, as the paper designs it | Run 9's agent |
|---|---|---|
| 1. Learn the argument syntax | A model reads a bundled man page with worked examples (`touch`, `rm`, `mv`, `ls`) (section 3). v1's model output for `sort` has 28 options; v1's curated reference 31 | Manual, `--help` and 88 probes; 33 options with value bounds and the `--check` values |
| 2. Choose what to run | Code enumerates option combinations up to 4 with typed values (section 4): for `sort`, 1,972,046 command lines, 307,023 distinct (measured here) | 88 hand-chosen probes, then test scripts (about 960 runs) |
| 3. Run and observe | Each case isolated and traced; split-input runs for PaSh (section 5) | Plain shell on small files; output and exit codes |
| 4. Decide the behaviour | Rules over traces. v1's annotator assigns only `stateless`, `non-pure` or `side-effectful` (`tracer/data.py`): there is no class for "parallel with a merge step" | Reasoned that sorted pieces need a merge, tested `sort -m` against one sort for 20 option sets |
| 5. Write for consumers | v1's committed `sort` annotation (`caruca/save/sort.json`, 2024-12-08): 6 cases (`sort`, `sort -m`, each with no file, a relative and an absolute path), all `stateless`, standard output only | PaSh's current Python form; table matches PaSh's own; parallelizability class fails inside PaSh for ordinary sorts |

**`sort` is the case where a merge step decides everything.** Splitting the input and joining the sorted
pieces does not give a sorted whole, so `sort` can be parallelised only with a merge. PaSh's own
annotation says exactly that, and so does the agent's. v1's committed annotation calls six `sort`
cases `stateless`, which by v1's own definition means "split, run, join gives the same result". That is
false for `sort` in general. *Not established:* why v1's traces led there. One possible mechanism, from
v1's code: when combining environments, v1 keeps the most parallelizable class after dropping failed
runs, so small or already-ordered test inputs could produce it. Not checked against the trace for `sort`.

**Where the agent's design is weakest is the consumer, not the command.** Every claim it made about
`sort` that it checked against `sort` holds. The one that fails is a claim about PaSh that it could only
check against its own imitation of PaSh.

**Cost.** The paper reports CPU time per command (section 7.4), not the cost of its model step. Run 9
took 304 seconds and $2.46 at list price.

## Run 9 compared with runs 4, 5 and 7

Same model, effort, prompt, image and day; different command.

| Measure | Run 4 (`grep`, sample) | Run 5 (`rm`, sample) | Run 7 (`cut`) | Run 9 (`sort`) |
|---|---|---|---|---|
| Wall clock · turns · tool calls | 322 s · 11 · 10 | 60 s · 6 · 5 | 104 s · 18 · 17 | 304 s · 24 · 23 |
| Output tokens (thinking) · cost | 24,495 (6,663) · $2.54 | 4,623 (937) · $0.80 | 9,117 (1,464) · $1.25 | 23,977 (6,381) · $2.46 |
| Binary runs before writing | 72 | 27 | 21 | 88 |
| Test after writing | 154 runs, stand-ins | none | 45 runs, stand-ins | about 960 runs, stand-ins |
| Parser table versus PaSh's own | the sample's | the sample's | PaSh's minus `-M` (unseen) | PaSh's plus `-y`, `--check` (unseen) |
| Classes inside PaSh's real code | not run | not run | PaSh's answers except `-z` | no answer for ordinary sorts |
| Version named in output files | 3 of 4 | 1 of 4 | 1 of 4 | 1 of 4 |
| Report overstates | "Everything passed" (1 failure) | bare `--interactive` (manual) | "every option … matched" | "worked" over `BAD = 8` |

## What this run suggests we ask next

1. **State PaSh's combination rule in the format document**, or give the session the real
   `pash_annotations` package. Either is a repair to our materials, not tuning: the request as written
   allowed an answer PaSh cannot accept. Record it in task 016's revision log if changed.
2. **Load every run's classes in the pash VM as a standard step** of the analysis. Runs 4 and 5 were
   never checked this way.
3. **Score syntax files as generator input too** (share of generated lines the binary accepts), as
   the analyses of runs 6, 7 and 9 did.
4. **Look at v1's `stateless` label for `sort`** in its traces before citing it in any comparison.

## Diagram tooling

The three diagrams were drawn with the Excalidraw diagram skill
(`https://github.com/coleam00/excalidraw-diagram-skill`, at `.claude/skills/excalidraw-diagram/`). **The
skill's repository declares no licence**; it is listed as third-party, unlicensed material in
`LICENSE-TEMPLATES.md`, and is kept in the repository by Tiran's decision of 2026-10-13. Elements were
placed by hand in the `*.spec.json` files beside each diagram and expanded with
`naive_llm_caruca/excalidraw_fill.py`; the v1-versus-agent layout is run 7's with run 9's content. Each
was rendered with `uv run python render_excalidraw.py <file>`, inspected, and corrected.
