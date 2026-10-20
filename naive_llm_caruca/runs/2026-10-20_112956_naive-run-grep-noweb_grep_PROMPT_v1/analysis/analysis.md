# Analysis of one run: `grep`, prompt version 1, 2026-10-20 11:30 (run 4)

**Run folder:** `naive_llm_caruca/runs/2026-10-20_112956_naive-run-grep-noweb_grep_PROMPT_v1/`
**Written:** 2026-10-20, from `stream.jsonl`, `stream.actions.log`, the session transcript, `run.env`,
`environment.txt` and the four output files. Call numbers below are the tool-call numbers printed in
`stream.actions.log` (1 to 10); times are local (UTC−4). Run 3, the earlier run of the same command
and prompt, is analysed in `runs/2026-10-13_193448_naive-run-grep_grep_PROMPT_v1/analysis/analysis.md`;
this document compares the two in a section of its own, and compares the session's approach with the
design of v1 described in the Caruca paper.

## Summary

A fresh Claude Code session (version 2.1.296, model `claude-fable-5-1` at medium effort, permissions
bypassed, web tools and MCP servers removed) in a throwaway Ubuntu 24.04 virtual machine was given
prompt version 1 for `grep`, which since 2026-10-20 carries one added rule: do not search the web or
read anything online. `grep` is one of the four samples, so its finished answer was in the folder.
In 322 seconds, 11 turns and 10 tool calls the session produced all four files, at a list-price cost
of $2.54. It made no network request of any kind (no URL in any of its 10 shell commands). It read
the samples, rendered the manual page it was pointed to and took the option list from it, ran the
binary 72 times on small files in `/tmp` before writing anything, wrote all four files in a single
call, and then tested them once with a harness of its own that runs the binary 154 times and drives
both classes through stand-in modules it wrote itself. That harness ended with one reported failure
(a `-p` option it had wrongly read out of the manual); the session confirmed the binary rejects
`-p`, did not rerun the harness, and reported "Everything passed". The parser table is the sample's
table with exactly the same 32 flag entries and 24 option entries; the syntax file and the two
classes were restructured, with the `-l`/`-L` distinction the sample gets wrong put right. Three of
the four files name GNU grep 3.11. Compared with v1's design in the Caruca paper, the session did
all five of the pipeline's jobs inside one model, chose 72 targeted probes instead of a generated
and bounded space of invocations, observed only printed output and exit codes instead of system
calls, and decided parallelizability by reasoning instead of by running a split-input test.

## 2.1 Timeline and phases

The session's 10 tool calls fall into seven phases. A phase's duration runs from its first call to
the next phase's first call; the last runs to the closing report. The session started at 11:30:01
and made its first call 9 seconds later.

| # | Phase | Calls | Start | Duration | What it read or ran |
|---|---|---|---|---|---|
| 1 | Orientation | 1–2 (2) | 11:30:10 | 20 s | listed the folder; read both format documents, all four grep sample files, `tee`'s three sample files and `uniq`'s parallelizability class; ran an unqualified `grep --version` and `grep --help`, which reached ugrep 7.8.4 through Claude Code's shell function |
| 2 | Identify the binary and its manual | 3–4 (2) | 11:30:30 | 44 s | `ls`, `file` and `--version` on `/usr/bin/grep` (GNU grep 3.11), `which -a grep`, the first 40 lines of the manual page (its version header), `type grep` (found Claude Code's shell function that runs ugrep), the samples again, `/usr/bin/grep --help` |
| 3 | Probe the binary | 5–6 (2) | 11:31:14 | 160 s | tried to import `caruca` and `pash_annotations`, `pip list`, `find /` for both; rendered the manual with `man -l` and pulled its option lines and four passages; 72 probe runs (31 in call 5, 41 in call 6) on `/tmp/t.txt` (four lines), `/tmp/rtest/` (two files), `/tmp/pats`, `/tmp/ex` |
| 4 | Write the deliverables | 7 (1) | 11:33:54 | 57 s | one shell call wrote `grep.py`, `grep.json` and both classes with here-documents, then checked the JSON parses and the Python compiles |
| 5 | Test | 8 (1) | 11:34:51 | 8 s | built `/tmp/grepspec_test` (stand-in `caruca.ir.syntax` and `pash_annotations` modules, `run_tests.py`) and ran it once: `TOTAL FAILURES: 1` |
| 6 | Check the failure | 9 (1) | 11:34:59 | 4 s | searched its saved manual for `-p` (nothing found), ran `grep -p` (exit 2, "invalid option") |
| 7 | Wrap up and report | 10 (1) | 11:35:03 | 20 s | deleted `__pycache__` from `output/`; closing report at 11:35:23 |

**First write:** call 7 at 11:33:54, all four files at once, 233 seconds into the session. The binary
had already been run in calls 3 to 6: 72 probe runs with inputs, plus `--version` and `--help`. After
the first write the binary ran only inside the harness (154 runs, call 8) and once more in call 9.
No file was edited after it was written, so there was no write, test, fix loop.

**Where the time went.** API time was 321.5 of the 322 seconds. Every tool call returned within half
a second; the time between calls is the model composing its next call: 35 s before call 5, 56 s
before call 6, 103 s before call 7 (the four files), 57 s before call 8 (the harness).

![Session workflow](session_workflow.png)

## 2.2 Sources it used

**Inside the folder.**
- Both format documents, read in full (the syntax format in call 1, PaSh's in call 2), with parts of
  PaSh's reread in calls 3 and 4.
- The grep sample, all four files, read in full (call 2) and again (call 4).
- For conventions: `tee`'s three sample files and `uniq`'s parallelizability class (call 2). It did
  not read the `rm` sample.

**The manual page it was pointed to.** Used, and used more than in run 3. Call 3 printed the first 40
lines, which hold the version stamp "GNU grep 3.11". Call 5 rendered the page with `man -l` and
printed every option line (47 lines). Call 6 saved the rendered page as `/tmp/grep.man` and printed
the passages on standard input, `-y`, `--unix-byte-offsets` and `-C NUM, -NUM`. The harness then
compared the syntax file's spellings against both the manual and `--help`.

**The binary.** `--help` (call 4) and 72 probe runs (calls 5 and 6); section 2.4 lists what they
established.

**Outside the folder.** Nothing from the network: `bash_urls=0` in `run.env`, and no command names a
host. It looked for the two Python packages the formats mention only on this machine: an import
attempt and `pip list` (call 5), and `find / -xdev` for `pash_annotations*`, `caruca*` and `pash`
(call 6), which found only the sample folders. It never tried to download either package. Whether
it would have tried without the prompt's new rule cannot be told from one run; run 3, without the
rule, fetched `pash-annotations` from PyPI within two minutes.

**Copied versus derived (grep is one of the four samples).** Diffs of `output/` against
`samples/grep/`:

| File | Sample | Output | Relation |
|---|---|---|---|
| `grep.py` | 66 lines, 1 syntax | 100 lines, 2 syntaxes | same constructor names; option list moved into a shared `_common_options`; two syntaxes (pattern as first operand; `-e`/`-f` with every operand a file); adds `-y` as an alias of `-i`, `-u`/`--unix-byte-offsets`, `min=0` on the three context counts, `flag_followed_by_equals=True` on `--color`, arity on the glob and `-e`/`-f` options; a header comment naming GNU grep 3.11 and listing what the format cannot express. 148 lines differ |
| `pash/grep.json` | 32 flag entries, 24 options | 32 flag entries, 24 options | **the same entries**, including argument types; only line layout and order differ |
| `pash/InputOutputInfoGeneratorGrep.py` | 42 lines | 43 lines | rewritten around one test (is there `-e` or `-f`?); implements what the sample leaves as a commented-out TODO: no standard input when recursive with no file. 65 lines differ |
| `pash/ParallelizabilityInfoGeneratorGrep.py` | 71 lines | 90 lines | restructured from the sample: same placeholder names (`merge_keeping_longer_output`, `sum_indiv_results_up`, `grep_add_*`) and the same "skip if not implemented" ending; adds `-m` and `-z` to the refusals, splits `-L` from `-l` with a new placeholder, and a header comment explaining each exclusion. 137 lines differ |

So the parser table was copied unchanged, and the other three files were reworked from the sample
with changes the probes or the manual support.

![Information flow](information_flow.png)

## 2.3 Isolation and safety

- **No isolation.** No namespace, container, `unshare`, `chroot` or copy-on-write layer. `strace` and
  `unshare` are installed in the image; neither was used. Probes used scratch files in `/tmp`
  (`t.txt`, `rtest/`, `pats`, `ex`, `grep.man`), and the harness lived in `/tmp/grepspec_test`.
- **Nothing destructive.** `grep` only reads. The session's deletions were its own: `rm -rf` of its
  harness folder before rebuilding it (call 8) and of `__pycache__` in `output/` (call 10).
- **Where it worked.** `~/naive-arm/output/` for the deliverables only; `/tmp` for everything else.
  Unlike run 3 it wrote no memory note and created no `tests/` folder in the work folder.
- **No system-call tracing.** What grep reads and writes was reasoned from the manual and from the
  printed output of probes (for example, `-r` with no file printed `a:beta`, a match from a file in
  the current directory), not observed.

## 2.4 Testing

**Probes before writing (calls 5 and 6; 72 runs).** Inputs: `/tmp/t.txt` with four lines (`alpha`,
`beta`, `gamma`, `alpha beta`), a directory `/tmp/rtest` with `a` and later `sub/b`, a pattern file and
an exclude file. Each probe printed its exit code. What they established:
- `-y` works as `-i`; `-u` and `--unix-byte-offsets` are accepted with an "obsolete" warning.
- Bare `--color` takes no following word (`--color never /tmp/t.txt` searched for "never"); an invalid
  `--color=bad` prints the usage text but exits 0.
- `-m -1` is accepted (no limit) and `-m 0` selects nothing; `-A -1`, `-m 1k` and `-A 1k` are rejected.
- `-f -` reads patterns from standard input; after `-e` every operand is a file; options may follow
  operands.
- With no file, grep reads standard input, except under `-r`, `-d recurse` or `--directories=recurse`,
  where it searches the current directory.
- `-l`, `-L`, `-H` and `-c` on standard input print "(standard input)" or a count; `-z` uses NUL-ended
  records; `-E -F` together is an error; unknown options exit 2.

**One harness, run once (call 8).** `run_tests.py` imports `output/grep.py` against a stand-in
`caruca.ir.syntax` that records constructor arguments, and does four things:
1. compares the set of spellings in the syntax file (86) with those found in `--help` and the
   manual: it reported `-p` as documented but missing, and `-y`, `-u`, `--unix-byte-offsets` as
   present but undocumented (the last three were allowed);
2. runs every spelling through the binary: each flag once; each `Selection` with every choice and
   with an invalid one; each valued option in its separate and attached or `=` form; each integer
   with `abc`, `-1` and `0`; plus five shape checks (`-` as standard input, `-f -`, the `-e` form, no
   file, bare `--color`);
3. checks that `grep.json` has the same flag and option spellings as the syntax file;
4. drives both classes through stand-in base classes on 18 invocations, printing each result, and
   asserts 16 expectations (4 on inputs and outputs, 12 on parallelizability).

Replaying the harness on the Mac with a stand-in binary that only counts its calls gives **154 runs
of the binary per harness run**.

**The closing report's claims, checked against the log.**

| Claim | Supported? |
|---|---|
| "`/usr/bin/grep` is GNU grep 3.11" | Yes: call 3 |
| "The shell's `grep` in this session is a function that runs ugrep, so every test called `/usr/bin/grep` by absolute path" | Yes: call 4 printed the function; every probe and test is by path. (The unqualified `grep --version` in call 2, which reached ugrep, was not a test) |
| "`grep.py` describes 86 option spellings" | Yes: the harness printed "spec spellings: 86" |
| "`-m` allows negatives since grep treats them as unlimited" | Yes: `-m -1` probe (call 5) and the manual passage (call 6) |
| "`-y` … and `-u`/`--unix-byte-offsets` … since the binary accepts both" | Yes: call 5 |
| "`pash/grep.json` lists the same flags and options" | Yes for the spellings (harness check 3). Not for their forms: the table takes `--color WHEN` as a separate word, the syntax file `--color=WHEN` only; the check compared spellings, not forms |
| "I separated `-L` from `-l` because the sample's shared aggregator is wrong for `-L`" | Yes: the sample sends both to `merge_keeping_longer_output`, while its own comment says the two propagate the file name under opposite conditions |
| "ran every spelling, every `Selection` choice, a bogus choice, attached and `=` forms, and integer boundary values through the binary" | Yes: harness section 2 |
| "exercised both generator classes on 18 invocations" | Yes, with a caveat: 18 were run and printed; 16 expectations were asserted |
| **"Everything passed."** | **No.** The harness's last line was `TOTAL FAILURES: 1`. The session attributed the failure to "regex noise from the man page", confirmed `grep -p` is rejected (call 9), and did not rerun the harness. Its search for the source (`'^\s+-p\b'`) could not have found it: the harness pattern takes any indented line that starts with a dash and a letter, so a wrapped line beginning with a word such as `-pattern` would yield `-p`, and the added `\b` excludes exactly that case. The source was never located, and the same pattern does not produce `-p` from the `--help` text in the log or from v1's copy of the 3.11 manual. "One failure, explained as a false alarm of the test, not rerun" is the supportable wording |
| "The real `caruca` and `pash_annotations` packages are not installed here" | Yes: calls 5 and 6 |
| "`-NUM` … cannot be expressed in either format" | Yes: neither format has a numeric-option form; the syntax file says so in a comment |
| "`--color` … I followed the samples and listed it as a value option" | Partly: true of `grep.json` only; `grep.py` departs from the sample here and follows the probe |
| "`-d recurse` … over-approximated as reading stdin" | Yes: the input/output class's comment and code |

## 2.5 Reproducibility and versions

- **Recorded during the run:** the binary's version (call 3), its type and size (`file`, `ls -la`),
  the manual's version stamp (call 3), and that `grep` in the tool's shell is a function (call 4).
  The OS was never queried; `run.env` records it (Ubuntu 24.04.4 LTS, aarch64). The report names grep
  3.11, not the OS.
- **In the output:** `grep.py` opens with "Syntax description of GNU grep 3.11 (/usr/bin/grep)"; both
  classes open their comments with "GNU grep 3.11". `grep.json` cannot hold a comment and states
  nothing. (Run 3 stated the version in none of its files.) The README's first note on this run said
  no file states the version; that was wrong and has been corrected.
- **Repeatability of probes:** every probe was run once; nothing was repeated or varied for
  nondeterminism.
- **Prompt version 1 asks for none of this**, so the version stamp is the session's own choice.

## 2.6 Deliverable quality, mechanically

- All four files parse (`ast.parse` for the three Python files, `json.tool` for the table).
- `output/grep.py` **imports under v1's real `caruca.ir.syntax` module** (checked on the Mac with v1's
  virtual environment): 2 syntaxes, with 46 and 48 option nodes and 2 and 1 positionals. The `--color`
  node loads as a `Selection` with `flag_followed_by_equals=True` and the three choices.
- **Against the manual** (the 47 option lines the session printed in call 5, 84 spellings in all):
  both the table and the syntax file contain every spelling except `-NUM`, which the syntax file
  names in a comment as inexpressible. Both add `-y`, `-u` and `--unix-byte-offsets`, which are not in
  the 3.11 manual or `--help` but which the binary accepts (call 5). Nothing else is added or missing.
- **The two files disagree on `--color`:** the syntax file says the value follows `=`; the table, as in
  the sample, says it is a separate word. The probe in call 6 showed the separate-word reading is
  wrong for this binary (`--color never` searched for "never"), so PaSh's parser would take the
  pattern as `--color`'s value in `grep --color pattern file`.
- **Known limits the session itself listed** and that the code confirms: `-NUM` is unparsed, so
  `grep -2 x` could be offered for parallel splitting although context lines cross chunk boundaries;
  `-d recurse` with no file is treated as reading standard input; `--include`/`--exclude` are
  treated as not narrowing the inputs.
- The classes were not run against PaSh's real code, here or in the session. That is a separate step
  in the pash VM.

## 2.7 Cost and effort

From the `result` event in `stream.jsonl`:

| Measure | Value |
|---|---|
| Model | `claude-fable-5-1`, medium effort (list-price cost basis, billed to the Max subscription) |
| Turns | 11 |
| Tool calls | 10, all Bash |
| Wall clock | 322 s (API time 321.5 s); 11:30:01 to 11:35:23 |
| Input tokens (uncached) | 322 |
| Cache writes | 59,798 tokens |
| Cache reads | 464,127 tokens |
| Output tokens | 24,495, of which 6,663 thinking |
| Reported cost | $2.54 at list price |
| Permission denials | 0 (permissions bypassed) |
| Web search / fetch tools | not available in this session; 0 URLs in shell commands |

Not included: the launcher's $0.02 trial call that chose the model, which runs before the session.
Of the 10 calls, 4 ran the binary with inputs (5, 6, 8, 9), 1 wrote the deliverables (7), and 1 built
and ran the harness (8).

## 2.8 Behaviour worth recording

- **Few, very large calls.** Calls 5, 6 and 8 are 2,367, 3,115 and 10,761 characters long: whole probe
  batches and a whole test program per call. Call 7 writes all four deliverables. The visible text
  between calls is four short sentences in total; the session explained itself mainly in the files'
  comments and in the closing report.
- **The `grep` shell function caught it once, as in run 3.** The unqualified `grep --version` and
  `grep --help` at the end of call 2 printed ugrep 7.8.4 and ugrep's help. The next call ran
  `/usr/bin/grep --version` (GNU grep 3.11) and `which -a grep`; call 4 ran `type grep` and printed the
  function. From then on every use of grep, including its own searches of text, was `/usr/bin/grep` by
  path. Both runs were misled by the first call and recovered in the next two.
- **No network, and no attempt.** The session never ran `curl`, `wget`, `pip download` or `git`. When
  the packages were not on disk it built stand-ins for them from the format document's description of
  their interfaces.
- **No loop back.** The only test run ended with a failure, and the session resolved it by argument
  (call 9) rather than by fixing and rerunning the test. Nothing in the deliverables changed after
  the first write.
- **It corrected the sample where the probes contradicted it,** in two of three places: `-l`/`-L` and
  recursion with no file. In the third, `--color`, it corrected the syntax file but kept the sample's
  table, and said so in its report.
- **No questions were asked**; the session ran unattended to its report, and listed its uncertainties
  under "Things I am unsure about".

## How the Caruca paper designs the experiment, and what the agent chose instead

The paper (Lamprou et al., arXiv:2510.14279, sections 2 to 6) splits the problem into four challenges
and gives each a dedicated, mostly hand-written component. The agent faced the same problem with no
pipeline at all. The table sets the two side by side, job by job; the paragraphs after it draw out the
differences that matter for this research.

![v1's design versus the agent's approach](v1_design_vs_agent.png)

| Job | v1, as the paper designs it | Run 4's agent |
|---|---|---|
| 1. Learn the argument syntax | A language model (GPT-4o) reads the man page or `--help` with three worked examples (`rm`, `mv`, `touch`), writes the syntax in v1's Python format; the result is imported and type-checked, with up to three retries that feed the error back (section 3.2) | The same model that does every other job writes it, starting from the grep sample and adding the manual's option lines and `--help`; checked afterwards by running every spelling through the binary, once, with no retry |
| 2. Choose what to run | Code generates every combination of up to four flags (the paper's survey of 665,000 real invocations finds 99.998% use four or fewer), with typed values: integers −1, 0 and 1, every choice of a selection, paths from a file-system model (missing, file, empty or non-empty directory, absolute or relative); inputs drawn from book text, arithmetic, JSON and images (section 4) | The model picks 72 cases by hand, mostly edge cases (`-m -1`, `-A -1`, `-m 1k`, invalid choices, options after operands, `-r` with no file), on one four-line text file and a two-file directory; flag combinations are sampled, not enumerated |
| 3. Run and observe | Each case runs in its own throwaway OverlayFS layer, in a fresh namespace, under `chroot`; `strace` records the file-system system calls, and the layer is diffed afterwards to classify every change (section 5) | Plain shell in `/tmp`, no sandbox; the session sees exit codes and printed output only |
| 4. Decide the behaviour | Rules over the traces: an invocation is stateless if running it on split input and joining the outputs gives the same bytes as one run; inputs and outputs are the files read and written; it also derives filtering, current-directory use, and file-system pre- and post-conditions (section 6.3) | The model reasons from what grep is documented to do and from the probes; it never runs a split-against-whole comparison (run 3 did); its test checks the classes against the model's own expectations |
| 5. Write for consumers | Adapters translate one internal result into PaSh and Shseer JSON, POSH YAML and ShellCheck Haskell (section 6.4) | Writes PaSh's current form directly (parser table plus two Python classes), as the prompt asks; no other consumer |

**Where the model sits.** The paper is explicit that the model "solely generates the syntax
specification — it is not involved in any remaining components that observe command execution and
derive command specifications." Everything after the syntax is deterministic code, so the same
syntax gives the same behaviour classes every time. In run 4 the model does all five jobs, including
the two the paper deliberately keeps away from it: choosing the experiments and judging the results.
That is the design difference this arm exists to measure, and it shows in the run: every behavioural
claim in the two classes traces to the model's reading of the manual and to probes it chose, not to
a rule applied to recorded evidence.

**Breadth versus aim.** v1 explores systematically and within a stated bound. For `grep` our earlier
reproduction (E0, `ai_docs/analysis/e0_artifact_pinning.md`, v1 run in the Lima VM) found 122
invocations when v1 is held to one flag at a time, out of 1,426,920 with no limit; each invocation is
then paired with several file-system states and input contents. The agent ran 72 invocations, chosen
for their edges. Some of them are cases v1's typed generators would not produce (`-m 1k`, `--color=bad`,
an operand before `-e`), and they found real facts (`-m` accepts negatives, `-A` does not). But no
invocation combined more than three flags, the input was one four-line file, and nothing guarantees
that the cases it did not think of behave like the ones it did.

**What is observed.** v1 watches system calls, so it knows which files an invocation opened, whether it
wrote anything, and whether it asked for the current directory. The agent saw only what grep printed.
Its conclusion that `-r` with no file reads the current directory is right, but it was inferred from
a printed match (`a:beta`), not from an observed read. For a command whose effects are not visible in
its output (`rm`, `tee`, anything that writes a file), this difference would decide whether the
input/output class can be right at all. `strace` was installed in the VM and was not used.

**How behaviour is decided.** v1's stateless rule is an experiment: split the input, run the pieces,
join the outputs, compare bytes. Run 4 decided the same question by argument ("grep processes its
input line by line"), and listed the exceptions it could think of (`-q`, `-m`, context, `-z`, and the
placeholders for `-c`, `-l`, `-L`, `-n`, `-b`). That reasoning is plausible for grep, which is well
known; it is exactly what cannot be relied on for an undocumented binary, which is the case Caruca is
designed for. One fact about v1's code (not its paper) belongs beside this: v1 reaches `stateless` only
from traces made with split input (`caruca trace --stdin split --content split`), which its own PaSh
pipeline uses; at the default trace mode it can classify nothing as stateless
(`memory/project_pash_downstream_study.md`).

**Isolation.** v1 isolates every execution because some commands destroy things (the paper's running
example is `rm -rf`). The agent isolated nothing. For `grep` this cost nothing; for `rm`, which is a
sample, the same choice would delete real files in the VM.

**Validation of the syntax.** v1 checks that the generated syntax loads and is well typed, and relies on
tracing to exercise it. The agent went further in one respect: it ran every spelling in its syntax file
through the binary and checked for "unrecognized option" or a usage message. That check leans on GNU
grep's error messages, which is the kind of signal the paper warns is not dependable in general
(challenge C1: "no standard way for a command to inform that its arguments were invalid"); it works for
this binary.

**Targets differ, so outputs are not directly comparable.** v1's PaSh adapter writes JSON in PaSh's
older annotation format; this prompt (since Prof. Greenberg's 2026-10-13 review) asks for PaSh's current
Python form. The agent also produced nothing for POSH, Shseer or ShellCheck, nor the file-system pre-
and post-conditions, because the prompt did not ask for them.

**Cost.** The paper reports CPU time per command (103 of its 120 commands under an hour at a two-flag
bound) and does not report the cost of its model step. Run 4 took 322 seconds and $2.54 at list price
for one command, almost all of it model time. The two are measured on different hardware and do
different amounts of work, so they cannot be set against each other as they stand.

**None of this says which output is more correct.** That needs scoring: the syntax file against v1's
spec and the hand-written reference with `caruca-v2 score`, and the classes in the pash VM.

## Run 4 compared with run 3

Same command, same prompt version (run 4's prompt adds only the no-web section), same image and Claude
Code version, both in watch mode. Different model (`claude-haiku-5-5` then, `claude-fable-5-1` at medium
effort now), different web access (open then, tools removed and forbidden in the prompt now), one week
apart. With one run each and three things changed at once, no difference below can be attributed to
any one of them.

![Run 3 and run 4 on one time scale](run3_vs_run4.png)

| Measure | Run 3 | Run 4 |
|---|---|---|
| Wall clock | 739 s | 322 s |
| Turns · tool calls | 73 · 72 | 11 · 10 |
| Output tokens (thinking) | 123,918 (82,852) | 24,495 (6,663) |
| Cost at list price | $0.96 | $2.54 |
| Network | 9 calls: PyPI wheel, GitHub search, 3 of this project's memory notes | none |
| Manual page | first 1,500 bytes only; options taken from `--help` | rendered; option lines used, and checked against |
| Binary runs before the first write | 85 | 72 |
| First write | 425 s (call 28) | 233 s (call 7) |
| Tests | 3 scripts; real PaSh parser and classes from the downloaded wheel; split-input checks on a 400-line corpus | 1 harness against stand-ins; no split-input check |
| Files changed after testing | yes: a guard added to both classes | none |
| `grep.json` versus the sample | sample plus 30 entries minus 2 | the sample's entries, unchanged |
| `grep.py` syntaxes (sample: 1) | 4 (shaped by our memory notes from GitHub) | 2 |
| Version named in output files | none | 3 of 4 |
| Closing report | accurate except one claim about the sample (`-y`, `-u`) | accurate except "Everything passed" |

What stands out:
- **Run 4 did less checking.** Run 3 spent 227 seconds testing and revising and used PaSh's real code;
  run 4 spent 12 seconds, against stand-ins it wrote itself, and changed nothing. Run 3's tests found
  something that led to a change; run 4's one finding was dismissed. Whether that is the model, the
  effort level, or the missing wheel (no web) cannot be separated here.
- **Run 4 copied the parser table; run 3 extended it.** Run 3 added the `-0`…`-9` and `--color=WHEN`
  spellings; run 4 kept the sample's table, including the `--color WHEN` form its own probe showed to
  be wrong.
- **Run 4's syntax file is its own.** Run 3's four-syntax structure came from our notes found on
  GitHub; run 4's two-syntax structure came from the manual's synopsis and the probes, with no outside
  help. Both reach the same underlying fact (after `-e` every operand is a file).
- **Run 4 is cheaper in tokens and dearer in money.** It produced a fifth of run 3's output tokens and
  cost 2.6 times as much, because Fable's list price per token is higher than Haiku's.

## What this run suggests we ask next

1. **Run a command that is not a sample.** Both grep runs could lean on the finished answer, and run 4
   kept the sample's table unchanged. `tac`, `tail` and `wc` are in the core nine and have no sample.
2. **Score the output.** `output/grep.py` imports under v1's syntax module, so `caruca-v2 score` can
   compare it with v1's spec and the hand-written reference; the classes can be loaded in the pash VM.
3. **Repeat run 4's setup** before reading anything into run 3 versus run 4: one more Fable run on grep
   would show how much of the light testing is the model and how much is chance.
4. **Decide whether the missing PaSh package matters.** Without the web the session could not load
   PaSh's real classes, so its test of them was against its own stand-ins. Putting `pash_annotations`
   in the golden image would restore that check without opening the web; it is a change to the
   environment, so it goes through task 016's revision log.
5. **Watch for "passed" claims.** This report said "Everything passed" over a run that ended with one
   failure. The analysis prompt's claim check caught it; keep that check.
6. **Try a command whose effects are not printed** (`tee` is a sample; `split` or `touch` are not in
   the core nine) to see whether the session reaches for `strace` or a sandbox when output alone
   cannot answer the question.

## Diagram tooling

The four diagrams were drawn with the Excalidraw diagram skill from
`https://github.com/coleam00/excalidraw-diagram-skill`, installed at `.claude/skills/excalidraw-diagram/`.
**The skill's repository declares no licence**; it is listed as third-party, unlicensed material in
`LICENSE-TEMPLATES.md`, and Tiran's decision (2026-10-13) was to keep it in the repository on that
basis. The renderer still uses the pinned `@excalidraw/excalidraw@0.18.0` import recorded in run 3's
analysis. Each diagram's elements were placed by hand; a small helper filled in Excalidraw's fixed
per-element fields (seeds, versions, flags) and sized text from its length. Each diagram was rendered
with `uv run python render_excalidraw.py <file>`, inspected, and corrected one to three times before it
passed. The first two diagrams answer the analysis prompt; the third and fourth were added for the
two comparisons.
