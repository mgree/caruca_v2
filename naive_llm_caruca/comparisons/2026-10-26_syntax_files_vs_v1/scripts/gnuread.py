"""Read the corpus with GNU getopt_long rules, but with the option table taken from a grammar.
python -I gnuread.py PKG CMD CORPUS
Separates what a grammar knows (spellings, takes-a-value or not) from how v1's matcher uses it."""
import importlib, json, shlex, sys
from collections import Counter
sys.path.insert(0, "/Users/tirandagan/dev/stevens/caruca/caruca/src"); sys.path.insert(0, ".")
import caruca.ir.syntax as S
import readcheck_lib as RC   # truth tables + parser, imported without running main

pkg, cmd, corpus = sys.argv[1:4]
spec = getattr(importlib.import_module(f"{pkg}.{cmd}"), f"{cmd}_syntax_spec")
real_shorts, real_longs = RC.TABLES[cmd]
shorts, longs = {}, {}
for syntax in spec:
    for pos in syntax:
        for n in pos:
            if not n.flag: continue
            kind = RC.N if isinstance(n, S.Flag) else RC.R
            if isinstance(n, S.Selection) and "" in n.choices: kind = RC.OPT
            for sp in (n.flag, *n.alias):
                if sp.startswith("--"):
                    name, eq, val = sp[2:].partition("=")
                    # map to the real id so identities are comparable
                    rid = real_longs.get(name, ("UNKNOWN--"+name,))[0]
                    if eq:   # e.g. alias "--check=quiet": an optional-argument long option
                        longs[name] = (rid, RC.OPT); continue
                    longs[name] = (rid, RC.OPT if name in longs and longs[name][1] == RC.OPT else kind)
                elif sp.startswith("-") and len(sp) == 2:
                    shorts[sp[1]] = kind
RC.TABLES = {cmd: (shorts, longs)}
st = Counter()
for line in open(corpus):
    line = line.strip()
    if not line or line.split()[0] != cmd: continue
    try: words = shlex.split(line)[1:]
    except ValueError: continue
    RC.TABLES[cmd] = (real_shorts, real_longs)
    try: t = RC.truth(cmd, words)
    except RC.Bad: continue
    st["valid"] += 1
    RC.TABLES[cmd] = (shorts, longs)
    try: g = RC.truth(cmd, words)
    except RC.Bad as e:
        st["not_read"] += 1; st["why:" + str(e).split()[-1]] += 1; continue
    st["correct" if g == t else "wrong"] += 1
print(pkg, cmd, {k: v for k, v in st.most_common() if not k.startswith("why")}, "| top unreadable:", [(k[4:], v) for k, v in st.most_common() if k.startswith("why")][:6])
