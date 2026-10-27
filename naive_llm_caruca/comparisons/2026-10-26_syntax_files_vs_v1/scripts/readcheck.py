"""Is a matcher 'full match' a correct reading of the line?

python -I readcheck.py PKG CMD CORPUS OUTJSONL

Truth: an emulation of GNU getopt_long (permuting; '--' ends options; long options may be
abbreviated to a unique prefix; required arguments attached or in the next word; optional
arguments only after '=') over the coreutils 9.4 option tables below.
Matcher reading: v1's caruca.oracle.oracle with every node's could_match instrumented, so each
consumed word is attributed to the grammar node that consumed it.
A reading is correct when it yields the same options (identity + value, as a multiset) and the
same operands in the same order as the truth.
"""
import importlib
import json
import shlex
import sys
from collections import Counter

sys.path.insert(0, "/Users/tirandagan/dev/stevens/caruca/caruca/src")
sys.path.insert(0, ".")

import caruca.ir.syntax as S  # noqa: E402
import caruca.oracle as O  # noqa: E402

# ---- coreutils 9.4 option tables: short letter -> kind ; long name -> (id, kind)
N, R, OPT = "none", "required", "optional"
TABLES = {
    "cut": (
        {"b": R, "c": R, "d": R, "f": R, "n": N, "s": N, "z": N},
        {"bytes": ("b", R), "characters": ("c", R), "delimiter": ("d", R), "fields": ("f", R),
         "only-delimited": ("s", N), "output-delimiter": ("output-delimiter", R),
         "complement": ("complement", N), "zero-terminated": ("z", N),
         "help": ("help", N), "version": ("version", N)},
    ),
    "sort": (
        {c: N for c in "bcCdfghimMnrRsuVz"} | {"k": R, "o": R, "S": R, "t": R, "T": R, "y": R},
        {"ignore-leading-blanks": ("b", N), "batch-size": ("batch-size", R), "check": ("c", OPT),
         "compress-program": ("compress-program", R), "debug": ("debug", N),
         "dictionary-order": ("d", N), "files0-from": ("files0-from", R),
         "general-numeric-sort": ("g", N), "human-numeric-sort": ("h", N), "ignore-case": ("f", N),
         "ignore-nonprinting": ("i", N), "key": ("k", R), "merge": ("m", N), "month-sort": ("M", N),
         "numeric-sort": ("n", N), "output": ("o", R), "parallel": ("parallel", R),
         "random-sort": ("R", N), "random-source": ("random-source", R), "reverse": ("r", N),
         "sort": ("sort", R), "stable": ("s", N), "buffer-size": ("S", R),
         "field-separator": ("t", R), "temporary-directory": ("T", R), "unique": ("u", N),
         "version-sort": ("V", N), "zero-terminated": ("z", N), "help": ("help", N),
         "version": ("version", N)},
    ),
    "rm": (
        {"d": N, "f": N, "i": N, "r": N, "R": N, "v": N, "I": N},
        {"force": ("f", N), "interactive": ("interactive", OPT), "one-file-system": ("one-file-system", N),
         "no-preserve-root": ("no-preserve-root", N), "preserve-root": ("preserve-root", OPT),
         "recursive": ("r", N), "dir": ("d", N), "verbose": ("v", N), "help": ("help", N),
         "version": ("version", N), "-presume-input-tty": ("presume-input-tty", N)},
    ),
}
SAME = {"rm": {"R": "r"}}  # -R is -r


def canon(cmd, oid, val):
    oid = SAME.get(cmd, {}).get(oid, oid)
    if cmd == "sort" and oid == "c" and val in ("quiet", "silent"):
        return ("C", None)
    if cmd == "sort" and oid == "c" and val == "diagnose-first":
        return ("c", None)
    if cmd == "sort" and oid == "y":
        return ("y", None)  # value ignored when all digits; compare as presence
    return (oid, val)


class Bad(Exception):
    pass


def truth(cmd, words):
    shorts, longs = TABLES[cmd]
    opts, operands, i = [], [], 0
    while i < len(words):
        t = words[i]
        if t == "--":
            operands += words[i + 1:]
            break
        if t.startswith("--"):
            name, eq, val = t[2:].partition("=")
            cands = [n for n in longs if n == name] or [n for n in longs if n.startswith(name)]
            if not cands or len({longs[n][0] for n in cands}) != 1:
                raise Bad(f"unrecognized/ambiguous {t}")
            oid, kind = longs[cands[0]]
            if kind == N:
                if eq:
                    raise Bad(f"{t} takes no argument")
                opts.append(canon(cmd, oid, None))
            elif kind == R:
                if not eq:
                    i += 1
                    if i >= len(words):
                        raise Bad(f"{t} needs an argument")
                    val = words[i]
                opts.append(canon(cmd, oid, val))
            else:
                opts.append(canon(cmd, oid, val if eq else None))
        elif t.startswith("-") and t != "-":
            j = 1
            while j < len(t):
                c = t[j]
                if c not in shorts:
                    raise Bad(f"invalid option -{c}")
                if shorts[c] == N:
                    opts.append(canon(cmd, c, None))
                    j += 1
                    continue
                rest = t[j + 1:]
                if not rest:
                    i += 1
                    if i >= len(words):
                        raise Bad(f"-{c} needs an argument")
                    rest = words[i]
                if cmd == "sort" and c == "y" and not rest.isdigit() and t == f"-{c}":
                    i -= 1  # sort puts a non-digit word after -y back
                opts.append(canon(cmd, c, rest))
                break
        else:
            operands.append(t)
        i += 1
    return sorted(opts, key=repr), operands


# ---- instrument the matcher
LOG = []


def wrap(cls):
    orig = cls.could_match

    def w(self, other):
        before = list(other)
        rem, strats = orig(self, other)
        if rem != before:
            LOG.append((self, before, list(rem), [type(s).__name__ for s in strats]))
        return rem, strats
    cls.could_match = w


wrap(S.Flag)
wrap(S.ValueArgument)


def spelling_to_id(cmd, sp):
    shorts, longs = TABLES[cmd]
    if sp.startswith("--"):
        name, _, val = sp[2:].partition("=")
        if name in longs:
            return longs[name][0], (val or None)
        return "UNKNOWN" + sp, None
    if sp.startswith("-") and len(sp) == 2 and sp[1] in shorts:
        return sp[1], None
    return "UNKNOWN" + sp, None


def matcher_reading(cmd):
    opts, operands = [], []
    for node, before, after, strats in LOG:
        removed = len(before) - len(after)
        if isinstance(node, S.Flag):
            oid, v = spelling_to_id(cmd, node.flag)
            if removed == 1 and before[0] in node.alias:
                oid, v = spelling_to_id(cmd, before[0])
            opts.append(canon(cmd, oid, v))
            continue
        if node.flag is None:
            operands += before[:removed]
            continue
        oid, _ = spelling_to_id(cmd, node.flag)
        tok = before[0]
        if node.flag_followed_by_equals:
            used = next(f for f in (node.flag, *node.alias) if tok.startswith(f))
            val = tok.removeprefix(used)
            val = val.removeprefix("=") if val.startswith("=") else val
            uid, uval = spelling_to_id(cmd, used)
            opts.append(canon(cmd, uid if not uid.startswith("UNKNOWN") else oid, val if val != "" else uval))
            continue
        vals = before[1:removed]
        if tok != node.flag and tok not in node.alias and tok.startswith(node.flag):
            vals = [tok[len(node.flag):]] + vals  # attached value (ShortFlagSplat)
        elif tok in node.alias:
            oid, _ = spelling_to_id(cmd, tok)
        val = " ".join(vals) if vals else None
        opts.append(canon(cmd, oid, val))
    return sorted(opts, key=repr), operands


pkg, cmd, corpus, outp = sys.argv[1:5]
real = O.get_syntax_spec
O.get_syntax_spec = lambda path, name: real(pkg, name)

stats = Counter()
with open(corpus) as f, open(outp, "w") as out:
    for line in f:
        line = line.strip()
        if not line or line.split()[0] != cmd:
            continue
        stats["lines"] += 1
        LOG.clear()
        remaining, strats = O.oracle(line)
        full = not remaining
        try:
            words = shlex.split(line)[1:]
        except ValueError:
            stats["unsplittable"] += 1
            out.write(json.dumps({"line": line, "full": full, "verdict": "unsplittable"}) + "\n")
            continue
        try:
            t = truth(cmd, words)
        except Bad as e:
            stats["invalid_for_binary"] += 1
            stats["invalid_for_binary_full"] += full
            out.write(json.dumps({"line": line, "full": full, "verdict": "invalid", "why": str(e)}) + "\n")
            continue
        stats["valid"] += 1
        if not full:
            stats["valid_not_full"] += 1
            verdict = "not_read"
            m = None
        else:
            m = matcher_reading(cmd)
            verdict = "correct" if m == t else "wrong"
            stats["valid_full_" + verdict] += 1
        out.write(json.dumps({"line": line, "full": full, "verdict": verdict, "truth": t, "read": m}) + "\n")
print(pkg, cmd, dict(stats))
