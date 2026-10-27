"""Run each rendered option form on the real binary in a minimal valid context (runs inside a VM).

python3 probe_vm.py forms.json CMD[,CMD...] usenix.jpg out.jsonl
Each form runs once in a fresh temporary directory; stdin is /dev/null; 20 s timeout.
"""
import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile

forms_path, cmds, image, outp = sys.argv[1], sys.argv[2].split(","), sys.argv[3], sys.argv[4]
entries = [e for e in json.load(open(forms_path)) if e["cmd"] in cmds]
SELECTORS = {"-b", "-c", "-f", "--bytes", "--characters", "--fields"}


def fixtures(d, cmd, opt):
    with open(os.path.join(d, "in.txt"), "w") as f:
        f.write("a\nb\n")  # sorted, so --check passes
    if cmd == "convert":
        shutil.copy(image, os.path.join(d, "in.jpg"))
    for ph in ("relpath_1", "abspath_1"):
        p = os.path.join(d, ph)
        if cmd == "sort" and opt in ("-T", "--temporary-directory"):
            os.mkdir(p)
        elif cmd == "sort" and opt == "--files0-from":
            open(p, "wb").write(b"in.txt\0")
        elif cmd == "sort" and opt == "--random-source":
            open(p, "wb").write(os.urandom(4096))
        elif cmd == "sort" and opt in ("-o", "--output"):
            pass  # created by sort
        elif cmd == "convert":
            shutil.copy(image, p)
        else:
            open(p, "w").write("a\nb\n")
    open(os.path.join(d, "target"), "w").write("x\n")


def argv_for(cmd, opt, words, d):
    words = [w.replace("abspath_1", os.path.join(d, "abspath_1")) if w.startswith("abspath_1") or "=abspath_1" in w
             else w for w in words]
    if cmd == "rm":
        return ["rm", *words, "target"]
    if cmd == "cut":
        return ["cut", *words, "in.txt"] if opt in SELECTORS else ["cut", "-f", "1", *words, "in.txt"]
    if cmd == "sort":
        return ["sort", *words] if opt == "--files0-from" else ["sort", *words, "in.txt"]
    if cmd == "convert":
        return ["convert", "in.jpg", *words, "out.png"]


with open(outp, "w") as out:
    for e in entries:
        for form in e["forms"]:
            d = tempfile.mkdtemp(prefix="probe_")
            try:
                fixtures(d, e["cmd"], e["opt"])
                argv = argv_for(e["cmd"], e["opt"], shlex.split(form), d)
                try:
                    p = subprocess.run(argv, cwd=d, stdin=subprocess.DEVNULL, capture_output=True, timeout=20)
                    code, err = p.returncode, p.stderr.decode(errors="replace").strip()
                except subprocess.TimeoutExpired:
                    code, err = "timeout", ""
                out.write(json.dumps({**{k: e[k] for k in ("cmd", "g", "opt", "type")}, "form": form,
                                      "argv": argv, "exit": code, "stderr": err[:300]}) + "\n")
            finally:
                shutil.rmtree(d, ignore_errors=True)
print("done", outp)
