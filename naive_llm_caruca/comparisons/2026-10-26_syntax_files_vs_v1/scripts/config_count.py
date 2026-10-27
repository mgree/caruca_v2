"""Exact count of what v1 would trace for a grammar at max-count k, without listing the lines.

v1's generator picks exactly k optional entries per combination (CommandSpecification.__filtered_args);
each chosen entry contributes its variations, including "absent". So the number of command lines is
the k-th elementary symmetric sum of the per-entry variation counts, times the required entries'
counts. Each line is then traced once per combination of its arguments' file situations and per
stdin variant (CommandInvocation.to_exec_env), so configurations use per-entry weights
W = sum over the entry's variations of the number of file situations. Defaults: max-arity 1,
plain relations, --stdin simple, --content simple.

python -I config_count.py PKG CMD K...
"""
import importlib
import sys

sys.path.insert(0, "/Users/tirandagan/dev/stevens/caruca/caruca/src")
sys.path.insert(0, ".")

import caruca.ir.syntax as S  # noqa: E402
from caruca.ir.contents import Content  # noqa: E402
import caruca.ir.string as Str  # noqa: E402

S.Argument.max_repetition = 1
S.Argument.elaborate_relations = False
Str.RawArgument.content_variation = "simple"
STDINS = len(Content.variation("simple"))

pkg, cmd, *ks = sys.argv[1:]
spec = getattr(importlib.import_module(f"{pkg}.{cmd}"), f"{cmd}_syntax_spec")


def weights(node):
    lines = configs = 0
    for seq in node.syntax_variation():
        lines += 1
        configs += len(list(seq.environment_variation())) if seq.args else 1
    return lines, configs


def esym(values, k):
    e = [1] + [0] * k
    for v in values:
        for j in range(k, 0, -1):
            e[j] += e[j - 1] * v
    return e[k]


for k in map(int, ks):
    tot_lines = tot_cfg = 0
    for syntax in spec:
        opt_l, opt_c, req_l, req_c = [], [], 1, 1
        for pos in syntax:
            for n in pos:
                l, c = weights(n)
                if n.is_optional():
                    opt_l.append(l); opt_c.append(c)
                else:
                    req_l *= l; req_c *= c
        kk = min(k, len(opt_l))
        tot_lines += req_l * esym(opt_l, kk)
        tot_cfg += req_c * esym(opt_c, kk) * STDINS
    print(f"{pkg} {cmd} k={k}: command lines {tot_lines:,}  traced configurations {tot_cfg:,}")
