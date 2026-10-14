import json, re, os
P = os.path.dirname(os.path.abspath(__file__))
T = json.load(open(f"{P}/timeline.json")); plan, vo, TOTAL = T["plan"], T["vo"], T["total"]
lines = {l["id"]: l["text"] for l in json.load(open(f"{P}/assets/audio/vo_lines.json"))}
LEAD = 1.2
def ts(t):  # SRT
    ms = int(round(t*1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"
def yt(t):
    t = int(t); m, s = divmod(t, 60); return f"{m}:{s:02}"
def parse(t):
    h, m, r = t.split(":"); s, ms = r.split(","); return int(h)*3600+int(m)*60+int(s)+int(ms)/1000
# proper nouns the speech-to-text misheard
FIX = [(r"\bCloud\b", "Claude"), (r"\bclouds\b", "Claude"), (r"naive\s+LM Karuka", "naive LLM Caruca"), (r"\bKaruka\b", "Caruca"),
       (r"Excalibur Draw", "Excalidraw"), (r"on the Excaligra,", "on the"), (r"Excaligra,\s*", ""), (r"\bpatch output\b", "PaSh output"),
       (r"naive golden is running", "naive-golden is running")]
# recording cues
src = open(f"{P}/assets/transcript.srt").read().strip()
cues = []
for b in re.split(r"\n\s*\n", src):
    L = b.strip().split("\n")
    if len(L) < 3: continue
    a, e = [parse(x.strip()) for x in L[1].split("-->")]
    txt = " ".join(L[2:]).strip()
    for w, r in FIX: txt = re.sub(w, r, txt)
    cues.append((a, e, txt))
segs = [(p[2], p[3], p[4][0]) for p in plan if p[0] == "v"]
out = []
for a, e, txt in cues:
    for st, d, ms in segs:
        if ms <= a < ms + d:
            out.append((st + a - ms, st + min(e, ms + d) - ms, "", txt)); break
# narrator cues: sentences spread over the clip by length
for k, c, s, d, e in plan:
    if k != "g" or not e: continue
    start, dur = s + LEAD, vo[e]
    sents = re.findall(r"[^.!?]+[.!?]", lines[e])
    # split long sentences at the colon/comma nearest the middle
    chunks = []
    for snt in sents:
        snt = snt.strip()
        while len(snt) > 90:
            cut = max((m.end() for m in re.finditer(r"[,:]", snt[:90])), default=0)
            if cut < 30: cut = snt.rfind(" ", 0, 84)
            chunks.append(snt[:cut].strip()); snt = snt[cut:].strip()
        chunks.append(snt)
    tot = sum(len(c) for c in chunks); t = start
    for ch in chunks:
        dd = dur * len(ch) / tot
        out.append((t, t + dd - 0.05, "Narrator: ", ch)); t += dd
out.sort()
with open(f"{P}/youtube/captions.en.srt", "w") as f:
    for i, (a, b, who, txt) in enumerate(out, 1):
        f.write(f"{i}\n{ts(a)} --> {ts(b)}\n{who}{txt}\n\n")
# transcript, paragraph per chapter
chap = [(0.0, "Intro: what a naive LLM run is")]
names = {"inter-1":"Clone the VM and start the run","inter-2":"Collect the output","inter-3":"Ask Claude Code to analyse its own run","inter-4":"The session, phase by phase","inter-5":"By the numbers, and the written analysis","outro":"End card"}
for k, c, s, d, e in plan:
    if c == "seg1": chap.append((s, "Setup: the README and the golden VM"))
    if c in names: chap.append((s, names[c]))
md = []
for i, (cs, name) in enumerate(chap):
    ce = chap[i+1][0] if i+1 < len(chap) else TOTAL
    md.append(f"\n[{yt(cs)}] {name}\n")
    body = []; cur = None
    for a, b, who, txt in out:
        if cs <= a < ce:
            spk = "Narrator" if who else "Tiran"
            if spk != cur: body.append(f"\n{spk} ({yt(a)}): "); cur = spk
            body.append(txt + " ")
    md.append("".join(body).strip() + "\n")
transcript = "".join(md).strip()
open(f"{P}/youtube/transcript.txt", "w").write(transcript + "\n")
chapters = "\n".join(f"{yt(cs)} {n}" for cs, n in chap)
desc = f"""Caruca: Naive LLM Run #1, by Tiran Dagan

A fresh Claude Code session, running in a throwaway Ubuntu VM, gets only a short problem statement, two format documents and a few worked examples. Its task: describe the grep command precisely enough that a shell parallelizer (PaSh) can use the result. This walkthrough shows the first run end to end: cloning the VM, running prompt v1, collecting the output, and asking Claude Code to reconstruct its own session from the transcript.

Run facts: GNU grep 3.11 on Ubuntu 24.04 (aarch64), Claude Code 2.1.296, model claude-haiku-5-5, 739 seconds, 72 tool calls, 85 probe runs of grep, $0.96 at list price.

Chapters
{chapters}

Full transcript: open "Show transcript" under the video (captions are synced to the edit).\n\nRepository: https://github.com/tirandagan/caruca_v2
Run folder: naive_llm_caruca/runs/2026-10-13_193448_naive-run-grep_grep_PROMPT_v1
Caruca paper: https://arxiv.org/abs/2510.14279

The narrated interludes between chapters are synthetic speech generated with ElevenLabs. Music generated with ElevenLabs Music.
"""
open(f"{P}/youtube/description.txt", "w").write(desc)
full = desc + "\nTranscript\n" + transcript + "\n"
print("description chars:", len(desc), "| with transcript:", len(full), "| captions:", len(out))
print(chapters)
