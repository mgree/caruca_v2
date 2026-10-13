#!/usr/bin/env bash
# Copy a run's results out of a clone into the repo and delete the clone.
#   ./collect_run.sh <vm-name> [dest-dir]
# Default dest: ../eval/naive_claude_code/<date>_<vm-name>/
set -euo pipefail
NAME="${1:?usage: collect_run.sh <vm-name> [dest-dir]}"
HERE="$(cd "$(dirname "$0")" && pwd)"
DEST="${2:-$HERE/../eval/naive_claude_code/$(date +%Y-%m-%d)_${NAME}}"
limactl list -q | grep -qx "$NAME" || { echo "error: no VM named $NAME" >&2; exit 1; }
[ "$(limactl list "$NAME" --format '{{.Status}}')" = "Running" ] || limactl start "$NAME" --tty=false
mkdir -p "$DEST"
limactl copy -r "$NAME:~/naive-arm/output" "$DEST/output"
limactl copy -r "$NAME:~/naive-arm/runs" "$DEST/runs"
limactl shell "$NAME" -- bash -lc 'claude --version; lsb_release -ds; uname -m; claude auth status 2>/dev/null | grep -E "subscriptionType|authMethod"' > "$DEST/environment.txt" || true
echo "== collected into $DEST:"; find "$DEST" -type f | sort
echo "== deleting clone $NAME"
limactl delete -f "$NAME"
