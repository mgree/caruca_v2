#!/bin/bash
# Benchmark PaSh against bash on a CPU-bound pipeline.
#   usage: ~/try-pash.sh [reps] [dict-copies]
#
# Conditions: bash, then PaSh at width 1, 2, 4, 8.
#   width 1 = PaSh's machinery with a single worker. It isolates PaSh's fixed
#             overhead from the gain that parallelism actually buys.
set -u
REPS=${1:-5}
COPIES=${2:-4}
D=$(mktemp -d); trap 'rm -rf "$D"' EXIT; cd "$D" || exit 1

for _ in $(seq 1 "$COPIES"); do cat /usr/share/dict/words; done > in.txt
echo "workload : grep with back-references (CPU-bound)"
echo "input    : $(wc -l < in.txt) lines, $(du -h in.txt | cut -f1)"
echo "reps     : $REPS      cores: $(nproc)"
echo

# The pattern is SINGLE-quoted on purpose. PaSh silently returns the wrong answer
# when it parallelizes a grep whose pattern is double-quoted (bash 928, PaSh 0).
# That is a PaSh bug, not an annotation effect. Verified 2026-10-05.
cat > script.sh <<'SH'
cat in.txt | grep '\(.\).*\1\(.\).*\2\(.\).*\3\(.\).*\4' | wc -l
SH

run_once() {
  local s e
  s=$(date +%s.%N)
  if [ "$1" = bash ]; then
    bash script.sh > o.txt 2>/dev/null
  else
    "$PASH_TOP/pa.sh" -w "$1" -d 2 --log_file L script.sh > o.txt 2>/dev/null
  fi
  e=$(date +%s.%N)
  awk -v a="$s" -v b="$e" 'BEGIN{printf "%.3f", b-a}'
}

parallelized() {   # reads L; UNKNOWN if no log, never assume success
  if [ ! -s L ]; then echo "UNKNOWN"; return; fi
  if [ "$(grep -ciE 'r_split|r_merge' L)" -gt 0 ] && ! grep -q "No region was parallelized" L
    then echo "yes"; else echo "no"; fi
}

REF=""; ORDER=(bash 1 2 4 8); declare -A TIMES
for cond in "${ORDER[@]}"; do
  run_once "$cond" > /dev/null                 # warm-up, discarded
  out=$(cat o.txt)
  if [ -z "$REF" ]; then REF="$out"; fi
  if [ "$out" != "$REF" ]; then
    echo "  !! condition '$cond' produced '$out', expected '$REF' - wrong answer, aborting"
    exit 1
  fi
  if [ "$cond" = bash ]; then par="n/a"; else par=$(parallelized); fi
  ts=""
  for _ in $(seq 1 "$REPS"); do ts="$ts $(run_once "$cond")"; done
  TIMES[$cond]="$ts"
  label=$([ "$cond" = bash ] && echo bash || echo "pash w=$cond")
  printf "  %-10s parallelized=%-8s times:%s\n" "$label" "$par" "$ts"
done

echo
echo "every condition produced the same answer: $REF"

python3 - "${TIMES[bash]}" "${TIMES[1]}" "${TIMES[2]}" "${TIMES[4]}" "${TIMES[8]}" <<'PY'
import sys, statistics as st
labels = ["bash", "pash w=1", "pash w=2", "pash w=4", "pash w=8"]
widths = [1, 1, 2, 4, 8]
data = [[float(x) for x in a.split()] for a in sys.argv[1:6]]
base = st.median(data[0])
print()
hdr = f"{'condition':<10}{'min':>8}{'median':>9}{'mean':>8}{'max':>8}{'stdev':>8}{'vs bash':>10}{'efficiency':>12}"
print(hdr); print("-" * len(hdr))
for i, (lab, d) in enumerate(zip(labels, data)):
    med = st.median(d); sp = base / med
    sd = st.stdev(d) if len(d) > 1 else 0.0
    eff = "" if i < 2 else f"{sp / widths[i] * 100:.0f}%"
    print(f"{lab:<10}{min(d):8.3f}{med:9.3f}{sum(d)/len(d):8.3f}{max(d):8.3f}{sd:8.3f}{sp:9.2f}x{eff:>12}")
seq1 = st.median(data[1]); best = st.median(data[4])
print()
print(f"  PaSh fixed overhead (w=1 vs bash) : {seq1-base:+.3f} s   ({seq1/base:.2f}x)")
print(f"  Parallel gain      (w=8 vs w=1)   : {seq1/best:.2f}x")
print(f"  Net effect         (w=8 vs bash)  : {base/best:.2f}x")
print()
print("  'efficiency' = speedup divided by width. 100% would be perfect scaling;")
print("  the shortfall is PaSh's split/merge cost plus whatever does not parallelize.")
PY
