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

**Renderer fix (2026-10-13, verified).** The skill was absent from `.claude/skills/` at the start of
the run-3 analysis session and was installed then (clone + `uv sync` + playwright chromium; both
work on this Mac). Its `render_template.html` imports `https://esm.sh/@excalidraw/excalidraw?bundle`
unpinned; on 2026-10-13 that resolved to 0.18.1 whose dependency
`@braintree/sanitize-url@6.0.2/es2022/dist/constants.mjs` returned 404 from esm.sh, so
`window.__moduleReady` never fired and `render_excalidraw.py` timed out after 30 s every time.
**Pinning the import to `@excalidraw/excalidraw@0.18.0?bundle` loads in ~5 s** (0.17.6 lacks the
`exportToSvg` export). The pinned template is in place; the original is `render_template.html.orig`.
Also: `exportToSvg` gets the raw elements (no `restoreElements`), so every element needs the full
field set from `references/element-templates.md`. Rendering takes ~10 s per diagram.

**State at the end of 2026-10-13:** the skill is tracked in git (committed during the run-3
analysis session, by Tiran in parallel) and listed in `LICENSE-TEMPLATES.md` as third-party with no
licence. The pinned `render_template.html` and the `.orig` copy were uncommitted when this was written.

**Where the prompt is:** `naive_llm_caruca/README.md`, section "Analysing a collected run: a prompt
to start from". Runs on the Mac in the repo, never in a VM; writes to `runs/<run>/analysis/` and the
README's Observed entry only. Related: [[project_naive_claude_code_arm]].
