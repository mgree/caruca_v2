#!/usr/bin/env python3
"""Ask the real command which option spellings it accepts and whether each takes a value.

Runs inside a throwaway clone of the naive-arm VM image (the same binaries the agent saw),
with the standard library only:

    python3 probe_binary.py CMD candidates.json > probe.json

`candidates.json` is {"spellings": [...]}: every option spelling named by any syntax file being
scored. The probe adds every spelling it can find in `CMD --help` and the manual page, so the
union of sources defines what "all the options" means; the binary decides which are real.

Each spelling is run at most twice, with stdin from /dev/null, in a fresh empty folder holding
one small text file, with LC_ALL=C and a 3-second limit:

  long  (--name)  `CMD --name` and `CMD --name=zzinvalid`
  short (-x)      `CMD -x`
  word  (bs, if)  `CMD word=1`   (dd-style operands)

and classified by GNU's own error messages: "unrecognized option" / "invalid option" /
"unrecognized operand" mean the spelling does not exist; "requires an argument" means it needs a
value; "doesn't allow an argument" means it takes none; anything else means it was accepted.
"Valid arguments are:" lists are kept, since they are the command describing its own values.
"""
import json, os, re, shutil, subprocess, sys, tempfile

CMD = sys.argv[1]
GIVEN = json.load(open(sys.argv[2]))["spellings"]
TIMEOUT = 3
ENV = {"PATH": "/usr/bin:/bin", "LC_ALL": "C", "HOME": os.environ.get("HOME", "/tmp")}

# GNU getopt's messages, then Python argparse's (binwalk): an unknown option there is taken as a file
# name ("Cannot open file --bogus"), a missing value is "expected one argument", and a value given to an
# option that takes none is "ignored explicit argument"
NOT_ACCEPTED = re.compile(r"unrecognized option|invalid option --|unrecognized operand|unknown option|illegal option"
                          r"|unrecognized arguments")
AMBIGUOUS = re.compile(r"is ambiguous")
REQUIRES = re.compile(r"requires an argument|expected one argument")
NO_VALUE = re.compile(r"doesn't allow an argument|ignored explicit argument")
VALUE_ITEM = re.compile(r"[‘'`]([^’'`]+)[’'`]")


def not_accepted(spelling, stderr):
    return bool(NOT_ACCEPTED.search(stderr)) or f"Cannot open file {spelling} " in stderr


def run(argv):
    work = tempfile.mkdtemp(prefix="t018probe.")
    with open(os.path.join(work, "a.txt"), "w") as f:
        f.write("one\ntwo\nthree\n")
    try:
        p = subprocess.run(argv, cwd=work, env=ENV, stdin=subprocess.DEVNULL, capture_output=True,
                           timeout=TIMEOUT, text=True, errors="replace")
        out = {"argv": argv, "rc": p.returncode, "stderr": p.stderr[:600], "timed_out": False}
    except subprocess.TimeoutExpired:
        out = {"argv": argv, "rc": None, "stderr": "", "timed_out": True}
    finally:
        shutil.rmtree(work, ignore_errors=True)
    return out


def valid_values(stderr):
    if "Valid arguments are:" not in stderr:
        return []
    tail = stderr.split("Valid arguments are:", 1)[1]
    values = []
    for line in tail.splitlines():
        if not line.strip().startswith("-"):
            if values:
                break
            continue
        values += VALUE_ITEM.findall(line)
    return values


def probe(spelling):
    if spelling.startswith("--"):
        r0, r1 = run([CMD, spelling]), run([CMD, spelling + "=zzinvalid"])
        runs = [r0, r1]
        if not_accepted(spelling, r0["stderr"]):
            verdict = {"accepted": False}
        elif AMBIGUOUS.search(r0["stderr"]):
            verdict = {"accepted": False, "ambiguous": True}
        elif REQUIRES.search(r0["stderr"]):
            verdict = {"accepted": True, "value": "required"}
        elif NO_VALUE.search(r1["stderr"]):
            verdict = {"accepted": True, "value": "none"}
        else:
            verdict = {"accepted": True, "value": "optional"}
        verdict["valid_values"] = valid_values(r1["stderr"]) or valid_values(r0["stderr"])
    elif spelling.startswith("-") and len(spelling) >= 2:
        r0 = run([CMD, spelling])
        runs = [r0]
        if not_accepted(spelling, r0["stderr"]):
            verdict = {"accepted": False}
        elif REQUIRES.search(r0["stderr"]):
            verdict = {"accepted": True, "value": "required"}
        else:
            verdict = {"accepted": True, "value": "none"}
        verdict["valid_values"] = valid_values(r0["stderr"])
    else:
        r0 = run([CMD, spelling + "=1"])
        runs = [r0]
        verdict = {"accepted": not NOT_ACCEPTED.search(r0["stderr"]), "value": "required", "valid_values": []}
    verdict["runs"] = runs
    return verdict


def from_docs():
    """Option spellings named by the command's own --help and manual page."""
    found = {}
    man = subprocess.run(["man", "-P", "cat", CMD], env={**ENV, "MANWIDTH": "200"},
                         capture_output=True, text=True, errors="replace").stdout
    help_out = subprocess.run([CMD, "--help"], env=ENV, stdin=subprocess.DEVNULL, capture_output=True,
                              text=True, errors="replace", timeout=TIMEOUT).stdout
    for source, text in (("help", help_out), ("man", man)):
        for line in text.splitlines():
            if not re.match(r"\s*-", line):
                continue
            # an option line: spellings first, then two or more spaces, then the description
            head = re.split(r"\s{2,}", line.strip())[0]
            for s in re.findall(r"(?<![\w-])(--?[A-Za-z0-9][A-Za-z0-9-]*)", head):
                found.setdefault(s, set()).add(source)
    return {k: sorted(v) for k, v in found.items()}


def version():
    # GNU tools answer --version; binwalk has none and names its version in --help's first line
    for flag in ("--version", "--help"):
        try:
            p = subprocess.run([CMD, flag], env=ENV, capture_output=True, text=True, timeout=TIMEOUT)
        except Exception:
            continue
        lines = [l.strip() for l in (p.stdout + p.stderr).splitlines() if l.strip()]
        # binwalk takes --version as a file name and answers with an error, so require a clean answer
        if lines and p.returncode == 0 and "error" not in lines[0].lower() and re.search(r"\d+\.\d+", lines[0]):
            return lines[0]
    return "unavailable"


docs = from_docs()
sources = {s: ["syntax files"] for s in GIVEN}
for s, where in docs.items():
    sources.setdefault(s, []).extend(where)

result = {"command": CMD, "binary": shutil.which(CMD), "version": version(), "spellings": {}}
for s in sorted(sources):
    entry = probe(s)
    entry["named_by"] = sources[s]
    result["spellings"][s] = entry
json.dump(result, sys.stdout, indent=1, ensure_ascii=False)
