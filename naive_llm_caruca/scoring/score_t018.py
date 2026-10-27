#!/usr/bin/env python3
"""Task 018: grade every syntax file for a command, and tabulate.

For each command, the syntax files are: Caruca's reference (the answer key), Caruca's shipped GPT-4o
output, and every naive-agent run of it (PROMPT_v1, claude-fable-5-1). Each file gets, never blended:

  Headline   program-checked accuracy: facts the file gets right / all facts, every fact settled by
             running the program (facts.py; fact types a to h)
  Fit with v1's current programs
    reach    real command lines read: by GNU's own option rules where the other session's reader has
             the command's option table (comparisons/2026-10-26_syntax_files_vs_v1/scripts/gnuread.py),
             else by this file's strict reader; and by v1's own matcher (reach.py), which accepts any
             word as any value-taking option (task 018, section 4.2)
    generator  distinct command lines v1 generates from it that do real work (trace_usefulness.py)
  Paper-comparable  agreement with Caruca's reference (caruca_v2's structural scorer and v1's own
             cmp_specs.py, whose blind spots are listed in task 018, section 4.4)
  Performance  for agent files, the run's own time, cost, turns and tool calls

Run from the repo root with caruca_v2's interpreter; the VMs `t018-probe` and `caruca` must be running:

    .venv/bin/python naive_llm_caruca/scoring/score_t018.py CMD [CMD ...]      # score, then tabulate
    .venv/bin/python naive_llm_caruca/scoring/score_t018.py --table            # tabulate only

Writes naive_llm_caruca/scoring/results/<cmd>.json and results/summary.md.
"""
import ast, json, shlex, shutil, subprocess, sys, tempfile, time
from collections import Counter
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from caruca_v2 import v1  # noqa: E402
from caruca_v2.harness.score import score_spec  # noqa: E402
from facts import program_facts  # noqa: E402

V1 = Path.home() / "dev/stevens/caruca"
V1_PY = V1 / "caruca/.venv/bin/python"
CORPUS = V1 / "eval/user-scripts/invocations.txt"
HERE = REPO / "naive_llm_caruca/scoring"
GNUREAD = REPO / "naive_llm_caruca/comparisons/2026-10-26_syntax_files_vs_v1/scripts"
GNU_TABLES = {"cut", "sort", "rm"}  # commands gnuread's coreutils 9.4 option tables cover
RESULTS = HERE / "results"
PROBE_VM, TRACE_VM = "t018-probe", "caruca"
# a file whose generator output is too large to trace is traced again with v1's own skip list
SKIP_IF_TOO_MANY = {"binwalk": "-s"}


def sources(cmd):
    out = {"reference": V1 / f"caruca/src/caruca/syntax_specs/{cmd}.py",
           "gpt-4o (shipped)": V1 / f"outputs/llm-dsl-generation/{cmd}.py"}
    for run in sorted((REPO / "naive_llm_caruca/runs").glob(f"*_{cmd}_PROMPT_v1")):
        env = dict(l.split("=", 1) for l in (run / "run.env").read_text().splitlines() if "=" in l)
        spec = run / "output" / f"{cmd}.py"
        if env.get("model") == "claude-fable-5-1" and env.get("command") == cmd and spec.is_file():
            out[f"agent {run.name[:17]}"] = spec
    return {k: v for k, v in out.items() if v.is_file()}


def sh(argv, **kw):
    return subprocess.run(argv, capture_output=True, text=True, **kw)


# ---- paper-comparable: agreement with Caruca's reference -------------------------------------------

def answer_key(cmd, path):
    rec = {}
    for ref in ("v1-specs", "ground-truth"):
        try:
            r = score_spec(cmd, path, reference=ref, with_cmp_specs=(ref == "v1-specs"))
        except Exception as exc:  # the hand-annotated lists cover 108 of the 120 commands
            rec[ref] = {"error": f"{type(exc).__name__}: {exc}"}
            continue
        keep = {k: r.get(k) for k in ("scoreable", "counts", "agreement", "precision", "recall", "f1",
                                       "exact_argument_rate", "missing_surfaces", "spurious_surfaces")}
        if r.get("cmp_specs"):
            c = r["cmp_specs"]
            keep["cmp_specs"] = {"diff_count": c.get("diff_count"), "exact": c.get("diff_count") == 0,
                                 "error": c.get("error")}
        rec[ref] = keep
    return rec


# ---- facts a, b, c: the binary probe -----------------------------------------------------------------

def flag_entries(path, cmd):
    inv = v1.dump_spec_inventory(cmd, path)
    return [e for e in inv.entries if e.get("flag")] if inv.ok else None


def probe(cmd, files):
    spellings = set()
    for path in files.values():
        for e in flag_entries(path, cmd) or []:
            spellings.update([e["flag"], *e["alias"]])
    with tempfile.TemporaryDirectory() as tmp:
        cand = Path(tmp) / "candidates.json"
        cand.write_text(json.dumps({"spellings": sorted(spellings)}))
        sh(["limactl", "copy", str(cand), f"{PROBE_VM}:/tmp/t018_candidates.json"], check=True)
        sh(["limactl", "copy", str(HERE / "probe_binary.py"), f"{PROBE_VM}:/tmp/t018_probe.py"], check=True)
        p = sh(["limactl", "shell", PROBE_VM, "--", "python3", "/tmp/t018_probe.py", cmd, "/tmp/t018_candidates.json"])
    if p.returncode:
        raise RuntimeError(f"probe failed for {cmd}: {p.stderr[-800:]}")
    return json.loads(p.stdout)


def binary_score(entries, probed):
    if entries is None:
        return {"error": "the file does not load under v1's syntax module"}
    sp = probed["spellings"]

    def name(s):  # "--check=silent" written as a spelling names the option --check with a value
        return s.split("=", 1)[0] if s.startswith("--") else s

    real = {name(s) for s, v in sp.items() if v["accepted"]}
    surfaces = [(s, e) for e in entries for s in [e["flag"], *e["alias"]]]
    accepted = [(s, e) for s, e in surfaces if sp.get(s, {}).get("accepted")]
    # one verdict per spelling: a file may list the same option in several alternative syntaxes
    file_says = {}
    for s, e in accepted:
        file_says.setdefault(s, set()).add(bool(e["takes_value"]))
    value_checked, value_agree, optional = len(file_says), 0, 0
    disagree = []
    for s, says in sorted(file_says.items()):
        binary_value = sp[s]["value"]
        if binary_value == "optional":
            optional += 1
            value_agree += 1
        elif says == {binary_value == "required"}:
            value_agree += 1
        else:
            file_text = " and ".join("takes a value" if v else "no value" for v in sorted(says))
            disagree.append([s, f"file: {file_text}", f"binary: {binary_value}"])
    choices = []
    for s, e in accepted:
        listed = sp[s].get("valid_values") or []
        if e.get("choices") and listed:
            choices.append({"spelling": s, "file": e["choices"], "binary": listed,
                            "binary_values_in_file": len(set(listed) & set(e["choices"]))})
    in_file = {name(s) for s, _ in surfaces}
    return {
        "spellings_in_file": len({s for s, _ in surfaces}),
        "spellings_accepted": len({s for s, _ in accepted}),
        "spellings_rejected": sorted({s for s, _ in surfaces if sp.get(s, {}).get("accepted") is False}),
        "value_checked": value_checked, "value_agree": value_agree, "value_optional_in_binary": optional,
        "value_disagreements": disagree,
        "real_spellings_all_sources": len(real),
        "real_spellings_in_file": len(real & in_file),
        "real_spellings_missing": sorted(real - in_file),
        "choice_lists": choices,
    }


# ---- fit with v1's programs: real-world reading ------------------------------------------------------

_CORPUS_LINES = None


def corpus_lines(cmd):
    global _CORPUS_LINES
    if _CORPUS_LINES is None:
        _CORPUS_LINES = [l.strip() for l in CORPUS.read_text(errors="replace").splitlines()]
    return [l for l in _CORPUS_LINES if l.split(maxsplit=1)[:1] == [cmd]]


def strict_reach(cmd, entries):
    """Real lines in which every option word is an option the syntax file names.

    Independent of v1's matcher, which accepts any word as the flag of any value-taking option.
    Words are read as GNU getopt reads them: `--name` or a unique prefix of one, with its value after
    `=` or (if the option takes one) in the next word; `-abc` as a cluster of short options, where an
    option that takes a value takes the rest of the word or the next word; `--` ends the options.
    For dd-style syntax files (option names without a dash), a `key=value` word must use a listed key.
    Used where the GNU-rules reader has no option table for the command.
    """
    if entries is None:
        return {"error": "the file does not load under v1's syntax module"}
    # spelling -> "none", "attached" (value only after =) or "next" (value attached or in the next word);
    # where entries disagree, the most permissive reading wins
    rank = {"none": 0, "attached": 1, "next": 2}
    mode = {}
    for e in entries:
        for s in [e["flag"], *e["alias"]]:
            name = s.split("=", 1)[0] if s.startswith("--") else s
            m = "none" if not e["takes_value"] else ("attached" if e["flag_followed_by_equals"] else "next")
            if name not in mode or rank[m] > rank[mode[name]]:
                mode[name] = m
    longs = [s for s in mode if s.startswith("--")]
    words_keys = {s for s in mode if not s.startswith("-")}

    def long_match(name):
        if name in mode:
            return name
        hits = [s for s in longs if s.startswith(name)]
        return hits[0] if len(hits) == 1 else None

    def recognised(line):
        words = shlex.split(line)[1:]
        i = 0
        while i < len(words):
            w = words[i]
            if w == "--":
                return True, None
            if w.startswith("--") and len(w) > 2:
                name, eq, _ = w.partition("=")
                hit = long_match(name)
                if hit is None:
                    return False, w
                if mode[hit] == "next" and not eq:
                    i += 1
            elif w.startswith("-") and len(w) > 1:
                if w in mode:  # a spelling listed whole, e.g. -NUM forms
                    if mode[w] == "next":
                        i += 1
                else:
                    for j, ch in enumerate(w[1:], start=1):
                        sp = "-" + ch
                        if sp not in mode:
                            return False, w
                        if mode[sp] != "none":
                            if j == len(w) - 1 and mode[sp] == "next":
                                i += 1
                            break
            elif words_keys and "=" in w and w.split("=", 1)[0] not in words_keys:
                return False, w
            i += 1
        return True, None

    lines = corpus_lines(cmd)
    ok = unparseable = 0
    unknown = Counter()
    for line in lines:
        try:
            good, word = recognised(line)
        except ValueError:
            unparseable += 1
            continue
        if good:
            ok += 1
        else:
            unknown[word] += 1
    return {"invocations": len(lines), "read": ok, "unparseable": unparseable,
            "top_unrecognised_words": unknown.most_common(10)}


def gnu_read(cmd, path):
    """The other session's reader: every valid line (one GNU itself accepts) read with GNU's own rules,
    the option table taken from the syntax file, compared word by word with the real table."""
    with tempfile.TemporaryDirectory() as tmp:
        pkg = Path(tmp) / "t018gp"
        pkg.mkdir()
        (pkg / "__init__.py").write_text("")
        shutil.copy(path, pkg / f"{cmd}.py")
        for script in ("gnuread.py", "readcheck_lib.py"):
            shutil.copy(GNUREAD / script, Path(tmp) / script)
        p = sh([str(V1_PY), "-I", "gnuread.py", "t018gp", cmd, str(CORPUS)], cwd=tmp)
    if p.returncode:
        return {"error": p.stderr[-600:]}
    line = p.stdout.strip().splitlines()[-1]
    counts = ast.literal_eval(line.split(" ", 2)[2].split(" | ")[0])
    top = ast.literal_eval(line.split("| top unreadable: ")[1])
    return {"valid_lines": counts.get("valid", 0), "read_correctly": counts.get("correct", 0),
            "read_wrongly": counts.get("wrong", 0), "not_read": counts.get("not_read", 0), "top_unreadable": top}


def reach(cmd, path, entries):
    with tempfile.TemporaryDirectory() as tmp:
        p = sh([str(V1_PY), "-I", str(HERE / "reach.py"), cmd, str(path), str(CORPUS)], cwd=tmp)
    if p.returncode:
        return {"error": p.stderr[-800:]}
    r = json.loads(p.stdout)
    rec = {"v1_matcher": {k: r[k] for k in ("invocations", "read", "read_exactly",
                                             "read_with_a_word_taken_as_another_option", "top_unread_remainders")},
           "strict": strict_reach(cmd, entries)}
    if cmd in GNU_TABLES:
        rec["gnu_rules"] = gnu_read(cmd, path)
    return rec


# ---- fit with v1's programs: generator use -------------------------------------------------------------

def usefulness(cmd, path, label, skip=None):
    env = f"SKIP='{skip}' " if skip else ""
    p = sh(["limactl", "shell", TRACE_VM, "--", "bash", "-lc",
            f"cd $(mktemp -d) && {env}~/caruca-venv/bin/python -I {HERE / 'trace_usefulness.py'} {cmd} '{path}' '{label}' 2>/dev/null"])
    if p.returncode:
        return {"error": f"exit {p.returncode}"}
    r = json.loads(p.stdout)
    r.pop("syntax_file", None)
    return r


# ---- performance -----------------------------------------------------------------------------------------

def run_metrics(spec_path):
    """The agent run's own figures, from the result event and tool calls in its stream log."""
    run = Path(spec_path).parents[1]
    result, tools = None, 0
    for line in (run / "stream.jsonl").read_text(errors="replace").splitlines():
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        if ev.get("type") == "result":
            result = ev
        elif ev.get("type") == "assistant":
            tools += sum(1 for c in ev.get("message", {}).get("content", []) if c.get("type") == "tool_use")
    if result is None:
        return {"error": "no result event in stream.jsonl"}
    usage = result.get("usage", {})
    return {"run": run.name, "seconds": round(result.get("duration_ms", 0) / 1000),
            "cost_usd_list_price": round(result.get("total_cost_usd", 0), 2), "turns": result.get("num_turns"),
            "tool_calls": tools, "output_tokens": usage.get("output_tokens"),
            "thinking_tokens": (usage.get("output_tokens_details") or {}).get("thinking_tokens")}


def performance(label, path):
    if label.startswith("agent"):
        return run_metrics(path)
    if label == "reference":
        return {"note": "written and corrected by hand (the paper: 80 person-hours for the whole answer key)"}
    return {"note": "shipped with v1; when, with which settings and at what cost it was made is not recorded"}


# ---- one command ---------------------------------------------------------------------------------------------

def score(cmd):
    files = sources(cmd)
    print(f"== {cmd}: {', '.join(files)}", flush=True)
    started = time.time()
    probed = probe(cmd, files)
    out = {"command": cmd, "scored": datetime.now().isoformat(timespec="seconds"),
           "caruca_v1_commit": v1.v1_commit(), "probe_vm": PROBE_VM, "binary_version": probed["version"],
           "files": {}}
    for label, path in files.items():
        print(f"   {label}", flush=True)
        entries = flag_entries(path, cmd)
        rec = {"path": str(path), "real_binary": binary_score(entries, probed)}
        rec["real_world_reach"] = reach(cmd, path, entries) if corpus_lines(cmd) else {"note": "no lines in the corpus"}
        g = usefulness(cmd, path, label)
        if not g.get("traced") and cmd in SKIP_IF_TOO_MANY:
            g["with_skip"] = usefulness(cmd, path, label, skip=SKIP_IF_TOO_MANY[cmd])
        rec["generator_use"] = g
        rec["answer_key"] = answer_key(cmd, path) if label != "reference" else {"note": "is the answer key"}
        rec["performance"] = performance(label, path)
        out["files"][label] = rec
    print("   program-checked facts", flush=True)
    facts, runs = program_facts(cmd, files, {l: r["real_binary"] for l, r in out["files"].items()}, probed)
    for label, f in facts.items():
        out["files"][label]["program_checked"] = f
    out["facts_runs"] = runs
    out["scoring_seconds"] = round(time.time() - started)
    out["probe"] = probed
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / f"{cmd}.json").write_text(json.dumps(out, indent=1, ensure_ascii=False, default=str))


# ---- tables -----------------------------------------------------------------------------------------------------

def frac(a, b):
    return "n/a" if not b else f"{a:,}/{b:,} ({100 * a / b:.0f}%)"


TYPES = ["a listed", "b real", "c value", "d kind", "e equals", "f repeat", "g files", "h rules"]
# the commands Tiran asked for on 2026-10-27; results for others (the 2026-10-26 pilot) stay on disk
TABLE_COMMANDS = ["cut", "sort", "rm", "binwalk"]


def table(commands=TABLE_COMMANDS):
    data = [json.loads((RESULTS / f"{c}.json").read_text()) for c in commands if (RESULTS / f"{c}.json").is_file()]
    head, fit, paper, perf = [], [], [], []
    for d in data:
        c = d["command"]
        for label, r in d["files"].items():
            pc = r.get("program_checked", {})
            if "types" in pc:
                cells = " | ".join(f"{t[0]}/{t[1]}" for t in (pc["types"][k] for k in TYPES))
                head.append(f"| `{c}` | {label} | **{frac(pc['right'], pc['total'])}** | {cells} |")
            w = r.get("real_world_reach", {})
            gr, st, vm = w.get("gnu_rules"), w.get("strict", {}), w.get("v1_matcher", {})
            if gr and "error" not in gr:
                real_world = f"{frac(gr['read_correctly'], gr['valid_lines'])} (GNU's rules)"
            elif st.get("invocations"):
                real_world = f"{frac(st['read'], st['invocations'])} (strict reader)"
            else:
                real_world = "no corpus lines"
            matcher = frac(vm["read"], vm["invocations"]) if vm.get("invocations") else "n/a"
            g = r.get("generator_use", {})
            if g.get("traced"):
                gen = frac(g["distinct_real_work"], g["distinct_lines"])
            elif g.get("with_skip", {}).get("traced"):
                s = g["with_skip"]
                gen = (f"not traced: {g['invocations']:,} lines; without `{s['skip']}`: "
                       f"{frac(s['distinct_real_work'], s['distinct_lines'])}")
            else:
                gen = "n/a"
            fit.append(f"| `{c}` | {label} | {real_world} | {matcher} | {gen} |")
            ak = r.get("answer_key", {}).get("v1-specs", {})
            if "counts" in ak and ak["counts"]:
                k = ak["counts"]
                exact = (ak.get("cmp_specs") or {}).get("exact")
                paper.append(f"| `{c}` | {label} | {k['matched']}/{k['reference_flags']} | {k['spurious']} | "
                             f"{'yes' if exact else 'no'} |")
            p = r.get("performance", {})
            if "seconds" in p:
                perf.append(f"| `{c}` | {label} | {p['seconds']:,} s | ${p['cost_usd_list_price']:.2f} | {p['turns']} | "
                            f"{p['tool_calls']} | {p['output_tokens']:,} |")
            else:
                perf.append(f"| `{c}` | {label} | {p.get('note', p.get('error', ''))} | | | | |")
    text = "\n".join([
        "## Headline: program-checked accuracy (facts right / all facts)", "",
        "| Command | Syntax file | Right | " + " | ".join(TYPES) + " |", "|---|---|---|" + "---|" * len(TYPES), *head, "",
        "## Fit with v1's current programs (mixes the file's quality with v1's conventions)", "",
        "| Command | Syntax file | Real-world lines read correctly | Lines v1's matcher counts as read | "
        "Generated lines doing real work |", "|---|---|---|---|---|", *fit, "",
        "## Paper-comparable: agreement with Caruca's reference (blind spots: task 018, section 4.4)", "",
        "| Command | Syntax file | Reference options matched | Extra options | Exact by v1's cmp_specs |",
        "|---|---|---|---|---|", *paper, "",
        "## Performance of the file's making", "",
        "| Command | Syntax file | Time | Cost (list price) | Turns | Tool calls | Output tokens |",
        "|---|---|---|---|---|---|---|", *perf, ""])
    (RESULTS / "summary.md").write_text(text)
    print(text)


if __name__ == "__main__":
    args = sys.argv[1:]
    if args != ["--table"]:
        for cmd in args:
            score(cmd)
    table()
