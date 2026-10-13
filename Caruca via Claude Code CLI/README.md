# Caruca via Claude Code CLI — operator notes

**These notes are for the experimenter. The Claude Code session must never see this file.**

## What this folder is

A third, deliberately minimal arm of the Caruca comparison. A fresh Claude Code CLI session is handed
a problem statement (one of the `PROMPT_v*.md` files), two format descriptions (`formats/`) and four
examples of finished output (`samples/`, copied byte-for-byte from v1). Nothing about how v1 works. The experiment is to watch what an unguided session does to produce the two files: whether it
consults documentation, runs the binary, isolates it, probes it with inputs, or simply writes from memory.

Design record and revision history: `ai_docs/tasks/016_naive_claude_code_arm.md` in the caruca_v2 repo.

What the session sees:

```
PROMPT_v1.md                   the task and nothing else; {{COMMAND}} is replaced per run
PROMPT_v2.md                   v1 plus three lines of behaviour guidance (see "Prompt versions")
formats/syntax_description.md  format of <command>.py, derived from v1's ir/syntax.py
formats/pash_annotation.md     format of <command>.json, derived from v1's annotator/pash.py
samples/{tee,bc,grep,rm}/      v1's own output for those four commands, verbatim
output/                        where the session writes its two files
```

`tee`, `bc`, `grep` and `rm` are the samples, so they **cannot be test commands**. Everything else is fair.

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
| `PROMPT_v1.md` | nothing beyond the objective, the deliverable, the formats and the samples | everything: how to find out what the command accepts, whether to run it, isolation, versioning |
| `PROMPT_v2.md` | a section "How the description must be established": execution not recall, probing as an experiment, OS and command version | documentation, isolation, tracing, how to decide the behaviour class |

### PROMPT_v1 — the bare task

**What it contains.** The objective (describe the command so programs like PaSh can understand it
without running it), the two output files and their formats, the four samples, and one sentence
saying the approach is up to the session.

**Why it exists.** It is the floor. It measures what Claude Code does when nothing at all is said about
method: whether it reaches for documentation, runs the binary, or writes both files from what it
already knows about the command.

**What we expect.** Most likely the session writes the syntax file from general knowledge, perhaps
after reading the manual, and reasons out the behaviour classes without running anything. Isolation
is unlikely to come up unless the command is obviously destructive.

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

**What we expect.** The session should now run the command, which forces it to confront isolation on
its own for anything that writes or deletes. The reproducibility point may lead it to repeat runs or
to note nondeterminism. The version point should make it record the OS and the command's version
string; the interesting question is whether it also realises the syntax file is therefore
version-specific.

**Observed.** No run yet.

### Adding a version

Copy the previous version to `PROMPT_v<n+1>.md`, make the change, and add an entry here with the same
four parts (contains or adds, why, expected, observed). Rerun the leakage check on the new file
(the operator notes in the design record, task 016, list the withheld words) and note which withheld
words the new version introduces. Add a line to task 016's revision log.

## The environment: Claude Code inside the Lima VM

Claude Code runs **inside** the VM used for v1 tracing, so a session is driven from within the
experimental environment rather than from the Mac. Installed 2026-10-13:

| Item | Value |
|---|---|
| VM | Lima instance `caruca`, Ubuntu 24.04.4, arm64, 8 vCPU / 8 GiB |
| Install | native installer, `curl -fsSL https://claude.ai/install.sh \| bash`; no Node needed |
| Binary | `~/.local/bin/claude` in the guest home `/home/tirandagan.guest`; on `PATH` in login shells (`bash -lc`) |
| Version | 2.1.296 |
| Package copy | `~/naive-arm` in the guest home, written by `./sync_to_vm.sh` from this folder; README excluded |
| Sign-in | done 2026-10-13 by Tiran: claude.ai account (Max subscription), stored in the guest home. `~/.claude/settings.json` holds only a theme; no global `CLAUDE.md` |

**Signing in again, if ever needed.** Run `limactl shell caruca`, then `claude`, then `/login`. The VM has
no browser, so Claude Code prints a URL: open it on the Mac, finish the sign-in, and paste the code
it gives you back into the VM. The credentials are stored in the guest home, separate from the Mac's.
An `ANTHROPIC_API_KEY` in the environment works instead if the run should bill an API key rather than
the subscription; either way, record which was used, because cost reporting differs.

**Re-installing or upgrading.** Re-run the installer line above inside the VM. Update the version in
the table and in the run records.

## Contamination hazard: keep the session away from the project

Claude Code loads `CLAUDE.md` from the working directory and every parent directory, plus the global
`~/.claude/CLAUDE.md`. This folder lives inside the caruca_v2 repo, whose `CLAUDE.md` describes v1's
whole pipeline. A session started here would be primed with everything the experiment withholds.

So the session runs from `~/naive-arm` in the guest home, where nothing above it has a `CLAUDE.md`
(checked 2026-10-13). `sync_to_vm.sh` keeps that copy current and never copies this README.

Two residual hazards to know about:

- The Mac home is mounted read-write inside the VM at `/Users/tirandagan`, so the v1 and v2
  checkouts are reachable if the session goes looking. Nothing points it there; if a run log shows it
  reading under `/Users`, record that as a finding, and consider a VM without the mount for later runs.
- Before each run, confirm `~/.claude/CLAUDE.md` does not exist in the guest home and that
  `~/.claude/settings.json` is absent or deliberate (it can pre-approve tools). Record the permission
  mode used.

## Launching a run, step by step

All commands marked *Mac* run on the Mac; all marked *VM* run inside `limactl shell caruca`.

1. **Sync the package** (*Mac*), after any change to a prompt, format or sample:

   ```sh
   cd "$HOME/dev/stevens/caruca_v2/Caruca via Claude Code CLI" && ./sync_to_vm.sh
   ```

2. **Enter the VM and check it is clean** (*Mac*, then *VM*):

   ```sh
   limactl shell caruca
   cd ~/naive-arm
   ls ~/.claude/CLAUDE.md 2>/dev/null && echo "STOP: global CLAUDE.md present"
   cat ~/.claude/settings.json          # should hold only a theme
   claude auth status | grep loggedIn   # expect true
   rm -rf output/* && ls output         # start empty
   ```

3. **Choose the prompt version and the command** (*VM*). Not tee, bc, grep or rm.

   ```sh
   P=PROMPT_v2.md
   CMD=sed
   ```

4. **Run it**, one of two ways (*VM*).

   Headless, with the complete machine-readable log (preferred for measurement):

   ```sh
   mkdir -p runs
   claude -p "$(sed "s/{{COMMAND}}/$CMD/g" "$P")" \
     --output-format stream-json --verbose > "runs/${CMD}_${P%.md}.jsonl"
   ```

   The last event in the log has `"type": "result"` with token usage, cost, duration and turn count.
   Every tool call and result is an earlier event. A headless run cannot answer questions; if the
   session stops to ask one, that is a result, and the interactive mode shows what it wanted.

   Interactive, to watch it work and answer its permission prompts:

   ```sh
   sed "s/{{COMMAND}}/$CMD/g" "$P" > /tmp/prompt.md
   claude     # paste the contents of /tmp/prompt.md as the first message
   ```

   To let an interactive session run without permission prompts, start it with
   `claude --permission-mode bypassPermissions` and record that you did.

5. **Collect the results** (*VM*). The Mac home is mounted, so copy straight into the repo:

   ```sh
   DEST="/Users/tirandagan/dev/stevens/caruca_v2/eval/naive_claude_code/$(date +%Y-%m-%d)_${CMD}_${P%.md}"
   mkdir -p "$DEST" && cp -r output runs/"${CMD}_${P%.md}.jsonl" "$DEST"/ 2>/dev/null
   claude --version > "$DEST/claude_version.txt"; lsb_release -ds >> "$DEST/claude_version.txt"
   ```

6. **Write it down** (*Mac*): fill in the "Observed" part of the prompt version's entry above, and
   add the run to the record list in task 016. Then clear `output/` in the VM before the next run.

### A cleaner environment, when wanted

The caruca VM is the v1 tracing machine, and it shows: `strace` and `unshare` are installed, the
user-namespace fix is already applied (`kernel.apparmor_restrict_unprivileged_userns=0`), v1 is
installed in `~/caruca-venv`, and the Mac home is mounted read-write. A session there is naive by
prompt, not by environment, and a destructive test command can damage the tracing setup.

The better arrangement is a fresh Ubuntu 24.04 VM with no mount and nothing but Claude Code, kept as
a golden image and cloned for each run so every run starts identical (`limactl clone naive naive-run`;
Lima snapshots need the qemu backend, and these VMs use vz). Cost: about ten minutes, a second
sign-in, and a few GB of disk per clone. Not built as of 2026-10-13; if it is, record it here and
note which VM every run used.

## What to record per run

- command under test; prompt version; date; machine (Lima VM `caruca`, Ubuntu 24.04) and `claude --version`
- model id and permission mode used
- wall-clock, input/output tokens, cost (from the `result` event)
- the two files from `output/`, copied out before the next run
- observations, in these terms:
  - Did it read the command's documentation? Which source?
  - Did it run the binary at all? With what inputs?
  - Did it set up any isolation before running the binary, or run it in place?
  - Did it try to observe reads and writes (system call tracing or similar), or reason them out?
  - How did it decide the behaviour class?
  - What did it do with the `pipe:[N]` entries in the samples: copy the pattern, omit it, or invent values?
  - Did it stall on a question, and if so which one?

Bring the outputs back to the caruca_v2 repo under `eval/` (the Mac home is mounted in the VM, so
`cp` straight into `/Users/tirandagan/dev/stevens/caruca_v2/eval/...` works) for scoring against v1 and the ground truth;
the harness and scorers there already accept v1's two formats.
