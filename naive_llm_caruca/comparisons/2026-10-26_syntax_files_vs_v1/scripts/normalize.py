"""Load each grammar through v1's DSL and emit a normalized option table.

Run with v1's venv python -I from the specs/ scratch folder:
  python -I normalize.py CMD  -> JSON on stdout
"""
import importlib
import json
import sys

sys.path.insert(0, "/Users/tirandagan/dev/stevens/caruca/caruca/src")
sys.path.insert(0, ".")

import caruca.ir.syntax as S  # noqa: E402

# reverse map: class object -> all DSL names bound to it
NAMES = {}
for name in dir(S):
    obj = getattr(S, name)
    if isinstance(obj, type) and issubclass(obj, S.Argument) and name not in (
        "Argument", "ValueArgument"):
        NAMES.setdefault(obj, []).append(name)

CANON = {
    # preferred display name for classes with several names
}


def tname(node):
    names = NAMES.get(type(node), [type(node).__name__])
    # prefer the name that is not a plain synonym of a more specific one
    for pref in ("Integer", "String", "Path", "Selection", "Flag", "List", "Char", "Range",
                 "Geometry", "Size", "Delimiter", "Command", "Date", "Regex"):
        if pref in names:
            return pref, sorted(names)
    return sorted(names)[0], sorted(names)


def node_rec(node, syn, pos):
    t, syn_names = tname(node)
    rec = {
        "syntax": syn, "position": pos, "type": t, "type_synonyms": syn_names,
        "flag": node.flag, "alias": list(node.alias),
        "equals": node.flag_followed_by_equals,
        "arity": node.arity.name if hasattr(node.arity, "name") else node.arity,
    }
    if hasattr(node, "choices"):
        rec["choices"] = list(node.choices) if not isinstance(node.choices, str) else [node.choices]
    if hasattr(node, "dash_as_stdin"):
        rec["dash_as_stdin"] = node.dash_as_stdin
    if isinstance(node, S.Integer):
        rec["min"], rec["max"] = node.min, node.max
        rec["n_values"] = len(range(node.min, node.max + 1))
    return rec


def load(pkg, cmd):
    mod = importlib.import_module(f"{pkg}.{cmd}")
    spec = getattr(mod, f"{cmd}_syntax_spec")
    out = []
    for si, syntax in enumerate(spec):
        for pi, pos in enumerate(syntax):
            for node in pos:
                out.append(node_rec(node, si, pi))
    return {"n_syntaxes": len(spec), "positions": [len(s) for s in spec], "nodes": out}


if __name__ == "__main__":
    cmd = sys.argv[1]
    res = {}
    for pkg in ("g_ref", "g_model", "g_agent", "g_pash"):
        res[pkg] = load(pkg, cmd)
    print(json.dumps(res, indent=1))
