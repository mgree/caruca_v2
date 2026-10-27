"""Render every option of every grammar exactly as v1's generator writes it (max-arity 1, simple relations).
python -I render.py  -> out/forms.json"""
import importlib, json, sys
sys.path.insert(0, "/Users/tirandagan/dev/stevens/caruca/caruca/src"); sys.path.insert(0, ".")
import caruca.ir.syntax as S
S.Argument.max_repetition = 1
S.Argument.elaborate_relations = False
out = []
for cmd in ["rm", "cut", "sort", "convert"]:
    for pkg in ["g_ref", "g_model", "g_agent"]:
        spec = getattr(importlib.import_module(f"{pkg}.{cmd}"), f"{cmd}_syntax_spec")
        seen = set()
        for si, syntax in enumerate(spec):
            for pos in syntax:
                for n in pos:
                    if not n.flag or n.flag in seen: continue
                    seen.add(n.flag)
                    S.Path._counter = 1
                    forms = [str(seq) for seq in n.syntax_variation() if seq.args]
                    out.append({"cmd": cmd, "g": pkg, "opt": n.flag, "type": type(n).__name__ if type(n).__name__ != "_String" else "meta",
                                "n_forms": len(forms), "forms": forms})
json.dump(out, open("out/forms.json", "w"), indent=0)
from collections import Counter
print(Counter((o["cmd"], o["g"]) for o in out))
print(sum(len(o["forms"]) for o in out), "forms")
for o in out:
    if o["cmd"] in ("cut", "sort", "rm") and o["g"] == "g_agent": print(o["opt"], o["forms"])
print([o for o in out if o["n_forms"] == 0])
