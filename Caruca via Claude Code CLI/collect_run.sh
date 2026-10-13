#!/usr/bin/env bash
# Copy every run folder out of a clone into this package's runs/ and delete the clone.
#   ./collect_run.sh <vm-name> [--keep]        --keep: do not delete the clone
# Each run in the VM (~/runs/<date>_<time>_<vm>_<command>_<version>/) lands here as runs/<same name>/,
# with environment.txt added. The clone's complete Claude Code session store is also saved once, as
# runs/<date>_<time>_<vm>_claude-sessions/, in case a session was started outside naive-run.
# runs/ is never copied into a VM (sync_to_vm.sh stages only the prompts, formats/ and samples/).
set -euo pipefail
NAME="${1:?usage: collect_run.sh <vm-name> [--keep]}"
KEEP="${2:-}"
HERE="$(cd "$(dirname "$0")" && pwd)"
limactl list -q | grep -qx "$NAME" || { echo "error: no VM named $NAME" >&2; exit 1; }
[ "$(limactl list "$NAME" --format '{{.Status}}')" = "Running" ] || limactl start "$NAME" --tty=false
ENV="$(limactl shell "$NAME" -- bash -lc 'claude --version; lsb_release -ds; uname -m; claude auth status 2>/dev/null | grep -E "subscriptionType|authMethod"' 2>/dev/null || true)"
RUNS="$(limactl shell "$NAME" -- bash -lc 'ls -1 ~/runs 2>/dev/null' 2>/dev/null | tr -d '\r' || true)"
if [ -z "$RUNS" ]; then echo "(no runs in $NAME)"; else
  for R in $RUNS; do
    if [ -e "$HERE/runs/$R" ]; then echo "skip: runs/$R already collected"; continue; fi
    limactl copy -r "$NAME:~/runs/$R" "$HERE/runs/$R"
    printf '%s\n' "$ENV" > "$HERE/runs/$R/environment.txt"
    echo "collected runs/$R:"; find "$HERE/runs/$R" -type f | sort | sed "s|$HERE/||"
  done
fi
S="$HERE/runs/$(date +%Y-%m-%d_%H%M%S)_${NAME}_claude-sessions"
limactl copy -r "$NAME:~/.claude/projects" "$S" 2>/dev/null && echo "saved the clone's session store as runs/$(basename "$S")" || true
if [ "$KEEP" = "--keep" ]; then echo "keeping clone $NAME"; else echo "== deleting clone $NAME"; limactl delete -f "$NAME"; fi
