#!/bin/bash
# Time PaSh across a grid of worker counts (width) and batch sizes, against
# plain bash, on the same CPU-bound grep used by pash-workers.sh.
#
#   usage: ~/pash-sweep.sh [reps] [dict-copies] [widths] [batches]
#          ~/pash-sweep.sh 5 2 "4 6 7 8 10 12 16" "125000 250000 500000 1000000 static 4000000"
#
# A batch of "static" means input size / width, rounded up: every worker gets
# exactly one slice, which is OpenMP's schedule(static) with no chunk size.
#
# Runs are interleaved in a shuffled order each repetition, so slow drift in the
# VM (thermal, other host load) spreads across all settings instead of landing
# on one. The first full pass is a warm-up and is thrown away.
# Prints CSV: copies,width,batch,rep,seconds,answer_ok
set -u
case "${1:-}" in -h|--help) sed -n '2,13p' "$0" | sed 's/^# \{0,1\}//'; exit 0;; esac
REPS=${1:-5}
COPIES=${2:-2}
WIDTHS=${3:-"4 6 7 8 10 12 16"}
BATCHES=${4:-"125000 250000 500000 1000000 static 4000000"}
D=$(mktemp -d); trap 'rm -rf "$D"' EXIT; cd "$D" || exit 1

for _ in $(seq 1 "$COPIES"); do cat /usr/share/dict/words; done > in.txt
BYTES=$(stat -c %s in.txt)
cat > script.sh <<'SH'
cat in.txt | grep '\(.\).*\1\(.\).*\2\(.\).*\3\(.\).*\4' | wc -l
SH
WANT=$(bash script.sh)

now() { date +%s.%N; }
elapsed() { awk -v a="$1" -v b="$2" 'BEGIN{printf "%.4f", b-a}'; }

configs=()
for w in $WIDTHS; do
  for b in $BATCHES; do
    [ "$b" = static ] && b=$(( (BYTES + w - 1) / w ))
    configs+=("$w:$b")
  done
done

echo "copies,width,batch,rep,seconds,answer_ok"
for rep in $(seq 0 "$REPS"); do
  # bash baseline, once per pass
  s=$(now); out=$(bash script.sh); e=$(now)
  [ "$rep" -gt 0 ] && echo "$COPIES,bash,0,$rep,$(elapsed "$s" "$e"),$([ "$out" = "$WANT" ] && echo 1 || echo 0)"
  for cfg in $(printf '%s\n' "${configs[@]}" | shuf); do
    w=${cfg%%:*}; b=${cfg##*:}
    s=$(now); out=$("$PASH_TOP/pa.sh" -w "$w" --r_split_batch_size "$b" script.sh 2>/dev/null); e=$(now)
    [ "$rep" -gt 0 ] && echo "$COPIES,$w,$b,$rep,$(elapsed "$s" "$e"),$([ "$out" = "$WANT" ] && echo 1 || echo 0)"
  done
done
