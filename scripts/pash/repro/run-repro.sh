#!/bin/bash
# Run one reproducer pipeline under plain bash and under PaSh, in a throwaway
# directory, and report: both answers, whether they match, whether PaSh
# parallelized, and any PaSh error.
#
#   usage: run-repro.sh <pipeline.sh> [width] [dict-copies]
#          run-repro.sh double_quoted_grep_wrong_answer.sh 8 2
#
# Each pipeline reads in.txt (copies of /usr/share/dict/words). A pipeline that
# writes out.txt is compared on out.txt's contents instead of standard output.
set -u
case "${1:-}" in ""|-h|--help) sed -n '2,10p' "$0" | sed 's/^# \{0,1\}//'; exit 0;; esac
SRC=$(readlink -f "$1"); WIDTH=${2:-8}; COPIES=${3:-2}
D=$(mktemp -d); trap 'rm -rf "$D"' EXIT; cd "$D" || exit 1
for _ in $(seq 1 "$COPIES"); do cat /usr/share/dict/words; done > in.txt
cp "$SRC" script.sh

answer() { if [ -f out.txt ]; then sha256sum < out.txt | cut -c1-16; rm -f out.txt; else sha256sum < "$1" | cut -c1-16; fi; }

bash script.sh > bash.stdout 2>/dev/null; B=$(answer bash.stdout)
"$PASH_TOP/pa.sh" -w "$WIDTH" -d 2 --log_file pash.log script.sh > pash.stdout 2> pash.err; RC=$?
P=$(answer pash.stdout)

PAR=no
grep -qE 'r_split|r_merge' pash.log 2>/dev/null && ! grep -q "No region was parallelized" pash.log && PAR=yes
echo "pipeline     : $(cat script.sh)"
echo "bash answer  : $B  ($(head -c 60 bash.stdout | tr '\n' ' '))"
echo "pash answer  : $P  ($(head -c 60 pash.stdout | tr '\n' ' '))  exit $RC"
echo "same answer  : $([ "$B" = "$P" ] && echo yes || echo NO)"
echo "parallelized : $PAR"
[ -s pash.err ] && echo "pash stderr  : $(grep -m1 -E 'Error|assert|Assertion' pash.err || head -1 pash.err)"
exit 0
