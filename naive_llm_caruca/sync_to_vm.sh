#!/usr/bin/env bash
# Copy the prompt package into a Lima VM, leaving out the operator files (this README and this
# script). The work folder ~/naive-arm gets formats/, samples/ and an empty output/ and nothing else;
# the prompt files go to ~/prompts and logs to ~/runs, outside the folder the session works in, so a
# session cannot read the other prompt versions or the run's own metadata. Uses `limactl copy`.
#
#   ./sync_to_vm.sh                 # into naive-golden (the golden image; stop it again afterwards)
#   ./sync_to_vm.sh naive-run       # into a running clone
#
# Re-run against the golden image after any change to a prompt, a format document or a sample, so
# that later clones carry the change. output/ and ~/runs in the VM are left alone.
set -euo pipefail
VM="${1:-naive-golden}"
SRC="$(cd "$(dirname "$0")" && pwd)"
# copy only what the session may see: never runs/ (collected transcripts), README, scripts, vm/
STAGE="$(mktemp -d)"; mkdir -p "$STAGE/naive-arm-sync"
cp "$SRC"/PROMPT_v*.md "$STAGE/naive-arm-sync/"; cp -r "$SRC/formats" "$SRC/samples" "$STAGE/naive-arm-sync/"
limactl copy -r "$STAGE/naive-arm-sync" "$VM:/tmp/naive-arm-sync"; rm -rf "$STAGE"
limactl shell "$VM" -- bash -lc '
  set -e
  mkdir -p ~/naive-arm/output ~/prompts ~/runs
  cd /tmp/naive-arm-sync
  rm -f ~/prompts/PROMPT_v*.md ~/naive-arm/PROMPT_v*.md; rm -rf ~/naive-arm/runs
  cp PROMPT_v*.md ~/prompts/
  rm -rf ~/naive-arm/formats ~/naive-arm/samples
  cp -r formats samples ~/naive-arm/
  rm -rf /tmp/naive-arm-sync
  echo "synced into '"$VM"' (work folder ~/naive-arm, prompts in ~/prompts):"; find ~/naive-arm ~/prompts -type f -not -path "*/output/*" | sort
'
