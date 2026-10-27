"""Run v1's real-world matcher (caruca.oracle.oracle) with a chosen grammar package.

python -I oracle_run.py PKG CMD CORPUS OUTJSONL
Only corpus lines whose first word is CMD are used (v1's per-command counts group by first word).
"""
import importlib
import json
import sys

sys.path.insert(0, "/Users/tirandagan/dev/stevens/caruca/caruca/src")
sys.path.insert(0, ".")

import caruca.oracle as O  # noqa: E402

pkg, cmd, corpus, outp = sys.argv[1:5]
real = O.get_syntax_spec
if pkg != "default":
    O.get_syntax_spec = lambda path, name: real(pkg, name)

n = full = 0
with open(corpus) as f, open(outp, "w") as out:
    for line in f:
        line = line.strip()
        if not line or line.split()[0] != cmd:
            continue
        n += 1
        remaining, strats = O.oracle(line)
        names = sorted({type(s).__name__ for s in strats})
        ok = not remaining
        full += ok
        out.write(json.dumps({"line": line, "full": ok, "strats": names, "remaining": remaining}) + "\n")
print(pkg, cmd, n, full)
