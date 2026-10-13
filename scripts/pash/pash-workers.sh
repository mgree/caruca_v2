#!/bin/bash
# Show PaSh's parallel workers: how many, how long each was busy, and how much
# of the wall clock they overlap.
#
#   usage: ~/pash-workers.sh [width] [dict-copies] [batch-bytes]
#          ~/pash-workers.sh 8 2            # 8 workers, ~1.3M lines, 1 MB batches (default)
#          ~/pash-workers.sh 4 4            # 4 workers, ~2.6M lines
#          ~/pash-workers.sh 8 2 250000     # 8 workers, 250 KB batches
#
# batch-bytes is passed to PaSh as --r_split_batch_size: the size of each slice
# of input handed to a worker. PaSh deals slices to workers in turn, and each
# slice gets its own grep process, so smaller batches mean more grep processes.
#
# Each worker runs `bash -c ' grep ... '`, so grep is found on PATH. We put a
# wrapper named grep earlier on PATH; it timestamps itself, runs the real grep,
# timestamps again, and appends one line. One line per worker.
set -u
case "${1:-}" in -h|--help)
  cat <<'HELP'
usage: pash-workers.sh [width] [dict-copies] [batch-bytes]

Runs one CPU-heavy grep pipeline under plain bash and under PaSh, checks both
give the same answer, and draws when each PaSh worker ran.

  width        number of parallel workers PaSh uses (PaSh's -w)       default 8
  dict-copies  how many copies of /usr/share/dict/words make up the
               input; each copy is ~663,000 lines, ~6.9 MB            default 2
  batch-bytes  size of each slice of input handed to a worker
               (PaSh's --r_split_batch_size). Slices are dealt to
               workers in turn, one grep process per slice            default 1000000

examples:
  pash-workers.sh                  8 workers, 2 copies, 1 MB slices
  pash-workers.sh 4 4              4 workers, 4 copies
  pash-workers.sh 8 2 250000       8 workers, 250 KB slices (more, shorter greps)
  pash-workers.sh 8 2 1730607      one slice per worker (input size / 8)
HELP
  exit 0;;
esac
WIDTH=${1:-8}
COPIES=${2:-2}
BATCH=${3:-1000000}
D=$(mktemp -d); trap 'rm -rf "$D"' EXIT; cd "$D" || exit 1

for _ in $(seq 1 "$COPIES"); do cat /usr/share/dict/words; done > in.txt
LINES=$(wc -l < in.txt); SIZE=$(du -h in.txt | cut -f1)

# Single quotes around the pattern are deliberate: PaSh returns the wrong answer
# when it parallelizes a double-quoted pattern.
cat > script.sh <<'SH'
cat in.txt | grep '\(.\).*\1\(.\).*\2\(.\).*\3\(.\).*\4' | wc -l
SH

mkdir -p shim
export PASH_WORKER_LOG="$D/workers.tsv"
cat > shim/grep <<'SHIM'
#!/bin/bash
s=$(date +%s.%N)
/usr/bin/grep "$@"; rc=$?
e=$(date +%s.%N)
printf '%s\t%s\t%s\n' "$$" "$s" "$e" >> "$PASH_WORKER_LOG"
exit $rc
SHIM
chmod +x shim/grep

: > "$PASH_WORKER_LOG"
b0=$(date +%s.%N); bash script.sh > bash.out 2>/dev/null; b1=$(date +%s.%N)
BASH_T=$(awk -v a="$b0" -v b="$b1" 'BEGIN{printf "%.4f", b-a}')

: > "$PASH_WORKER_LOG"
p0=$(date +%s.%N)
PATH="$D/shim:$PATH" "$PASH_TOP/pa.sh" -w "$WIDTH" --r_split_batch_size "$BATCH" -d 2 --log_file pash.log script.sh > pash.out 2>/dev/null
p1=$(date +%s.%N)
PASH_T=$(awk -v a="$p0" -v b="$p1" 'BEGIN{printf "%.4f", b-a}')

PAR=unknown
if [ -s pash.log ]; then
  if [ "$(grep -ciE 'r_split|r_merge' pash.log)" -gt 0 ] && ! grep -q "No region was parallelized" pash.log
    then PAR=yes; else PAR=no; fi
fi
NODES=$(grep -c "bash -c ' grep" pash.log 2>/dev/null || echo 0)

python3 - "$PASH_WORKER_LOG" "$PASH_T" "$BASH_T" "$WIDTH" "$LINES" "$SIZE" \
         "$(cat bash.out)" "$(cat pash.out)" "$PAR" "$NODES" "$BATCH" <<'PY'
import sys, os, statistics as st

log, wall, base, width, lines, size, bans, pans, par, nodes, batch = sys.argv[1:12]
wall=float(wall); base=float(base); width=int(width); lines=int(lines); nodes=int(nodes); batch=int(batch)

tty = sys.stdout.isatty() and not os.environ.get("NO_COLOR")
def c(code, s):
    return f"\033[{code}m{s}\033[0m" if tty else s
BOLD, DIM = "1", "2"
RED, GREEN, YELL, GREY = "38;5;167", "38;5;71", "38;5;179", "38;5;244"
WAVE = ["38;5;167", "38;5;109", "38;5;179", "38;5;139", "38;5;72", "38;5;180"]

try: TW = max(72, min(int(os.environ.get("COLUMNS") or os.get_terminal_size().columns), 100))
except Exception: TW = 80
IN = TW - 2                                   # inside the box frame

def rule(l, m, r, w=IN): return l + m*w + r
def row(text, pad=1, vis=None):
    v = vis if vis is not None else len(text)
    return "│" + " "*pad + text + " "*max(0, IN-v-pad) + "│"

BLOCKS = "▏▎▍▌▋▊▉█"
def bar(frac_start, frac_end, cells):
    """Horizontal bar between two 0..1 fractions, eighth-block precision."""
    a, b = frac_start*cells, frac_end*cells
    out = []
    for i in range(cells):
        cov = min(b, i+1) - max(a, i)
        if cov <= 0: out.append(" ")
        elif cov >= 0.999: out.append("█")
        else: out.append(BLOCKS[max(0, min(7, int(cov*8)-1))])
    return "".join(out)

print()
print(rule("┌","─","┐"))
title = "PaSh worker report"
bstr  = f"{batch/1e6:g} MB" if batch >= 1e6 else f"{batch/1e3:g} KB"
meta  = f"width {width}  ·  batch {bstr}  ·  {lines:,} lines  ·  {size}"
print("│ " + c(BOLD,title) + " "*(IN-1-len(title)-len(meta)-1) + c(DIM,meta) + " │")
print(rule("├","─","┤"))

# ── timings ──────────────────────────────────────────────────────────────────
lab = 7; numw = 10
track = IN - lab - numw - 4
slow = max(base, wall)
for name, t, col in (("bash", base, GREY), ("pash", wall, RED)):
    filled = bar(0, t/slow, track)
    extra = f"{t:7.3f}s"
    print("│ " + f"{name:<{lab}}" + c(col, filled) + "  " + c(BOLD, extra) + " "*(IN-lab-track-len(extra)-3) + "│")
speed = base/wall if wall else 0
verdict = f"{speed:.2f}× faster" if speed >= 1 else f"{1/speed:.2f}× slower"
print(row(" "*lab + c(BOLD if speed>=1 else DIM, verdict), vis=lab+len(verdict)))

ok = (bans == pans)
mark = c(GREEN,"✓") if ok else c(RED,"✗")
ansline = f"answer  {bans}" + ("  (same under both)" if ok else f"   ✗ pash said {pans}")
print(row(f"{mark} {ansline}", vis=2+len(ansline)))
pmark = c(GREEN,"✓") if par=="yes" else (c(RED,"✗") if par=="no" else c(YELL,"?"))
pline = f"parallelized  {par}   ·   {nodes} grep nodes compiled"
print(row(f"{pmark} {pline}", vis=2+len(pline)))

rows=[]
for line in open(log):
    p=line.split()
    if len(p)==3: rows.append((float(p[1]), float(p[2])))
if not rows:
    print(rule("└","─","┘")); print(); raise SystemExit

rows.sort()
t0=min(r[0] for r in rows); t1=max(r[1] for r in rows)
span=max(t1-t0, 1e-9)
ev=[]
for a,b in rows: ev += [(a,1),(b,-1)]
ev.sort(); cur=peak=0
for _,d in ev:
    cur+=d; peak=max(peak,cur)

print(rule("├","─","┤"))
hdr = f"{len(rows)} grep processes   ·   {peak} running at once   ·   {span:.3f}s of worker time"
print(row(c(BOLD,hdr), vis=len(hdr)))
if len(rows) > peak:
    note = f"in waves of {peak} — one grep process per {bstr} batch, dealt to workers in turn"
    print(row(c(DIM,note), vis=len(note)))
print(rule("├","─","┤"))

gl = 4; gnum = 9
gtrack = IN - gl - gnum - 4
for i,(s,e) in enumerate(rows, 1):
    col = WAVE[((i-1)//max(peak,1)) % len(WAVE)]
    g = bar((s-t0)/span, (e-t0)/span, gtrack)
    busy = f"{e-s:6.3f}s"
    print("│ " + c(DIM,f"{i:>{gl-1}} ") + c(col,g) + " " + c(DIM,busy) + " "*(IN-gl-gtrack-len(busy)-2) + "│")

# concurrency profile
SPARK="▁▂▃▄▅▆▇█"
prof=[]
for i in range(gtrack):
    t = t0 + span*(i+0.5)/gtrack
    n = sum(1 for s,e in rows if s <= t <= e)
    prof.append(SPARK[min(7, max(0, int(n/max(peak,1)*7.99)))] if n else " ")
print(rule("├","─","┤"))
print("│ " + c(DIM,f"{'busy':>{gl-1}} ") + c(YELL,"".join(prof)) + " " + c(DIM,f"{peak:>5} max") + " "*(IN-gl-gtrack-11) + "│")
tl = f"0s{' '*(gtrack-10)}{span:.2f}s"
print("│ " + " "*gl + c(DIM,tl) + " "*(IN-gl-len(tl)-1) + "│")

busy=[e-s for s,e in rows]; total=sum(busy)
print(rule("├","─","┤"))
for label, val in (
    ("per worker", f"min {min(busy):.3f}s   median {st.median(busy):.3f}s   max {max(busy):.3f}s"),
    ("summed",     f"{total:.3f}s of work compressed into {span:.3f}s of wall clock"),
    ("overlap",    f"{total/span:.2f}× of a possible {peak}×   =   {total/span/peak*100:.0f}% efficient"),
    ("overheads",  f"{wall-span:.3f}s startup and merge, outside the workers"),
):
    line = f"{label:<11}{val}"
    print(row(c(DIM,f"{label:<11}") + val, vis=len(line)))
print(rule("└","─","┘"))
print()
PY
