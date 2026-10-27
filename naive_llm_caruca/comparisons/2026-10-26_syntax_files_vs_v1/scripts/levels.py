import json, sys
LEVELS = [  # (name, excluded strategy classes) -- as in v1 eval/user-scripts/completeness_accumulate.sh
 ("no_assumption (script, typo keeps ShortFlagSplat)", {"DefaultArg","PathAgnosticism","ArityStrategy","IntAgnosticism","StringAgnosticism"}),
 ("no_assumption (corrected)", {"ShortFlagSplat","DefaultArg","PathAgnosticism","ArityStrategy","IntAgnosticism","StringAgnosticism"}),
 ("flag_match", {"PathAgnosticism","ArityStrategy","IntAgnosticism","StringAgnosticism"}),
 ("path_match", {"ArityStrategy","StringAgnosticism","IntAgnosticism"}),
 ("int_match", {"ArityStrategy","StringAgnosticism"}),
 ("string_match", {"ArityStrategy"}),
 ("all (full match, any strategy)", set()),
]
for c in ["rm","sort","cut"]:
    print(f"== {c}")
    print(f"{'level':52s}" + "".join(f"{p:>10s}" for p in ["g_ref","g_model","g_agent"]))
    data = {p:[json.loads(l) for l in open(f"out/oracle/{p}_{c}.jsonl")] for p in ["g_ref","g_model","g_agent"]}
    n = len(data["g_ref"])
    print(f"{'corpus lines':52s}" + "".join(f"{len(data[p]):>10d}" for p in data))
    for name, ex in LEVELS:
        print(f"{name:52s}" + "".join(f"{sum(1 for r in data[p] if r['full'] and not (set(r['strats'])&ex)):>10d}" for p in data))
    # strategy usage among full matches
    for p in data:
        from collections import Counter
        cnt = Counter(s for r in data[p] if r['full'] for s in r['strats'])
        print("   ", p, "strategies in full matches:", dict(cnt.most_common()))
