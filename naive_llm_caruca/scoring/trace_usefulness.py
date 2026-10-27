#!/usr/bin/env python3
"""Generator usefulness: trace the command lines v1 generates from one syntax file, and count how many
the command accepts (exit status 0) and how many do real work (accepted, and not cut short by --help or
--version). v1's annotator drops failed runs before it classifies anything, so a run that fails here
contributes nothing to v1's specification.

v1's `caruca trace` command cannot do this itself: it ignores `--path` (it reads only the default,
`--pash` or `--posh` specifications) and its `--length-only` count ignores `--max-count`. So this calls
v1's own `string_invocations` and `Tracer` directly, with the CLI's defaults except `max_count`.
Runs inside the `caruca` Lima VM, from a scratch folder (the tracer writes `tracer.log` into the
current folder, and v1's checkout must not be touched):

    cd $(mktemp -d) && ~/caruca-venv/bin/python -I <repo>/naive_llm_caruca/scoring/trace_usefulness.py \
        CMD SYNTAX_FILE LABEL > usefulness.json
"""
import json, os, shutil, subprocess, sys, tempfile, time
from pathlib import Path

CMD, SPEC, LABEL = sys.argv[1], Path(sys.argv[2]), sys.argv[3]
MAX_COUNT, LIMIT = 1, int(os.environ.get("LIMIT", "4000"))
SKIP = os.environ.get("SKIP") or None  # v1's own skip list (comma-separated flags), for oversized files
V1_SRC = Path("/Users/tirandagan/dev/stevens/caruca/caruca/src")
sys.path.insert(0, str(V1_SRC))

scratch = Path(tempfile.mkdtemp(prefix="t018trace."))
(scratch / "t018spec").mkdir()
(scratch / "t018spec" / "__init__.py").write_text("")
shutil.copy(SPEC, scratch / "t018spec" / f"{CMD}.py")
sys.path.insert(0, str(scratch))

from caruca.cli.generate import string_invocations  # noqa: E402
from caruca.tracer.tracer import Tracer  # noqa: E402

# the CLI's defaults: no skip list, max_arity 1, no elaborate relations, parallel 10, simple stdin and content
invocations = list(string_invocations(CMD, "t018spec", SKIP, 1, False, MAX_COUNT))
rec = {"command": CMD, "syntax_file": str(SPEC), "label": LABEL, "skip": SKIP,
       "settings": f"max_count {MAX_COUNT}, max_arity 1, stdin simple, content simple, parallel 10"
                   + (f", skipping {SKIP}" if SKIP else ""),
       "coreutils": subprocess.run(["dpkg-query", "-W", "-f=${Version}", "coreutils"],
                                   capture_output=True, text=True).stdout,
       "invocations": len(invocations), "limit": LIMIT, "traced": False}

if len(invocations) <= LIMIT:
    start = time.time()
    traces = Tracer(10, "simple", "simple", "").run(invocations)
    rec["seconds"] = round(time.time() - start)
    # one trace set per generated command line; one traced run per test environment inside it.
    # A line is accepted when at least one of its runs exits 0 (v1 keeps the successful runs).
    lines, ok, work, why = set(), set(), set(), {}
    runs = runs_ok = 0
    for s in traces:
        line = s.true_str
        lines.add(line)
        codes = [c.return_code for c in s.configs]
        runs += len(codes)
        runs_ok += sum(rc == 0 for rc in codes)
        if 0 in codes:
            ok.add(line)
            if not {"--help", "--version"} & set(line.split()):
                work.add(line)
        elif line not in why and s.configs:
            why[line] = (s.configs[0].stderr or "").strip().splitlines()[:1]
    rec.update({"traced": True, "runs": runs, "runs_accepted": runs_ok,
                "distinct_lines": len(lines), "distinct_accepted": len(ok), "distinct_real_work": len(work),
                "sample_rejected": [[l, why.get(l)] for l in sorted(lines - ok)[:15]]})

shutil.rmtree(scratch, ignore_errors=True)
json.dump(rec, sys.stdout, indent=1, default=str)
