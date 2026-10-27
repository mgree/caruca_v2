"""Three-way alignment of normalized grammars (ref, model, agent).

python3 compare.py CMD [--plusminus]   (reads out/CMD.json)
Options are grouped when their spellings overlap. With --plusminus (convert),
'+name' and '-name' are grouped under one base name.
"""
import json
import sys

cmd = sys.argv[1]
pm = "--plusminus" in sys.argv
D = json.load(open(f"out/{cmd}.json"))
G = ["g_ref", "g_model", "g_agent"]
LABEL = {"g_ref": "reference", "g_model": "v1 model", "g_agent": "agent"}


def spellings(n):
    s = {n["flag"], *n["alias"]} if n["flag"] else set()
    if pm:
        s = {x.lstrip("+-") for x in s}
    return s


groups = []  # list of (spellingset, {g: [nodes]})
operands = {g: [] for g in G}
for g in G:
    for n in D[g]["nodes"]:
        if not n["flag"]:
            operands[g].append(n)
            continue
        sp = spellings(n)
        hit = [grp for grp in groups if grp[0] & sp]
        if hit:
            base = hit[0]
            for other in hit[1:]:
                base[0].update(other[0])
                for k, v in other[1].items():
                    base[1].setdefault(k, []).extend(v)
                groups.remove(other)
            base[0].update(sp)
            base[1].setdefault(g, []).append(n)
        else:
            groups.append((set(sp), {g: [n]}))


def summarize(nodes):
    """collapse the agent's per-syntax copies of one option"""
    if not nodes:
        return None
    out = []
    seen = set()
    for n in nodes:
        key = json.dumps({k: v for k, v in n.items() if k not in ("syntax",)}, sort_keys=True)
        if key in seen:
            continue
        seen.add(key)
        out.append(n)
    return out


def short(n):
    if n is None:
        return "—"
    bits = [n["type"]]
    if n["flag"]:
        bits.append(n["flag"])
    if n["alias"]:
        bits.append("alias=" + ",".join(n["alias"]))
    if n["equals"]:
        bits.append("=")
    if n["arity"] != "OPTIONAL":
        bits.append(n["arity"])
    if n["type"] in ("Selection", "String", "List") and "choices" in n and n["choices"] != ["string"]:
        bits.append("choices=" + "|".join(map(str, n["choices"])))
    if n.get("dash_as_stdin"):
        bits.append("dash")
    if "min" in n and (n["min"], n["max"]) != (-1, 1):
        bits.append(f"min={n['min']},max={n['max']}(n={n['n_values']})")
    return " ".join(bits)


rows = []
for sp, per in groups:
    rec = {g: summarize(per.get(g, [])) for g in G}
    rows.append((sorted(sp, key=lambda x: (len(x), x)), rec))

presence = {}
for sp, rec in rows:
    key = tuple(bool(rec[g]) for g in G)
    presence.setdefault(key, []).append(sp[0])

print(f"## {cmd}: {len(rows)} option groups")
for key, names in sorted(presence.items(), key=lambda kv: -len(kv[1])):
    who = "+".join(LABEL[g] for g, k in zip(G, key) if k)
    print(f"  present in {who}: {len(names)}")
    if len(names) <= 40 and key != (True, True, True):
        print("     ", " ".join(names))

ATTRS = ["type", "equals", "alias", "arity", "choices", "dash_as_stdin", "min", "max"]
diffs = {a: [] for a in ATTRS}
for sp, rec in rows:
    if not all(rec[g] for g in G):
        continue
    first = {g: rec[g][0] for g in G}
    for a in ATTRS:
        vals = [first[g].get(a) for g in G]
        if a == "alias" and pm:
            vals = [sorted(x.lstrip("+-") for x in v) if v else v for v in vals]
        if a == "choices":
            vals = [sorted(map(str, v)) if v is not None else None for v in vals]
        if len({json.dumps(v) for v in vals}) > 1:
            diffs[a].append((sp[0], vals))
print("\n  attribute disagreements among options present in all three:")
for a in ATTRS:
    print(f"    {a}: {len(diffs[a])}")

if "--full" in sys.argv:
    print("\n| spellings | reference | v1 model | agent |\n|---|---|---|---|")
    for sp, rec in rows:
        cells = []
        for g in G:
            ns = rec[g]
            cells.append("<br>".join(short(n) for n in ns) if ns else "—")
        print(f"| {' '.join(sp)} | " + " | ".join(cells) + " |")
    print("\noperands:")
    for g in G:
        print(" ", LABEL[g], [short(n) + f" (syntax {n['syntax']})" for n in operands[g]])

if "--diffs" in sys.argv:
    for a in ATTRS:
        if diffs[a]:
            print(f"\n### {a}")
            for name, vals in diffs[a]:
                print(f"  {name}: " + " | ".join(f"{LABEL[g]}={v}" for g, v in zip(G, vals)))
