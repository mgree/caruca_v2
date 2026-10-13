#!/usr/bin/env python3
"""Print every tool call (and, with -r, every result) from a run's log as a readable list.

Reads either kind of file a run produces:
  runs/<tag>.jsonl             the --output-format stream-json log of a headless run
  runs/<tag>.transcript.jsonl  Claude Code's own session transcript (both modes)

    ./tool_log.py runs/sed_PROMPT_v2.transcript.jsonl        # one line per tool call
    ./tool_log.py -r runs/sed_PROMPT_v2.jsonl                # include each tool's result (truncated)
    ./tool_log.py --json FILE                                # the same, as JSON records
"""
import json, sys, argparse

def blocks(rec):
    m = rec.get("message")
    if isinstance(m, dict):
        c = m.get("content")
        if isinstance(c, list):
            for b in c:
                if isinstance(b, dict):
                    yield b

def summarize(name, inp):
    if not isinstance(inp, dict):
        return str(inp)[:200]
    for k in ("command", "file_path", "pattern", "url", "prompt", "description"):
        if k in inp:
            v = str(inp[k]).replace("\n", " ⏎ ")
            return f"{k}={v[:300]}"
    return json.dumps(inp)[:300]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file"); ap.add_argument("-r", "--results", action="store_true"); ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    out = []; n = 0
    for line in open(a.file, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        ts = rec.get("timestamp") or ""
        for b in blocks(rec):
            if b.get("type") == "tool_use":
                n += 1
                out.append({"n": n, "ts": ts, "tool": b.get("name"), "input": b.get("input"), "id": b.get("id")})
            elif b.get("type") == "tool_result" and a.results:
                c = b.get("content")
                if isinstance(c, list):
                    c = " ".join(x.get("text", "") for x in c if isinstance(x, dict))
                out.append({"ts": ts, "result_for": b.get("tool_use_id"), "is_error": b.get("is_error", False), "text": (str(c) if c is not None else "")[:500]})
        if rec.get("type") == "result":
            out.append({"ts": ts, "result": {k: rec.get(k) for k in ("duration_ms", "num_turns", "total_cost_usd", "usage", "is_error")}})
    if a.json:
        for r in out: print(json.dumps(r))
        return
    for r in out:
        if "tool" in r:
            print(f"{r['n']:4d}  {r['ts'][11:19] if r['ts'] else '        '}  {r['tool']:<12} {summarize(r['tool'], r['input'])}")
        elif "result_for" in r:
            print(f"      {'ERR ' if r['is_error'] else '    '}  -> {r['text'].replace(chr(10),' ⏎ ')[:300]}")
        else:
            print(f"      result: {json.dumps(r['result'])}")
    print(f"{n} tool calls", file=sys.stderr)


if __name__ == "__main__":
    main()
