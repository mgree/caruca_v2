# naive_llm_caruca — operator notes

**These notes are for the experimenter. The Claude Code session must never see this file.**

The folder was called "Caruca via Claude Code CLI" until 2026-10-13 evening, when Tiran renamed it
`naive_llm_caruca`. Older commit messages and the deleted run-1 records use the old name.

## What this folder is

A third, deliberately minimal arm of the Caruca comparison. A fresh Claude Code CLI session is handed
a problem statement (one of the `PROMPT_v*.md` files), two format descriptions (`formats/`) and four
examples of finished output (`samples/`: v1's syntax files and PaSh's own annotation files,
byte-for-byte). Nothing about how v1 works. The experiment is to watch what an unguided session does
to produce the files: whether it reads the manual page it is pointed to, runs the binary, isolates it,
probes it with inputs, or simply writes from memory.

Design record and revision history: `ai_docs/tasks/016_naive_claude_code_arm.md` in the caruca_v2 repo.

What the session sees:

```
PROMPT_v1.md                   the task and nothing else; {{COMMAND}} is replaced per run
PROMPT_v2.md                   v1 plus three lines of behaviour guidance (see "Prompt versions")
formats/syntax_description.md  format of <command>.py, derived from v1's ir/syntax.py
formats/pash_annotation.md     format of PaSh's three annotation files, derived from pash_annotations 0.2.4
samples/{tee,uniq,grep,rm}/    <cmd>.py from v1; pash/ = PaSh's parser table + generator classes, verbatim
samples/PASH_ANNOTATIONS_LICENSE  MIT licence of the copied PaSh files
output/                        where the session writes its files (output/<cmd>.py and output/pash/*)
runs/<date>_<time>_<vm>_<cmd>_<version>/   one folder per invocation of naive-run, collected: prompt.md (exactly as sent),
                               output/ (the deliverables), stream.jsonl (raw events), stream.actions.log (as shown on
                               screen), transcript_<session>.jsonl (Claude Code's own record), run.env, environment.txt
runs/<date>_<time>_<vm>_other-sessions/    sessions started in the clone outside naive-run (a bare `claude`); only written
                               when there are any; clones start with an empty session history

Operator tooling (never copied into a VM; sync_to_vm.sh stages only the prompts, formats/ and samples/):
new_run_vm.sh <name>           clone naive-golden -> <name>, start it, copy the package in fresh, install helper + welcome
collect_run.sh <name> [--keep] copy every run folder out of a clone into runs/, delete the clone (--keep to keep it)
sync_to_vm.sh [vm]             copy the package into a VM (used by new_run_vm.sh; run against naive-golden to update it)
vm/naive-run                   the in-VM helper: fills the placeholders and runs one session
vm/naive-watch.py              the live renderer for watch mode: prints each tool call, input and result; keeps raw + text logs
vm/bashrc-welcome.sh           the welcome printed on every interactive shell in a clone; lands you in ~/naive-arm
tool_log.py <log>              list every tool call (and -r: result) in a run's stream-json log or session transcript
```

`tee`, `uniq`, `grep` and `rm` are the samples. They can still be run, but the session then has a
finished answer in front of it, so a run on one of them measures copying, not solving; record it as such.

## Michael's feedback and what changed (2026-10-13)

Prof. Michael Greenberg reviewed the first prompt (inline comments on Discord). His points, and what
each one changed:

| Feedback | Change |
|---|---|
| "What command lines it accepts" is odd; use the technical terms. | The prompt now says "argument syntax: the options it accepts, the type of each option's argument, and the types of its operands", and the syntax format document opens the same way. |
| The prompt needs to specify the path to the binary and the path to the manual page. | Two placeholders, `{{PATH}}` and `{{MANPAGE_PATH}}`, after the objective. The launch procedure fills them with `command -v` and `man -w` inside the VM. |
| The behaviour annotation should be Python code that inspects and reflects on the parsed arguments, as in PaSh's current grep annotation, not JSON. | The behaviour deliverable is now the form PaSh consumes today: under `output/pash/`, the parser table `<cmd>.json`, an `InputOutputInfoGenerator<Cmd>.py` class and a `ParallelizabilityInfoGenerator<Cmd>.py` class. `formats/pash_annotation.md` was rewritten from PaSh's source (`pash_annotations` 0.2.4) to describe all three. The parser table is included because PaSh cannot run a generator class without it. The syntax description stays in v1's Python DSL. |
| "Both files must follow their format exactly" is unnecessary. | Removed. |
| The samples should match the current annotations in github.com/binpash/annotations. | Sample annotations are now PaSh's own files, copied unchanged from the package installed in the pash VM (MIT; licence beside them). PaSh has no annotation for `bc`, so `uniq` replaced it; `tee` and `rm` have no parallelizability class upstream, which the format document explains as "not parallelisable". |
| Replace "how you arrive at the two files is entirely up to you" with: generate a correct spec without my intervention, and be certain to test the binary against the spec you generate. | Done, in both prompt versions. This puts one method instruction into version 1, which was previously silent about execution; the version-1 entry below says so. |

How this changed the approach: the deliverable is now something a current PaSh can load, not only a
file in v1's shape, so a run can be judged by consumption as well as by comparison. The sample set
is anchored to PaSh's repository rather than to v1's output. And the floor prompt now asks for a
tested specification, so "does it run the binary at all" is no longer the first question; "does it
run it before or only after writing" is.

## Prompt versions

**This section is the living record of the prompt variations.** Whenever a prompt is added or changed,
or a run shows how a version behaves, update the entry here in the same sitting. Each run uses
exactly one prompt file, and the run record names it. Everything else in the package (formats,
samples, output location) is shared by all versions, so a difference between runs is attributable to
the prompt, the command, or the model's own variability, and nothing else.

Each version is the previous one plus something. The table is the summary; the entries below it say
what was added, why, what we expect to change, and what the runs actually showed.

| Version | Adds | Still withholds |
|---|---|---|
| `PROMPT_v1.md` | the objective, the deliverable, the formats, the samples, the binary and manual-page paths, and one instruction: test the binary against the specification | how to find out what the command accepts, isolation, versioning, reproducibility |
| `PROMPT_v2.md` | a section "How the description must be established": execution not recall, probing as an experiment, OS and command version | documentation, isolation, tracing, how to decide the behaviour class |

### PROMPT_v1 — the bare task

**What it contains.** The objective (describe the command's argument syntax and behaviour so programs
like PaSh can understand it without running it), the path of the binary and of its manual page, the
output files and their formats, the four samples, and the closing request: generate a correct
specification without intervention and be certain to test the binary against it.

**Why it exists.** It is the floor. It says nothing about how to find out what the command accepts or
how it behaves, nothing about isolation, nothing about versions. Since the 2026-10-13 review it does
carry one method instruction, "test the binary against the specification you generate", so it is no
longer silent about execution; v1 before that review said only "how you arrive at the files is up to
you". That earlier wording is kept in task 016's revision log, not as a live version.

**What we expect.** The session reads the manual page it was pointed to, writes the syntax file and
the generator classes from that, and then runs the binary at least enough to check them. Whether it
isolates anything before running a destructive command is the open question.

**Observed.** *Run 1, 2026-10-13, `sed`, interactive mode, clone `naive-run-grep`, Claude Code
2.1.296. Its records were collected and then deleted by Tiran the same evening, because the run came
from the leaky layout and the old helper; what follows is what was read off them before deletion,
and it is not reproducible from the repo.* About 8 minutes and 45 tool calls (37 Bash, 4 Write, 2 Edit,
2 Read). It produced all four files (syntax file 34 lines; parser table 71; input/output class 50;
parallelizability class 43). Its first Bash call listed the whole folder, and its second read
`PROMPT_v2.md` and the run's own `runs/sed_PROMPT_v1.env`, so a version-1 run saw version 2's
guidance and our metadata: a leak in the package layout, fixed the same day by moving prompts to
`~/prompts` and logs to `~/runs`. It then ran `sed --version`, read the manual page it was pointed
to, checked whether `caruca` or `pash_annotations` were importable, searched the filesystem for
them, and queried the GitHub API for repositories named "caruca" (the VM has network access). It
wrote and executed test scripts in its scratch directory and at the end deleted the compile caches
it had created under `output/`. Whether it ran `sed` on inputs before or only after writing the
files, and whether it isolated anything, was not read before the records were deleted. The operator
typed "status?" once, believing the session stalled; see "Interactive mode" below.

**Observed, run 2.** *2026-10-13 19:05, `grep`, watch mode, clone `naive-run-grep`, run 1 in that
clone, new layout. Collected to `runs/2026-10-13_190539_naive-run-grep_grep_PROMPT_v1/`. Not scored.
grep is one of the four samples, so the session had a finished answer in front of it.* 327 seconds,
34 turns, 33 tool calls (26 Bash, 5 Write, 2 Edit); the result event reports $0.32 at list price
(billed to the subscription). Its first three commands listed the folder, read both format documents,
and read grep's sample files. It then rendered the manual page it was pointed to, and spent calls 6
to 10 trying to install the `pash_annotations` package from PyPI (the stock image has no `pip`; it
found the package index reachable and listed versions 0.2.1 to 0.2.4). It invoked the grep binary
with patterns in 12 of its Bash calls. Its closing report claims 171 option cases checked against
grep 3.11 and 22 generator decisions confirmed, and says the syntax file could be checked only
against a stand-in for the `caruca` module. Output: syntax file 97 lines, parser table 54,
input/output class 43, parallelizability class 82. Whether it installed PaSh in the end, what the
"stand-in" was, and whether any run happened before the files were first written, is to be read off
the action log.

**Observed, run 3.** *2026-10-13 19:34, `grep`, watch mode, clone `naive-run-grep` (second clone of
that name), run 1 in that clone, model `claude-haiku-5-5`. Collected to
`runs/2026-10-13_193448_naive-run-grep_grep_PROMPT_v1/`; analysed in
[its `analysis/analysis.md`](runs/2026-10-13_193448_naive-run-grep_grep_PROMPT_v1/analysis/analysis.md)
with two diagrams. Not scored.* 739 seconds, 73 turns, 72 tool calls (43 Bash, 9 Write, 15 Edit,
4 Read, 1 TaskStop); $0.96 at list price. It read the manual page it was pointed to only for its
version header (first 1500 bytes) and took the option list from `grep --help`; it ran the binary 85
times on small files in a scratch directory under `/tmp`, with no other isolation, before writing
the first file at 19:41:53 (seven minutes in); it then wrote three check scripts of its own, ran the
real PaSh parser and classes from a `pash-annotations` 0.2.4 wheel it downloaded from PyPI (no
`pip` in the image, so it unpacked and read it), and fed one finding back into both generator
classes. It did not copy the sample: the parser table is the sample plus 30 entries (`-0`…`-9`
and the `--color=WHEN` spellings) minus the two `--color WHEN` options; the syntax file reuses the
sample's option inventory but has four syntaxes instead of one; both classes are rewritten. Its
syntax file imports under v1's real DSL. Three things to carry forward: Claude Code's shell defines
a `grep` function that runs its bundled ugrep, so the first `grep --version` reported ugrep 7.8.4
(the session noticed and used `/usr/bin/grep` by path); it searched GitHub for "caruca", found this
public repository and read three of our memory notes about grep, which shaped the four-syntax
structure; and no output file states the grep version. One claim in its report is wrong: the
sample's table already had `-y` and `-u`.

### PROMPT_v2 — execution is the standard

**What it adds.** One section with three points, placed between the samples and the closing scope
line:

1. parameters and behaviour must be derived from executing the command across all of its
   variations, not from memory or general knowledge;
2. the probing is an experiment: consider whether each observation is repeatable and whether the
   result would be reproducible by someone repeating the same runs;
3. core utilities differ in options and arguments between Unix flavours and versions, so establish
   which operating system and command version is in front of it and state that in the report.

Nothing else changes; the diff between the two files is exactly that section.

**Why it exists.** It is the smallest step away from naive that still says nothing about *how* to
execute. It names execution as the standard of evidence and raises the two concerns a careful
experimenter would have (reproducibility, platform dependence) without telling the session what to
do about them.

**What we expect.** The session should now derive the description from runs rather than from the
manual and only check afterwards, which forces it to confront isolation on its own for anything that
writes or deletes. The reproducibility point may lead it to repeat runs or
to note nondeterminism. The version point should make it record the OS and the command's version
string; the interesting question is whether it also realises the syntax file is therefore
version-specific.

**Observed.** No run yet.

### Adding a version

Copy the previous version to `PROMPT_v<n+1>.md`, make the change, and add an entry here with the same
four parts (contains or adds, why, expected, observed). Rerun the leakage check on the new file
(the operator notes in the design record, task 016, list the withheld words) and note which withheld
words the new version introduces. Add a line to task 016's revision log.

## The environment: a golden VM, cloned for every run

Runs happen in a throwaway clone of a **golden image**, a Lima VM named `naive-golden` that holds
nothing but Ubuntu 24.04, Claude Code and this package. The golden image is never run in; each run
starts from a fresh clone of it and the clone is deleted afterwards, so every run begins from a
byte-identical machine. Lima cannot roll a VM back on this Mac (snapshots are unimplemented on the vz
backend, and qemu is not installed), so cloning is the reset.

Why not the `caruca` VM, where v1's tracing runs: it has v1 installed in the guest home, the
user-namespace fix already applied, and the Mac home (both checkouts) mounted read-write. A session
there is naive by prompt but not by environment, and a destructive test command can damage the
tracing setup. Claude Code 2.1.296 is installed there too (2026-10-13), but it is not used for runs.

### What the golden image contains

Built 2026-10-13 with the steps below.

| Item | Value |
|---|---|
| VM | `naive-golden`, Lima template `ubuntu-24.04` (Ubuntu 24.04.4, arm64), vz backend, 4 vCPU / 4 GiB / 20 GiB, **no mounts** (`--mount-none`; there is no `/Users` inside) |
| Claude Code | 2.1.296, native installer, `~/.local/bin/claude` in the guest home `/home/tirandagan.guest`; on `PATH` in login shells |
| Package | `~/naive-arm`: `formats/`, `samples/`, empty `output/`, nothing else; the prompts in `~/prompts` and logs in `~/runs`, outside the session's folder (since run 1 showed the session reads everything in its folder); no README, no scripts |
| Sign-in | done 2026-10-13 (claude.ai account, Max subscription; `claude auth status` in the image confirms); every clone inherits it. The image's own session history (`~/.claude/projects`) was emptied on 2026-10-13 and each clone starts with it empty |
| Stock tools present | `strace`, `unshare`, `man`, `python3` (all in the stock cloud image); no `docker` |
| Stock restriction left in place | `kernel.apparmor_restrict_unprivileged_userns = 1`, so unprivileged user namespaces are blocked as on any stock Ubuntu 24.04; a session that wants a sandbox has to deal with that itself |
| Nothing from this project | no `CLAUDE.md` anywhere above `~/naive-arm`, no v1, no repo |

### Building the golden image (from scratch, on the Mac)

```sh
# 1. create and start: Ubuntu 24.04, no mounts
limactl create --name=naive-golden template:ubuntu-24.04 --mount-none --cpus 4 --memory 4 --disk 20 --tty=false
limactl start naive-golden --tty=false

# 2. install Claude Code (native installer; no Node needed)
limactl shell naive-golden -- bash -lc 'curl -fsSL https://claude.ai/install.sh | bash'
limactl shell naive-golden -- bash -lc 'claude --version'

# 3. copy the package in (README and sync script are left out by the script)
cd "$HOME/dev/stevens/caruca_v2/naive_llm_caruca" && ./sync_to_vm.sh naive-golden
```

**Sign in once** (by hand; the VM has no browser):

```sh
limactl shell naive-golden
claude          # then /login; open the printed URL on the Mac, paste the code back
exit
```

```sh
# 4. verify, then stop; the image is only ever started again to update it
limactl shell naive-golden -- bash -lc 'claude auth status | grep loggedIn; ls ~/.claude/CLAUDE.md 2>&1; cat ~/.claude/settings.json'
limactl stop naive-golden
```

**Updating the image** (new prompt version, changed sample, newer Claude Code): `limactl start
naive-golden`, make the change (`./sync_to_vm.sh naive-golden`, or re-run the installer line), `limactl
stop naive-golden`. Note the change in this README; clones made afterwards carry it, earlier runs did not.

## Running a command with Claude

### The short way (scripts)

```sh
cd "$HOME/dev/stevens/caruca_v2/naive_llm_caruca"
./new_run_vm.sh naive-run-sed-v2        # 1. fresh clone of naive-golden, package copied in fresh, helper installed
limactl shell naive-run-sed-v2          # 2. the welcome message lands you in ~/naive-arm and shows the commands
```

Inside the clone:

```sh
naive-run sed PROMPT_v2.md              # watch mode: runs unattended, every tool call / input / result shown live and logged
naive-run -i sed PROMPT_v2.md           # or Claude Code's own interactive screen (press Enter to send the prompt)
exit
```

**Watch mode** is the default and the one to use for the record. The session runs non-interactively
(`claude -p`) with permissions bypassed, which is safe in a throwaway VM and the only way a
non-interactive session can use tools at all, and its event stream is rendered live: the model and
permission mode at the start, the assistant's visible text, each tool call numbered with its name and
input (for Bash, the exact command), each result truncated to 600 characters, and the totals at the
end. Thinking is not shown. The run folder (see above) holds `stream.jsonl` (the raw stream, complete), `stream.actions.log`
(what was shown on screen) and `transcript_<session>.jsonl` (Claude Code's own session transcript).

**Interactive mode** (`-i`) is Claude Code's normal screen. The prompt is placed in the input box
and is not sent until you press Enter (observed 2026-10-13: a session looked stalled until a key was
pressed). You answer each permission prompt yourself. The screen shows less than watch mode does;
the transcript still records everything.

Back on the Mac:

```sh
./collect_run.sh naive-run-sed-v2       # 3. copies every run folder into runs/ here and deletes the clone
```

Then fill in the "Observed" part of the prompt version's entry above and add the run to task 016.

`naive-run` accepts any installed command. A command outside the project's core nine (cat, grep, pwd,
rm, tac, tail, tee, uniq, wc, the commands every other arm was measured on) gets a warning and a
yes/no confirmation; one of the four samples (tee, uniq, grep, rm) gets a note that the session can
see a finished answer, and runs. It refuses a command with no binary
or no manual page in the VM, an unknown prompt file, and a clone whose `output/` is not empty (one run
per clone).
It records the command, prompt version, binary path, manual-page path, mode, timestamps, Claude Code
version and OS in `runs/<command>_<version>.env`. `new_run_vm.sh` stops the golden image if it is
running (Lima clones only a stopped VM), and reports whether the clone is signed in and free of any
global `CLAUDE.md`.

### What the scripts do, by hand

1. **Clone and start** (*Mac*): `limactl clone naive-golden "$RUN" --tty=false && limactl start "$RUN" --tty=false`,
   then `./sync_to_vm.sh "$RUN"` so the package is the repo's current one, not the golden image's copy.

2. **Check the clone is clean** (*VM*): no `~/.claude/CLAUDE.md`; `~/.claude/settings.json` holds only a
   theme; `claude auth status` says logged in; `output/` is empty.

3. **Fill the three placeholders** (*VM*): the command, its binary's path (`command -v`) and its manual
   page's path (`man -w`):

   ```sh
   P=PROMPT_v2.md; CMD=sed; BIN=$(command -v "$CMD"); MAN=$(man -w "$CMD")
   fill() { sed -e "s|{{COMMAND}}|$CMD|g" -e "s|{{PATH}}|$BIN|g" -e "s|{{MANPAGE_PATH}}|$MAN|g" "$1"; }
   ```

4. **Run** (*VM*). Headless, with the complete machine-readable log (`stream-json` output requires
   `--verbose`, checked on 2.1.293 and 2.1.296):

   ```sh
   claude -p "$(fill "$P")" --output-format stream-json --verbose > "runs/${CMD}_${P%.md}.jsonl"
   ```

   The last event in the log has `"type": "result"` with token usage, cost, duration and turn count;
   every tool call and result is an earlier event. A headless run cannot answer questions; if the
   session stops to ask one, that is a result, and the interactive mode shows what it wanted.
   Interactive: `claude "$(fill "$P")"` starts the session with the prompt as its first message. To
   skip permission prompts, add `--permission-mode bypassPermissions` and record that you did.

5. **Collect and delete** (*Mac*): `limactl copy -r "$RUN:~/naive-arm/output" <dest>/output`, the same
   for `runs`, then `limactl delete -f "$RUN"`.

## Logging every tool call and command

There is no Claude Code flag that writes a tool log for an interactive session, but nothing is lost:

| Mode | Where every tool call and command is recorded | How |
|---|---|---|
| watch mode (`naive-run <cmd>`) | the run folder's `stream.jsonl` (raw) and `stream.actions.log` (as shown on screen) | `--output-format stream-json --verbose`: one JSON event per message; each `tool_use` block carries the tool name and its full input (for `Bash`, the exact command line), each `tool_result` the output; the final `result` event has tokens, cost and duration. `naive-watch.py` renders it live and keeps both files |
| both modes | the run folder's `transcript_<session-id>.jsonl` | Claude Code writes a transcript of every session to `~/.claude/projects/<cwd-slug>/<session-id>.jsonl` on its own, with the same `tool_use` / `tool_result` blocks plus timestamps; `naive-run` copies every session file written during the run into the run folder, and `collect_run.sh` saves any session started in the clone outside `naive-run` as `runs/<date>_<time>_<vm>_other-sessions/`; `new_run_vm.sh` empties the clone's session history at creation so inherited sessions never appear there |

To read either file as a plain list of calls (number, time, tool, command or path), on the Mac:

```sh
./tool_log.py runs/<date>_<time>_<vm>_<cmd>_<version>/transcript_<session-id>.jsonl
./tool_log.py -r ...      # also show each tool's result, truncated
./tool_log.py --json ...  # one JSON record per call, for scripts
```

Two more options exist and are not used: `claude --debug-file <path>` writes Claude Code's internal
debug log (noisy, not a tool log), and a `PreToolUse` hook in `~/.claude/settings.json` could append
every call to a file of our own, but that would put a hook into the environment the session runs in,
which the experiment keeps stock.

## Analysing a collected run: a prompt to start from

The idea: open a Claude Code session **on the Mac, in the caruca_v2 repo** (never in a VM), point it
at one collected run folder, and have it produce a written analysis plus workflow diagrams. The
diagrams use the Excalidraw skill from https://github.com/coleam00/excalidraw-diagram-skill, which
turns a description into an `.excalidraw` file and renders it to PNG for checking. The prompt below
installs the skill if it is missing, then runs the analysis. Replace the run folder path on the
first line. Treat the prompt as a starting point and refine it in place as analyses teach us what
to ask for.

One thing to know about the skill: its repository declares no licence (checked 2026-10-13). Tiran's
call, the same day, is to keep it in this repo anyway, under `.claude/skills/excalidraw-diagram/`,
alongside the other third-party skill (`impeccable`); it is listed with those exclusions in
`LICENSE-TEMPLATES.md` so nobody reads our licence as covering it. `uv`, which it needs, is on the Mac.

````markdown
Analyse one collected run of the naive Claude Code arm and produce a written analysis with workflow
diagrams. The run folder is: naive_llm_caruca/runs/2026-10-13_190539_naive-run-grep_grep_PROMPT_v1

**0. Set up the diagram skill (skip any step already done)**

The diagrams are made with the Excalidraw diagram skill. Check for `.claude/skills/excalidraw-diagram/SKILL.md`
in this repo. If it is absent, install it:

```sh
git clone --depth 1 https://github.com/coleam00/excalidraw-diagram-skill /tmp/excalidraw-diagram-skill
cp -r /tmp/excalidraw-diagram-skill .claude/skills/excalidraw-diagram
command -v uv >/dev/null || brew install uv
cd .claude/skills/excalidraw-diagram/references && uv sync && uv run playwright install chromium
```

Read the skill's SKILL.md before drawing anything, and follow its render-and-validate loop: every
diagram is rendered to PNG with `uv run python render_excalidraw.py <file>` from the skill's
`references/` folder, inspected, and fixed until it passes. Note the skill's licence in the analysis.

**1. What is in the run folder**

- `run.env`: command, prompt version, binary and man-page paths, mode, permission mode, timestamps,
  Claude Code version, OS, run number within the clone.
- `environment.txt`: Claude Code version, OS, architecture, account type.
- `prompt.md`: the prompt exactly as the session received it.
- `stream.jsonl`: every event of the session in order; each `tool_use` block has the tool name and
  full input, each `tool_result` the output, the final `result` event the turns, duration, cost and
  token counts. `stream.actions.log` is the same rendered as text.
- `transcript_<id>.jsonl`: Claude Code's own record of the session, with timestamps per record.
- `output/`: the deliverables: `<cmd>.py` (syntax description in v1's DSL) and `pash/` with the
  parser table `<cmd>.json`, `InputOutputInfoGenerator<Cmd>.py`, `ParallelizabilityInfoGenerator<Cmd>.py`.

`naive_llm_caruca/tool_log.py -r <file>` lists every tool call with its result. The README in
`naive_llm_caruca/` explains the arm; `ai_docs/tasks/016_naive_claude_code_arm.md` section 6 lists
the questions a run is meant to answer. Read both first.

**2. What to establish, each with evidence from the log (call numbers and timestamps)**

1. **Timeline and phases.** Segment the session into phases by what the calls do: orientation
   (listing and reading the folder), documentation (manual page or other sources), tooling attempts
   (installing packages, building test harnesses), probing the binary (running the command on
   inputs), writing the deliverables, testing them, reporting. For each phase: start and end time,
   number of calls, what it read or ran. Say in which phase the files were *first* written, and
   whether the binary was run before that point or only after.
2. **Sources it used.** The manual page it was pointed to, the samples, the format documents,
   anything from outside the folder (filesystem searches, network requests: name the URLs). If the
   command is one of the four samples, diff `output/<cmd>.py` and `output/pash/*` against
   `naive_llm_caruca/samples/<cmd>/` and say how much was copied versus derived.
3. **Isolation and safety.** Did it set up any isolation before running the binary (namespaces,
   containers, scratch directories, dry runs)? Did it run anything destructive? Where did it work?
4. **Testing.** What did it test, with what inputs, and what did it conclude? Check every claim in
   its closing report against the log (for example a count of cases checked) and say whether the
   log supports it.
5. **Reproducibility and versions.** Did it record the OS and the command's version, and does the
   output say which version it describes?
6. **Deliverable quality, mechanically.** Does `<cmd>.py` parse (`python3 -c "import ast; ast.parse(open(f).read())"`)?
   Do the PaSh classes parse? Does the parser table match the manual's options (list omissions and
   inventions)? Do not run the PaSh classes here; that needs the pash VM and is a separate step.
7. **Cost and effort.** Turns, tool calls by tool, duration, tokens, reported cost, from the
   `result` event.
8. **Behaviour worth recording** that the questions above do not cover: questions it wanted to ask,
   dead ends, retries, anything it did that the prompt did not ask for.

**3. Diagrams (with the skill)**

1. **Session workflow:** the phases from 2.1 as a left-to-right flow, each with its call count and
   duration, with loops where it iterated (write → test → fix), and the moment of first write marked.
2. **Information flow:** what went in (man page, binary runs, samples, format documents, outside
   sources) and which deliverable each fed, as a flow from sources to the four files.
Save both as `.excalidraw` and `.png` in `<run folder>/analysis/`.

**4. Write-up**

Write `<run folder>/analysis/analysis.md`: a one-paragraph summary, then sections 2.1 to 2.8 with
evidence, the two diagrams embedded, and a short list of what this run suggests we ask next. Plain
language: no shorthand a newcomer would not follow, every rate with its denominator. Then add a
one-paragraph summary with a link to the analysis under the matching prompt version's "Observed"
entry in `naive_llm_caruca/README.md`.

**5. Do not**

Do not change anything in `naive_llm_caruca/` other than `runs/<this run>/analysis/` and the README
entry. Do not touch the prompts, formats or samples: changing them is a change to the experiment and
goes through task 016's revision log. Do not copy anything into a VM.
````

## What to record per run

- command under test; prompt version; date; the clone's name and that it came from `naive-golden` (Ubuntu 24.04, arm64); `claude --version`
- model id and permission mode used
- wall-clock, input/output tokens, cost (from the `result` event)
- the run folder, collected with `collect_run.sh`
- observations, in these terms:
  - Did it read the command's documentation? Which source?
  - Did it set up any isolation before running the binary, or run it in place?
  - Did it try to observe reads and writes (system call tracing or similar), or reason them out?
  - How did it decide the behaviour class?
  - Did it try to run PaSh's parser or generator interfaces against its own classes, or install `pash_annotations`?
  - Did it stall on a question, and if so which one?
  (The command, prompt version, mode, timestamps and versions are already in the run folder's `run.env`.)

Bring the outputs back to the caruca_v2 repo under `eval/` (the Mac home is mounted in the VM, so
`cp` straight into `/Users/tirandagan/dev/stevens/caruca_v2/eval/...` works) for scoring against v1 and the ground truth;
the harness and scorers there already accept v1's two formats.
