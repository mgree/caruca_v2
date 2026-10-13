# Caruca via Claude Code CLI — operator notes

**These notes are for the experimenter. The Claude Code session must never see this file.**

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

Operator tooling (never copied into the VM's work folder):
new_run_vm.sh <name>           clone naive-golden -> <name>, start it, copy the package in fresh, install helper + welcome
collect_run.sh <name> [dest]   copy output/ and runs/ out of a clone into eval/naive_claude_code/, delete the clone
sync_to_vm.sh [vm]             copy the package into a VM (used by new_run_vm.sh; run against naive-golden to update it)
vm/naive-run                   the in-VM helper: fills the placeholders and runs one session
vm/bashrc-welcome.sh           the welcome printed on every interactive shell in a clone; lands you in ~/naive-arm
```

`tee`, `uniq`, `grep` and `rm` are the samples, so they **cannot be test commands**. Everything else is fair.

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

**Observed.** No run yet.

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
| Package | `~/naive-arm`: the prompts, `formats/`, `samples/`, empty `output/` and `runs/`; no README, no sync script |
| Sign-in | see "Sign in once" below; the credentials live in the image and are inherited by every clone |
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
cd "$HOME/dev/stevens/caruca_v2/Caruca via Claude Code CLI" && ./sync_to_vm.sh naive-golden
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
cd "$HOME/dev/stevens/caruca_v2/Caruca via Claude Code CLI"
./new_run_vm.sh naive-run-sed-v2        # 1. fresh clone of naive-golden, package copied in fresh, helper installed
limactl shell naive-run-sed-v2          # 2. the welcome message lands you in ~/naive-arm and shows the commands
```

Inside the clone:

```sh
naive-run sed PROMPT_v2.md              # headless; full log in runs/sed_PROMPT_v2.jsonl, metadata in runs/sed_PROMPT_v2.env
naive-run -i sed PROMPT_v2.md           # or interactive: watch it, answer its permission prompts
exit
```

Back on the Mac:

```sh
./collect_run.sh naive-run-sed-v2       # 3. copies output/ and runs/ to eval/naive_claude_code/<date>_naive-run-sed-v2/ and deletes the clone
```

Then fill in the "Observed" part of the prompt version's entry above and add the run to task 016.

`naive-run` refuses a sample command (tee, uniq, grep, rm), a command with no binary or no manual
page in the VM, an unknown prompt file, and a clone whose `output/` is not empty (one run per clone).
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

## What to record per run

- command under test; prompt version; date; the clone's name and that it came from `naive-golden` (Ubuntu 24.04, arm64); `claude --version`
- model id and permission mode used
- wall-clock, input/output tokens, cost (from the `result` event)
- everything under `output/`, copied out before the next run
- observations, in these terms:
  - Did it read the command's documentation? Which source?
  - Did it set up any isolation before running the binary, or run it in place?
  - Did it try to observe reads and writes (system call tracing or similar), or reason them out?
  - How did it decide the behaviour class?
  - Did it try to run PaSh's parser or generator interfaces against its own classes, or install `pash_annotations`?
  - Did it stall on a question, and if so which one?

Bring the outputs back to the caruca_v2 repo under `eval/` (the Mac home is mounted in the VM, so
`cp` straight into `/Users/tirandagan/dev/stevens/caruca_v2/eval/...` works) for scoring against v1 and the ground truth;
the harness and scorers there already accept v1's two formats.
