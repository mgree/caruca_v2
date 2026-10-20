---
name: reference-naive-run-playbook
description: Step-by-step playbook to run one command through the naive-LLM arm end to end (VM clone, run, collect, record, analyse with Excalidraw diagrams, compare with v1, PDF, addendum), with every gotcha hit on 2026-10-20
metadata:
  type: reference
---

How a run was done on 2026-10-20 (runs 4 `grep` and 5 `rm`), written so a future agent can repeat it
exactly. Operator docs: `naive_llm_caruca/README.md` (authoritative for the VM steps); design record:
`ai_docs/tasks/016_naive_claude_code_arm.md`. Related: [[project-naive-claude-code-arm]],
[[feedback-naive-llm-standalone]], [[reference-md-to-pdf-wide-diagrams]], [[feedback-readme-is-prompt-variant-log]].

## 1. Before the run (Mac, repo root)

- Prompt and launcher are in `naive_llm_caruca/` (`PROMPT_v1.md`, `PROMPT_v2.md`, `vm/naive-run`). Since
  2026-10-20 both prompts carry a "What you may not use" (no web) section and `naive-run` passes
  `--disallowedTools WebSearch WebFetch RemoteTrigger --strict-mcp-config`, then picks the model with a
  ~$0.02 trial call: `claude-fable-5-1` medium effort if allowed, else `claude-opus-5-5` high. It aborts
  (exit 4) if the VM is signed out. No `--fallback-model` (effort is per session).
- Choose the command and prompt with Tiran; default so far was `PROMPT_v1.md`, watch mode. Samples
  (`tee uniq grep rm`) show the agent a finished answer; prefer non-samples for evidence.
- `./new_run_vm.sh <name>` (e.g. `naive-run-rm`) clones `naive-golden` (stopping it if running), copies
  prompts/formats/samples and the helper in fresh. "signed in: yes" there is NOT proof: on 2026-10-20 a
  clone printed it and still failed with "OAuth session expired" seconds later. If that happens, Tiran must
  `limactl start naive-golden && limactl shell naive-golden`, run `claude`, `/login`, exit, stop the image
  (only he can: needs a browser). After his re-login, the next two clones (runs 4 and 5) worked.

## 2. The run

```sh
limactl shell <name> -- bash -lc 'cd ~/naive-arm && naive-run <cmd> PROMPT_v1.md' > <scratch>/console.log 2>&1
```
Run it in the background (Bash `run_in_background`); the harness notifies on exit. Then read the first
lines to confirm `== model claude-fable-5-1, effort medium (fable-ok)` and the session line. A command
outside the core nine (`cat grep pwd rm tac tail tee uniq wc`) asks y/N on a terminal and errors with no
terminal, so non-core commands need an interactive shell. If you add a Monitor on the log, start it
before the run can finish (run 5 ended in 60 s, before the monitor attached). macOS has no `timeout`.

### Non-coreutils commands (first done 2026-10-20: run 6, binwalk)

- `naive-run` requires `command -v <cmd>` AND `man -w <cmd>` to succeed in the clone, else exit 2. A tool
  built from a source repo usually has no installed man page, so it is refused as the script stands.
- Run 6's binwalk was apt-installed **in the golden image** by Tiran (not per clone). `run.env` records the
  OS but not the package version: record `dpkg -s <pkg>` from the clone by hand.
- Unattended launch without editing `naive-run`: `limactl shell <clone> -- bash -lc 'cd ~/naive-arm && echo
  y | script -qec "naive-run <cmd> PROMPT_v1.md" /dev/null' > log 2>&1` in the background (worked).
- **Never run the command in the golden image to check it** (run 6: a `binwalk --help` check there created
  `~/.config/binwalk/` in the image). Check in the clone instead. Use `collect_run.sh <clone> --keep` to keep
  the clone for post-run probes of the agent's claims, then `limactl delete -f <clone>`.
- Check packaging first: binwalk's binary is a Python script, so its source is on the machine and the agent
  used it (PROMPT_v1 bans only online repositories).
- The prompts forbid online code repositories but allow "a package installer" to use the network, so a
  session could `apt-get source` the command and read its code. Not observed; nothing audits for it.
- v1 has reference grammars (`syntax_specs/`) for some non-coreutils: awk, bc, sed, unzip, iconv, pandoc,
  convert, mogrify, uglifyjs. Anything outside v1's list has no reference to score against.

## 3. Collect and record (same turn)

- `./collect_run.sh <name>` copies `~/runs/<stamp>_<vm>_<cmd>_<ver>/` into `naive_llm_caruca/runs/` and
  deletes the clone. The folder holds prompt.md, run.env (model, effort, model_choice, bash_urls),
  stream.jsonl, stream.actions.log, transcript_*.jsonl, output/, bash_urls.txt, environment.txt.
- Write an "Observed, run N" entry under the prompt version in `naive_llm_caruca/README.md`, a ledger line
  in task 016 section 8, and update the memory note. Per the README rule, same turn as the run.

## 4. Analyse (the README's "Analysing a collected run" prompt)

1. Extract every call with timestamps and full results from the transcript (Python over
   `transcript_*.jsonl`: `tool_use` input, `tool_result` content, record `timestamp`), or
   `./tool_log.py -r`. Read ALL calls in full: summaries from the action log misled twice on 2026-10-20
   (run 4 actually read tee/uniq samples and hit the ugrep shell function in call 2; a first read said not).
2. Timeline (phase = calls, duration to next phase's first call), sources, copied-vs-derived (diff
   against `samples/<cmd>/`, which are v1's `syntax_specs/<cmd>.py` byte for byte plus PaSh 0.2.4 files),
   isolation, testing, versions, mechanics, cost, behaviour.
3. Check every claim in the agent's closing report against the log, in a table. Each analysed run had
   at least one overstated claim (run 4 "Everything passed" over `TOTAL FAILURES: 1`; run 5 "tested" with
   no post-write test).
4. Mechanical checks: `ast.parse` all files; import `output/<cmd>.py` under v1's real DSL with
   `~/dev/stevens/caruca/caruca/.venv/bin/python -I` and `sys.path.insert(0, '<v1>/caruca/src')`, run
   from a scratch dir; compare option spellings with the manual's option lines the agent printed.
5. To count binary runs inside an agent's own test harness, replay it on the Mac with paths rewritten and
   a counting stand-in binary (run 4: 154). Delete any `__pycache__` the replay leaves in the run folder.
6. v1 comparison (Tiran asked for it on every analysis): paper sections 2-6 vs the agent, job by job
   (syntax / choose what to run / run and observe / decide behaviour / write for consumers). Useful v1
   facts: model reads only `doc_sources/man/<cmd>.txt`, never `--help` or the binary; prompt forbids
   choices not in the man page; few-shot examples `touch rm mv ls` are their own references; paper's rm
   figure 8,749,056 configurations; `caruca generate <cmd> --max-count 1` runs on the Mac (grep: 122 lines);
   v1's committed PaSh annotation is `caruca/save/<cmd>.json`. Frame neutrally (v2 extends v1).
7. Tiran also wants a short plain-language "What this run teaches" section near the top (not verbose,
   not technical).

## 5. Diagrams (Excalidraw skill, `.claude/skills/excalidraw-diagram/`)

Read its SKILL.md and color-palette.md. Write a compact hand-placed spec, build with
`naive_llm_caruca/excalidraw_fill.py spec.json out.excalidraw`, render with
`cd .claude/skills/excalidraw-diagram/references && uv run python render_excalidraw.py <file>`, Read the
PNG, fix, repeat (1-3 rounds each). Start from an existing `runs/*/analysis/*.spec.json` (session_workflow,
information_flow, v1_design_vs_agent, run3_vs_run4). Gotchas: a long title widens the canvas and shrinks
everything; text placed over the first-write dashed line collides; arrows must end left of the target box
(x 1324 boxes, arrows 600→1322); dashed ellipses render badly. Keep `<name>.spec.json` beside each
`<name>.excalidraw`/`.png` in the run's `analysis/`.

## 6. PDF

`npm run convert -- <analysis.md> --title ... --subtitle ...` from the repo root. It downscales relative
images to 1,600 px, so: back up the .md, rewrite `](x.png)` to absolute paths, convert, restore, `cmp`.
Check `pdfimages -list` shows full-size images (~1,100 ppi). zsh: never start a word with `=` (`echo =====`
fails).

## 7. Addendum material

Anything for the paper goes in `ai_docs/analysis/white_paper_addendum_naive_llm.md` under the "Naive LLM"
heading, re-verified at primary sources, never citing the earlier rebuild's findings, then converted to PDF
the same way. Index line in `ai_docs/analysis/README.md` under "## Naive LLM".
