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

Each run uses exactly one prompt file. Record which one.

| File | What it adds | Purpose |
|---|---|---|
| `PROMPT_v1.md` | nothing: objective, deliverable, formats, samples | the fully naive baseline |
| `PROMPT_v2.md` | a "How the description must be established" section: derive everything by executing the command across its variations, not from memory; treat the probing as an experiment (repeatable, reproducible); identify the OS and command version, since core utilities differ between Unix flavours and versions, and state it in the report | does the session change its approach when told that execution, not recall, is the standard |

Later versions go in the same place, numbered in order, each described in the design record.

## Contamination hazard: run from a copy outside any checkout

Claude Code loads `CLAUDE.md` from the working directory and every parent directory, plus the global
`~/.claude/CLAUDE.md`. This folder lives inside the caruca_v2 repo, whose `CLAUDE.md` describes v1's whole
pipeline. A session started here would be primed with everything the experiment withholds.

So: copy this folder to a location with no `CLAUDE.md` above it and run from there. In the Lima VM:

```sh
# on the Mac
limactl copy -r "$HOME/dev/stevens/caruca_v2/Caruca via Claude Code CLI" caruca:~/naive-arm

# in the VM
limactl shell caruca
ls ~/.claude/CLAUDE.md 2>/dev/null && echo "global CLAUDE.md present: move it aside first"
cd ~/naive-arm && rm -f README.md        # the session must not read these notes
```

Also make sure the VM has no `.claude/settings.json` that pre-approves tools, unless that is a deliberate
part of the run. Record whatever permission mode was used.

## Running a session

Pick a command, say `sed`, and a prompt version. Start with an empty `output/`.

```sh
P=PROMPT_v2.md        # the prompt version for this run
```

**Interactive** (watch it work; you will be asked to approve tool calls unless you choose otherwise):

```sh
cd ~/naive-arm
sed 's/{{COMMAND}}/sed/g' "$P" > /tmp/prompt.md
claude            # then paste the contents of /tmp/prompt.md as the first message
```

**Headless, with a complete machine-readable log** (preferred for measurement; checked against Claude
Code 2.1.293, where `stream-json` output requires `--verbose`):

```sh
cd ~/naive-arm && mkdir -p runs
claude -p "$(sed 's/{{COMMAND}}/sed/g' "$P")" \
  --output-format stream-json --verbose > "runs/sed_${P%.md}.jsonl"
```

The last event in the log has `"type": "result"` and carries token usage, cost in dollars, duration and
the number of turns. Every tool call and its result is an earlier event, so the log is the full record of
what the session did.

Headless runs cannot ask you questions; if the session stops to ask one, that is itself a result worth
recording, and the interactive mode shows what it wanted to know.

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

Bring the outputs back to the caruca_v2 repo under `eval/` for scoring against v1 and the ground truth;
the harness and scorers there already accept v1's two formats.
