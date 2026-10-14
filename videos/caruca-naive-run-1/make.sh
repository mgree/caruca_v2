#!/bin/zsh
# Rebuild scenes and index from timeline.json, then re-carve the music beds (the index rebuild wipes the carve).
set -e
cd "$(dirname "$0")"
python3 build_scenes.py >/dev/null
python3 build_index.py
V=(); for v in vo0 vo1 vo2 vo3 vo4 vo5 vo6 rec1 rec2 rec3 rec4 rec5 rec6; do V+=(--voice $v); done
for b in 1 2 3 4; do node ~/.claude/skills/hyperframes-audio/scripts/carve.mjs --comp index.html --bed music-bed-$b "${V[@]}" | tail -1; done
