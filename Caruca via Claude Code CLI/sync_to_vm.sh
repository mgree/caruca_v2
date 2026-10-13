#!/usr/bin/env bash
# Copy the prompt package into a Lima VM as ~/naive-arm, leaving out the operator files
# (this README and this script). Works for VMs with no mounts: it uses `limactl copy`.
#
#   ./sync_to_vm.sh                 # into naive-golden (the golden image; stop it again afterwards)
#   ./sync_to_vm.sh naive-run       # into a running clone
#
# Re-run against the golden image after any change to a prompt, a format document or a sample, so
# that later clones carry the change. output/ and runs/ in the VM are left alone.
set -euo pipefail
VM="${1:-naive-golden}"
SRC="$(cd "$(dirname "$0")" && pwd)"
limactl copy -r "$SRC" "$VM:/tmp/naive-arm-sync"
limactl shell "$VM" -- bash -lc '
  set -e
  mkdir -p ~/naive-arm/output ~/naive-arm/runs
  cd /tmp/naive-arm-sync
  rm -f README.md sync_to_vm.sh; rm -rf output runs
  cp PROMPT_v*.md ~/naive-arm/
  rm -rf ~/naive-arm/formats ~/naive-arm/samples
  cp -r formats samples ~/naive-arm/
  rm -rf /tmp/naive-arm-sync
  echo "synced into '"$VM"':"; find ~/naive-arm -type f -not -path "*/output/*" -not -path "*/runs/*" | sort
'
