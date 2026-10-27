#!/usr/bin/env python3
"""Real-world reach: how many of a command's real invocations a syntax file can read.

Uses v1's own `caruca.oracle.oracle` (the matcher behind the paper's coverage section) on the
real-world corpus, with the syntax file swapped in. v1's `caruca oracle` command has no option for
an outside syntax file, so this loads one into a scratch package and points the oracle at it.
Run with v1's interpreter, isolated:

    ~/dev/stevens/caruca/caruca/.venv/bin/python -I reach.py CMD SYNTAX_FILE CORPUS > reach.json

An invocation counts as read when the oracle leaves nothing unmatched. It counts as read
"exactly" when, in addition, every match used v1's `Exact` strategy (no normalisation).

Caution, established 2026-10-26: v1's matcher accepts any word as the flag of any value-taking option
(see the comment below), so "read" does not mean every option in the line is one the syntax file
names; `sort --bogus-option file.txt` is read. The count of lines where that happened is reported,
and score_t018.py adds a strict count of its own.
"""
import json, shutil, sys, tempfile
from collections import Counter
from pathlib import Path

CMD, SPEC, CORPUS = sys.argv[1], Path(sys.argv[2]).resolve(), Path(sys.argv[3])

V1_SRC = Path.home() / "dev/stevens/caruca/caruca/src"
if not V1_SRC.is_dir():
    V1_SRC = Path.home() / "stevens/caruca/caruca/src"
sys.path.insert(0, str(V1_SRC))

scratch = Path(tempfile.mkdtemp(prefix="t018reach."))
pkg = scratch / "t018spec"
pkg.mkdir()
(pkg / "__init__.py").write_text("")
shutil.copy(SPEC, pkg / f"{CMD}.py")
sys.path.insert(0, str(scratch))

import caruca.oracle as v1_oracle  # noqa: E402
from caruca.ir.syntax import Exact  # noqa: E402
from caruca.syntax_specs import get_syntax_spec  # noqa: E402

v1_oracle.get_syntax_spec = lambda _path, name: get_syntax_spec("t018spec", name)

lines = [l.strip() for l in CORPUS.read_text(errors="replace").splitlines()]
mine = [l for l in lines if l.split(maxsplit=1)[:1] == [CMD]]

from caruca.ir.syntax import StringAgnosticism  # noqa: E402

read = exact = substituted = 0
unread = Counter()
for line in mine:
    remaining, strategies = v1_oracle.oracle(line)
    if remaining:
        unread[remaining] += 1
        continue
    read += 1
    if all(isinstance(s, Exact) for s in strategies):
        exact += 1
    # v1's flag matcher (ir/syntax.py, ValueArgument.__flag_match) accepts any word as the flag of a
    # value-taking option, recording StringAgnosticism(word, that option's flag); value-level
    # StringAgnosticism records the choices tuple instead, which prints starting with "("
    if any(isinstance(s, StringAgnosticism) and not str(s.matched_with).startswith("(") for s in strategies):
        substituted += 1

shutil.rmtree(scratch, ignore_errors=True)
json.dump({
    "command": CMD, "syntax_file": str(SPEC), "corpus": str(CORPUS),
    "invocations": len(mine), "read": read, "read_exactly": exact,
    "read_with_a_word_taken_as_another_option": substituted,
    "top_unread_remainders": unread.most_common(10),
}, sys.stdout, indent=1)
