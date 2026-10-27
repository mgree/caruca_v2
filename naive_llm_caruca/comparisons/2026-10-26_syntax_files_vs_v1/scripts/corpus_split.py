"""Whole corpus, v1's own grammars: which full matches depend on taking a word as an option it is not?
A StringAgnosticism whose matched_with is an option spelling (starts with '-' or '+') comes from the
flag-position branch of ValueArgument.__flag_match (ir/syntax.py): the word was not the option's spelling,
not an alias, and did not start with the spelling. One whose matched_with is a value list comes from
String._value_match (a value outside the sample values) -- the case the paper describes."""
import json, sys
from collections import Counter
sys.path.insert(0, "/Users/tirandagan/dev/stevens/caruca/caruca/src")
import caruca.oracle as O
st = Counter(); per = Counter()
for line in open(sys.argv[1]):
    line = line.strip()
    if not line: continue
    st["lines"] += 1
    rem, strats = O.oracle(line)
    if rem: continue
    st["full"] += 1
    names = {type(s).__name__ for s in strats}
    flagpos = any(type(s).__name__ == "StringAgnosticism" and str(s.matched_with)[:1] in "-+" for s in strats)
    valpos = any(type(s).__name__ == "StringAgnosticism" and str(s.matched_with)[:1] not in "-+" for s in strats)
    if "ArityStrategy" not in names:
        st["full_without_arity"] += 1
        if "StringAgnosticism" not in names: st["full_without_arity_string"] += 1
        if flagpos: st["full_without_arity_flagpos"] += 1
        elif valpos: st["full_without_arity_valpos_only"] += 1
    if flagpos:
        st["full_flagpos"] += 1; per[line.split()[0]] += 1
print(json.dumps(dict(st)), json.dumps(per.most_common(25)))
