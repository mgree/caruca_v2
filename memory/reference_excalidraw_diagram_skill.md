---
name: reference_excalidraw_diagram_skill
description: Tiran wants run analyses to include workflow diagrams made with coleam00/excalidraw-diagram-skill; install facts (project .claude/skills, uv + playwright), no licence declared, the analysis prompt lives in naive_llm_caruca/README.md
metadata:
  type: reference
---

**What.** https://github.com/coleam00/excalidraw-diagram-skill — a Claude Code skill that writes
`.excalidraw` JSON from a description and renders it to PNG for a validate-and-fix loop. Tiran asked
on 2026-10-13 that analyses of naive-arm runs use it for workflow diagrams.

**Install (per the repo README, 2026-10-13):** copy the repo into the project's
`.claude/skills/excalidraw-diagram/`; then `cd .claude/skills/excalidraw-diagram/references && uv sync
&& uv run playwright install chromium`. Invoked conversationally (ask for a diagram); render with
`uv run python render_excalidraw.py <file.excalidraw>` from `references/`. `uv` is installed on the
Mac (`~/.local/bin/uv`); Tiran installed the skill into the project on 2026-10-13 evening (`.claude/skills/excalidraw-diagram/`); keep it out of the public repo as noted below.

**Licence:** the repository declares none (GitHub API, 2026-10-13). **Tiran's call (2026-10-13):
commit it with the repo anyway** ("im ok bringing it along"); it is listed as third-party in
`LICENSE-TEMPLATES.md` next to `impeccable`. Do not propose ignoring it again.

**Where the prompt is:** `naive_llm_caruca/README.md`, section "Analysing a collected run: a prompt
to start from". Runs on the Mac in the repo, never in a VM; writes to `runs/<run>/analysis/` and the
README's Observed entry only. Related: [[project_naive_claude_code_arm]].
