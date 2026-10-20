---
name: caruca-v1-value-generation
description: How v1 picks argument values and file contents (verified in code 2026-10-20) — Integer emits every value in [min,max] (default -1..1); content pool is 8 files incl. ONE JPEG (paper says PNGs); binwalk finds nothing in 7 of them; v1 generate accepts an outside grammar via --path
metadata:
  type: project
---

Established 2026-10-20 while analysing naive run 6 (binwalk), by reading v1's code at commit d80324073 and
running it on the Mac (v1 `.venv`, Python 3.12.9). Related: [[project-naive-claude-code-arm]],
[[caruca-v1-enumeration-redundancy]].

- **`Integer` enumerates its whole range.** `ir/syntax.py:263-269`: `min: int = -1`, `max: int = 1`,
  `syntax()` returns `range(self.min, self.max + 1)`. So a grammar with `Integer(min=0, max=65535)` yields
  65,536 invocations for that one option. None of v1's own `syntax_specs/*.py` uses `min=` or `max=` (grep,
  2026-10-20). The paper's section 4.2 says only "for integer, it generates the numbers -1, 0, 1".
  The naive arm's `formats/syntax_description.md` mentions `min=`/`max=` with no warning about this.
- **File content pool.** `ir/contents.py` + `data/`: `human_1.txt`, `human_2.txt`, `math_1.txt`,
  `math_2.txt`, `time_1.txt`, `time_2.txt`, `json.json`, `usenix.jpg`. `simple` (the default `--content`)
  = human text only; `varied` = text, math, JSON, time, image; `split` adds the halves. The paper (section
  4.3) says images are "a set of PNG images ranging from 2kb to 4MB"; the code ships one JPEG.
- **binwalk on that pool** (binwalk 2.3.3 in the naive-run clone, 2026-10-20): 0 results in all 7 text /
  math / time / JSON files; 1 in `usenix.jpg` (its own JFIF header at offset 0).
- **Running v1's generator on an outside grammar without touching v1:** put the file in a scratch package
  (`bwspec/__init__.py`, `bwspec/<cmd>.py`), then from that folder call
  `caruca.cli.generate.string_invocations("<cmd>", "bwspec", skip, 1, False, max_count)` with v1's
  `.venv/bin/python -I` and `sys.path.insert(0, '.')` (`get_syntax_spec` imports `f"{path}.{cmd}"`). On the
  binwalk agent grammar: 65,659 at max_count 1; skipping `-s`, 122 (72 distinct) at 1 and 7,282 (2,535
  distinct) at 2. Same method on v1's grep: 121 (74 distinct) at 1. `caruca generate --number`'s formula
  ignores value counts (gives 51 for binwalk at 1), so it undercounts. Wrap the loop with `python -u` or
  print per stage: output buffering hid progress for minutes.
