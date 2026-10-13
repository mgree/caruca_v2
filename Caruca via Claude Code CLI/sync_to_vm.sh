#!/usr/bin/env bash
# Copy the prompt package into the Lima VM "caruca" as ~/naive-arm, leaving out the operator README.
# Re-run after any change to a prompt, a format document or a sample. Output and run logs in the VM
# are kept; delete them there by hand when a fresh start is wanted.
set -euo pipefail
SRC="$(cd "$(dirname "$0")" && pwd)"
limactl shell caruca -- bash -lc "
  set -e
  mkdir -p ~/naive-arm/output ~/naive-arm/runs
  cp '$SRC'/PROMPT_v*.md ~/naive-arm/
  rm -rf ~/naive-arm/formats ~/naive-arm/samples
  cp -r '$SRC'/formats '$SRC'/samples ~/naive-arm/
  rm -f ~/naive-arm/README.md ~/naive-arm/sync_to_vm.sh
  echo 'synced:'; find ~/naive-arm -type f -newer ~/naive-arm/output | sort
"
