---
name: dev-machine-paths
description: "Tiran develops on two machines — a Windows/WSL PC and a Mac — and the caruca checkouts sit at different roots on each; both paths are current, resolve by platform"
metadata:
  type: reference
---

Tiran works on this project from **two machines**, and the same checkouts live at different
paths on each. **Neither path is stale or wrong** — pick by platform (`darwin` → the Mac,
`linux` → the WSL PC), and never "fix" one machine's path to the other's.

| What | PC (Windows/WSL) | Mac (darwin) |
|---|---|---|
| v1 (baseline) repo root | `~/stevens/caruca` | `/Users/tirandagan/dev/stevens/caruca` |
| v2 (this repo) | not recorded yet | `/Users/tirandagan/dev/stevens/caruca_v2` |

- `caruca_v2`'s CLAUDE.md writes all v1 paths as `~/stevens/...` — that is the WSL PC's
  perspective. On the Mac, substitute `~/dev/stevens/...`.
- Anything path-dependent that v2 code ships (e.g. task 001's `CARUCA_V1_ROOT`) must stay
  per-machine configurable (env var / `.env`), never hardcoded to one machine's layout.
- Machine-specific differences known so far:
  - The WSL clone of v1 carries local, uncommitted `CLAUDE.md` and `CODE_INSIGHTS.md`; the
    Mac clone does not (see [[caruca-v1-pipeline-reference]]).
  - The Mac clone has a working v1 venv (Python 3.12.13) at `caruca/.venv`.
  - CLAUDE.md's environment-constraint notes (no strace/overlayfs/docker/parallel, system
    Python 3.11) describe the WSL PC; macOS equally cannot run the Linux-only trace
    toolchain — tracing needs a provisioned Linux host from either machine.
  - **The Mac's shell is zsh, and two of its expansions break ordinary commands** (both hit on
    2026-10-06). A word starting with `=` is command-path expansion, so `echo =====` fails with
    "==== not found" and aborts the whole command chain; use `echo ---` as a separator. An unquoted
    glob in a flag is expanded first, so `grep -r --include=*.py` fails with "no matches found"; write
    `--include='*.py'`.
  - The Mac has the `pash-annotations` 0.2.4 source in the uv cache
    (`~/.cache/uv/archive-v0/*/pash_annotations/`), so PaSh's current annotation classes can be read
    without the `pash` Lima VM.
