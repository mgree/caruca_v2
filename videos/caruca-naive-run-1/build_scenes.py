import json, os
P = os.path.dirname(os.path.abspath(__file__))
vo = {k: float(os.popen(f"ffprobe -v error -show_entries format=duration -of csv=p=0 {P}/assets/audio/{k}.mp3").read()) for k in ["vo0","vo1","vo2","vo3","vo4","vo5","vo6"]}
LEAD, TAIL, X = 1.2, 1.0, 0.5   # narration lead-in, tail, crossfade overlap
SRC_END = 450.986
segs = [(0.0,33.5),(33.5,120.8),(120.8,219.0),(219.0,301.2),(301.2,386.9),(386.9,SRC_END)]
chapters = ["1 · Setup: the README and the golden VM","2 · Clone the VM and start the run","3 · Collect the output and look at the run folder","4 · Ask Claude Code to analyse its own run","5 · The eight-phase session diagram","6 · The written analysis and the final output"]
# nominal timeline
t = 0.0
plan = []  # (kind, id, start, dur, extra)
plan.append(("g","cover",0.0,5.0,None)); t = 5.0
inter_ids = ["inter-0","inter-1","inter-2","inter-3","inter-4","inter-5"]
for i,(a,b) in enumerate(segs):
    d = vo[f"vo{i}"] + LEAD + TAIL
    plan.append(("g",inter_ids[i],t,d,f"vo{i}")); t += d
    plan.append(("v",f"seg{i+1}",t,b-a,(a,chapters[i]))); t += (b-a)
out_d = vo["vo6"] + LEAD + 2.6
plan.append(("g","outro",t,out_d,"vo6")); TOTAL = t + out_d
json.dump({"vo":vo,"plan":plan,"total":TOTAL}, open(f"{P}/timeline.json","w"), indent=1)
print("TOTAL", round(TOTAL,2))
for p in plan: print(p[0], p[1], round(p[2],2), round(p[3],2))

FONTS = """
@font-face{font-family:'Lexend Deca';src:url('assets/fonts/LexendDeca-Regular.ttf') format('truetype');font-weight:400;font-style:normal}
@font-face{font-family:'Lexend Deca';src:url('assets/fonts/LexendDeca-SemiBold.ttf') format('truetype');font-weight:600;font-style:normal}
@font-face{font-family:'Lexend Deca';src:url('assets/fonts/LexendDeca-Bold.ttf') format('truetype');font-weight:700;font-style:normal}
@font-face{font-family:'JetBrains Mono';src:url('assets/fonts/JetBrainsMono-Regular.woff2') format('woff2');font-weight:400;font-style:normal}
"""
BASE_CSS = """
#root{position:absolute;inset:0;width:100%;height:100%;overflow:hidden;background:#0B1F33;color:#F4F7FB;font-family:'Lexend Deca',sans-serif;}
#root .bg{position:absolute;inset:0;background:radial-gradient(1200px 800px at 18% 85%, rgba(14,116,144,0.22), rgba(11,31,51,0) 70%), linear-gradient(135deg,#0B1F33 0%,#0E2744 60%,#0B1F33 100%);}
#root .rings{position:absolute;right:-340px;top:-420px;width:1200px;height:1200px;will-change:transform;}
#root .rings circle{fill:none;stroke:#0E7490;stroke-width:1.5}
#root .rule{position:absolute;left:120px;right:120px;top:148px;height:1px;background:#1E3A5F}
#root .accent{position:absolute;left:120px;top:146px;width:80px;height:4px;border-radius:2px;background:linear-gradient(to right,#0E7490,#2563EB);transform-origin:left center}
#root .micro{position:absolute;left:120px;top:96px;font-family:'JetBrains Mono',monospace;font-size:20px;letter-spacing:0.08em;text-transform:uppercase;color:#7DD3E8;}
#root .micro span{display:inline-block}
#root .headline{position:absolute;left:120px;top:190px;font-size:64px;font-weight:700;letter-spacing:-0.02em;line-height:1.1;color:#F4F7FB}
#root .headline span{display:inline-block;opacity:0;margin-right:0.26em;will-change:transform}
#root .sub{position:absolute;left:120px;top:290px;font-size:26px;font-weight:400;color:#A9BDD3;max-width:1500px;line-height:1.4}
#root .mono{font-family:'JetBrains Mono',monospace}
#root .card{position:absolute;background:#102B49;border:1px solid #27476E;border-radius:6px;padding:22px 26px;will-change:transform;transform-origin:50% 50%}
#root .card .t{font-size:26px;font-weight:600;color:#F4F7FB}
#root .card .d{font-size:21px;color:#A9BDD3;margin-top:6px;line-height:1.35}
#root .card.blue{border-color:#2563EB;box-shadow:0 0 0 1px rgba(37,99,235,0.35) inset}
#root .card.teal{border-color:#0E7490}
#root .chip{display:inline-block;font-family:'JetBrains Mono',monospace;font-size:18px;padding:6px 12px;border-radius:4px;background:#0E2744;border:1px solid #27476E;color:#CFE3F5;margin-right:10px}
#root svg.wires{position:absolute;left:0;top:0;width:1920px;height:1080px;pointer-events:none}
#root svg.wires path{fill:none;stroke:#2563EB;stroke-width:3;stroke-linecap:round}
#root svg.wires path.teal{stroke:#0E7490}
#root .mark{position:absolute;width:300px;height:200px;object-fit:contain}
#root .chipmark{position:absolute;background:#F4F7FB;border-radius:18px;display:flex;align-items:center;justify-content:center;will-change:transform;box-shadow:0 20px 60px rgba(0,0,0,0.35)}
#root .chipmark img{width:86%;height:86%;object-fit:contain}
#root .glow{position:absolute;border-radius:50%;background:radial-gradient(circle, rgba(37,99,235,0.55) 0%, rgba(14,116,144,0.25) 40%, rgba(11,31,51,0) 70%);opacity:0;will-change:transform,opacity}
"""
RINGS = """<svg class="rings" viewBox="0 0 1200 1200" aria-hidden="true">
<circle cx="600" cy="600" r="160" opacity="0.10"/><circle cx="600" cy="600" r="260" opacity="0.08"/><circle cx="600" cy="600" r="360" opacity="0.07"/><circle cx="600" cy="600" r="460" opacity="0.05"/><circle cx="600" cy="600" r="560" opacity="0.04"/></svg>"""

def ambient_js(cid):
    # sine-wave-loop: finite repeats; rings drift + accent bar draws
    return f"""
tl.fromTo("#{cid}-rings",{{rotation:0,scale:1}},{{rotation:6,scale:1.03,duration:9,ease:"sine.inOut",repeat:3,yoyo:true}},0);
if(document.getElementById("{cid}-accent"))tl.fromTo("#{cid}-accent",{{scaleX:0}},{{scaleX:1,duration:0.6,ease:"power3.out"}},0.25);
if(document.getElementById("{cid}-rule"))tl.fromTo("#{cid}-rule",{{opacity:0}},{{opacity:1,duration:0.5}},0.3);
"""
def waterfall_js(sel_prefix, n, t0=0.35):
    # waterfall-entry: binary reveal + whip from below, overlapping, shrinking gaps
    js=[]; t=t0; F=1/60
    for i in range(n):
        dur = 0.18 if i==0 else max(0.11,0.16-0.006*i)
        y = 70 if i==0 else 44
        js.append(f'tl.set("#{sel_prefix}{i}",{{opacity:1,y:{y}}},{t:.3f});tl.to("#{sel_prefix}{i}",{{y:0,duration:{dur:.3f},ease:"power4.out"}},{t:.3f});')
        t += dur - (2*F if i==0 else F*(1+min(i,2)))
    return "\n".join(js), t
def words_html(prefix, text):
    return "".join(f'<span id="{prefix}{i}">{w}</span>' for i,w in enumerate(text.split(" ")))

def scene(cid, dur, body, js, extra_css=""):
    return f"""<!doctype html>
<html lang="en"><head><meta charset="UTF-8"/></head><body>
<template>
<style>{FONTS}{BASE_CSS}{extra_css}</style>
<div id="root" data-composition-id="{cid}" data-width="1920" data-height="1080" data-duration="{dur:.3f}">
<div class="bg"></div>
{RINGS.replace('class="rings"', f'class="rings" id="{cid}-rings"')}
{body}
</div>
<script>
(function(){{
const tl = gsap.timeline({{ paused: true }});
{ambient_js(cid)}
{js}
window.__timelines["{cid}"] = tl;
}})();
</script>
</template></body></html>"""

def head(cid, micro, headline, sub=""):
    wjs, tend = waterfall_js(f"{cid}-h", len(headline.split(" ")))
    h = f'''<div class="micro" id="{cid}-micro">{micro}</div>
<div class="rule" id="{cid}-rule"></div><div class="accent" id="{cid}-accent"></div>
<div class="headline">{words_html(f"{cid}-h", headline)}</div>
{f'<div class="sub" id="{cid}-sub">{sub}</div>' if sub else ''}'''
    js = f'tl.fromTo("#{cid}-micro",{{opacity:0,x:-20}},{{opacity:1,x:0,duration:0.5,ease:"power2.out"}},0.15);\n{wjs}\n'
    if sub: js += f'tl.fromTo("#{cid}-sub",{{opacity:0,y:16}},{{opacity:1,y:0,duration:0.6,ease:"power2.out"}},{tend+0.1:.2f});\n'
    return h, js

def pop(sel, at, dur=0.55, y=24):
    return f'tl.fromTo("{sel}",{{scale:0.6,opacity:0,y:{y}}},{{scale:1,opacity:1,y:0,duration:{dur},ease:"power3.out"}},{at:.2f});\n'
def draw(cid, ids, at, dur=0.7, gap=0.5):
    js = f'''document.querySelectorAll("#{cid}-wires path").forEach(function(p){{var L=p.getTotalLength();p.style.strokeDasharray=L;p.style.strokeDashoffset=L;}});\n'''
    for i,pid in enumerate(ids):
        js += f'tl.to("#{pid}",{{strokeDashoffset:0,duration:{dur},ease:"power2.out"}},{at+i*gap:.2f});\n'
    return js

D = {p[1]:p[3] for p in plan}
files = {}

# ---------- COVER ----------
cid="cover"
title_words = "Caruca: Naive LLM Run #1".split(" ")
body = f'''
<div class="glow" id="{cid}-glow" style="left:60px;top:200px;width:720px;height:720px"></div>
<div class="chipmark" id="{cid}-mark" style="left:150px;top:370px;width:480px;height:340px"><img src="assets/logo.png" alt=""/></div>
<div id="{cid}-kicker" class="micro" style="left:744px;top:300px;font-size:24px;color:#7DD3E8">Caruca v2 · naive LLM arm · walkthrough</div>
<div class="headline" style="left:740px;top:360px;font-size:120px;line-height:1.02;max-width:1120px">{words_html(f"{cid}-h", "Caruca: Naive LLM Run #1")}</div>
<div id="{cid}-by" style="position:absolute;left:744px;top:650px;font-size:46px;font-weight:400;color:#CFE3F5;opacity:0;will-change:transform">by Tiran Dagan</div>
<div id="{cid}-chips" style="position:absolute;left:744px;top:760px;opacity:0;will-change:transform"><span class="chip">grep</span><span class="chip">PROMPT_v1</span><span class="chip">claude-haiku-5-5</span><span class="chip">2026-10-13</span></div>
<div class="accent" id="{cid}-accent" style="left:744px;top:730px;width:160px"></div>
<div class="rule" id="{cid}-rule" style="left:744px;right:120px;top:732px"></div>
'''
wjs, tend = waterfall_js(f"{cid}-h", len(title_words), t0=0.9)
js = f'''
tl.fromTo("#{cid}-mark",{{scale:0.7,opacity:0}},{{scale:1,opacity:1,duration:0.9,ease:"power3.out"}},0.3);
tl.fromTo("#{cid}-glow",{{opacity:0,scale:0.7}},{{opacity:0.42,scale:1,duration:1.1,ease:"power2.out"}},0.2);
(function(){{var g=document.getElementById("{cid}-glow");var ph={{p:0}};tl.to(ph,{{p:Math.PI*2*2,duration:4.2,ease:"none",onUpdate:function(){{var s=Math.sin(ph.p);g.style.opacity=String(0.42+s*0.05);g.style.transform="scale("+(1+s*0.03)+")";}}}},1.3);}})();
tl.fromTo("#{cid}-kicker",{{opacity:0,x:-20}},{{opacity:1,x:0,duration:0.5,ease:"power2.out"}},0.6);
{wjs}
tl.fromTo("#{cid}-by",{{opacity:0,y:20}},{{opacity:1,y:0,duration:0.5,ease:"power3.out"}},{tend+0.05:.2f});
tl.fromTo("#{cid}-chips",{{opacity:0,y:16}},{{opacity:1,y:0,duration:0.5,ease:"power3.out"}},{tend+0.35:.2f});
'''
files["cover"] = scene(cid, D["cover"]+X, body, js)

# ---------- INTER-0: what a naive run is ----------
cid="inter-0"
h, hjs = head(cid, "Chapter 0 · what a naive run is", "One prompt, one throwaway machine, four files")
body = h + f'''
<div class="card" id="{cid}-in0" style="left:120px;top:430px;width:420px"><div class="t">Problem statement</div><div class="d">PROMPT_v1: describe <span class="mono">grep</span></div></div>
<div class="card" id="{cid}-in1" style="left:120px;top:570px;width:420px"><div class="t">Two format documents</div><div class="d">Caruca syntax DSL · PaSh annotations</div></div>
<div class="card" id="{cid}-in2" style="left:120px;top:710px;width:420px"><div class="t">Worked examples</div><div class="d"><span class="mono">tee · uniq · grep · rm</span></div></div>
<div class="card blue" id="{cid}-vm" style="left:700px;top:520px;width:520px;padding:28px 30px"><div class="t">Throwaway Ubuntu VM</div><div class="d">Fresh Claude Code 2.1.296 session<br/>model <span class="mono">claude-haiku-5-5</span> · no hints, no pipeline</div></div>
<div class="card" id="{cid}-out0" style="left:1380px;top:400px;width:420px"><div class="t mono" style="font-size:21px">output/grep.py</div><div class="d">syntax description</div></div>
<div class="card" id="{cid}-out1" style="left:1380px;top:520px;width:420px"><div class="t mono" style="font-size:21px">pash/grep.json</div><div class="d">parser table</div></div>
<div class="card" id="{cid}-out2" style="left:1380px;top:640px;width:420px"><div class="t mono" style="font-size:21px">InputOutputInfoGeneratorGrep.py</div><div class="d">what it reads and writes</div></div>
<div class="card" id="{cid}-out3" style="left:1380px;top:760px;width:420px"><div class="t mono" style="font-size:21px">ParallelizabilityInfoGeneratorGrep.py</div><div class="d">can the input be split</div></div>
<svg class="wires" id="{cid}-wires" viewBox="0 0 1920 1080">
<path id="{cid}-w0" d="M540 478 C 620 478, 620 580, 700 580"/><path id="{cid}-w1" d="M540 618 L 700 618"/><path id="{cid}-w2" d="M540 758 C 620 758, 620 656, 700 656"/>
<path id="{cid}-w3" class="teal" d="M1220 600 C 1300 600, 1300 448, 1380 448"/><path id="{cid}-w4" class="teal" d="M1220 605 C 1300 605, 1300 568, 1380 568"/><path id="{cid}-w5" class="teal" d="M1220 610 C 1300 610, 1300 688, 1380 688"/><path id="{cid}-w6" class="teal" d="M1220 615 C 1300 615, 1300 808, 1380 808"/>
</svg>'''
js = hjs + pop(f"#{cid}-in0",1.6)+pop(f"#{cid}-in1",1.75)+pop(f"#{cid}-in2",1.9) + draw(cid,[f"{cid}-w0",f"{cid}-w1",f"{cid}-w2"],2.5,0.6,0.12) + pop(f"#{cid}-vm",3.1,0.7,0) + draw(cid,[f"{cid}-w3",f"{cid}-w4",f"{cid}-w5",f"{cid}-w6"],5.2,0.6,0.12) + "".join(pop(f"#{cid}-out{i}",5.9+i*0.15,0.5,16) for i in range(4))
files["inter-0"] = scene(cid, D["inter-0"]+2*X, body, js)

# ---------- INTER-1: clone and run ----------
cid="inter-1"
h, hjs = head(cid, "Chapter 2 · clone the VM and start the run", "A clean clone for every run")
body = h + f'''
<div class="card teal" id="{cid}-g" style="left:120px;top:430px;width:640px;padding:34px"><div class="micro" style="position:static;font-size:16px;color:#7DD3E8">golden image</div><div class="t" style="font-size:30px;margin-top:6px">naive-golden</div><div class="d">Ubuntu 24.04 · Claude Code 2.1.296<br/>no mounts, no project, nothing else</div></div>
<div class="card blue" id="{cid}-c" style="left:1100px;top:430px;width:640px;padding:34px"><div class="micro" style="position:static;font-size:16px;color:#7DD3E8">clone for this run</div><div class="t" style="font-size:30px;margin-top:6px">naive-run-grep</div><div class="d">runs the session, then is deleted</div></div>
<div id="{cid}-lbl" style="position:absolute;left:840px;top:470px;width:180px;text-align:center;font-family:'JetBrains Mono',monospace;font-size:20px;color:#7DD3E8;opacity:0">clone</div>
<svg class="wires" id="{cid}-wires" viewBox="0 0 1920 1080"><path id="{cid}-w0" d="M760 530 L 1100 530"/><path id="{cid}-w1" d="M1075 515 L 1100 530 L 1075 545"/></svg>
<div id="{cid}-term" class="card" style="left:120px;top:720px;width:1680px;padding:20px 26px;background:#071626;border-color:#1E3A5F"><div class="mono" style="font-size:23px;color:#CFE3F5;white-space:pre"><span style="color:#7DD3E8">$ </span><span id="{cid}-cmd"></span><span id="{cid}-cur" style="display:inline-block;width:12px;height:26px;background:#CFE3F5;vertical-align:-3px"></span></div><div id="{cid}-status" class="mono" style="font-size:20px;color:#A9BDD3;margin-top:10px;opacity:0">session running unattended · 73 turns · 72 tool calls · 12 min 19 s</div></div>
'''
cmd = "./new_run_vm.sh naive-run-grep  &&  limactl shell naive-run-grep  &&  naive-run grep PROMPT_v1.md"
js = hjs + pop(f"#{cid}-g",1.5,0.6,0) + draw(cid,[f"{cid}-w0",f"{cid}-w1"],2.4,0.5,0.35) + f'tl.fromTo("#{cid}-lbl",{{opacity:0,y:8}},{{opacity:1,y:0,duration:0.4}},2.6);\n' + pop(f"#{cid}-c",3.2,0.6,0) + f'''
tl.fromTo("#{cid}-term",{{opacity:0,y:20}},{{opacity:1,y:0,duration:0.5,ease:"power2.out"}},4.6);
(function(){{var full={json.dumps(cmd)};var el=document.getElementById("{cid}-cmd");var st={{n:0}};tl.to(st,{{n:full.length,duration:3.2,ease:"none",onUpdate:function(){{el.textContent=full.slice(0,Math.round(st.n));}}}},5.2);
var cur=document.getElementById("{cid}-cur");var bl={{p:0}};tl.to(bl,{{p:1,duration:{D["inter-1"]+1:.1f},ease:"none",onUpdate:function(){{cur.style.opacity=((tl.time()%1)<0.5)?"1":"0";}}}},0);}})();
tl.fromTo("#{cid}-status",{{opacity:0}},{{opacity:1,duration:0.5}},9.0);
'''
files["inter-1"] = scene(cid, D["inter-1"]+2*X, body, js)

# ---------- INTER-2: collect ----------
cid="inter-2"
h, hjs = head(cid, "Chapter 3 · collect the output", "Everything the session touched comes back out")
rows = [("runs/2026-10-13_193448_naive-run-grep_grep_PROMPT_v1/","",""),
 ("  output/grep.py","deliverable","syntax description in the Caruca DSL"),
 ("  output/pash/grep.json","deliverable","PaSh parser table (62 flags, 22 options)"),
 ("  output/pash/InputOutputInfoGeneratorGrep.py","deliverable","what grep reads and writes"),
 ("  output/pash/ParallelizabilityInfoGeneratorGrep.py","deliverable","when its input can be split"),
 ("  transcript_2b9d690b-….jsonl","evidence","every turn and tool call, in order"),
 ("  stream.jsonl · stream.actions.log","evidence","the live event stream and 72 numbered actions"),
 ("  environment.txt · run.env","evidence","OS, binary path, grep 3.11, model, clock")]
body = h + '<div style="position:absolute;left:120px;top:400px;width:1680px">' + "".join(f'''<div id="{cid}-r{i}" style="display:flex;align-items:center;height:62px;border-bottom:1px solid #1E3A5F;opacity:0;will-change:transform"><div class="mono" style="font-size:{26 if i==0 else 23}px;color:{'#7DD3E8' if i==0 else '#F4F7FB'};width:880px;white-space:pre">{a}</div><div style="width:160px">{f'<span class="chip" style="border-color:{"#2563EB" if b=="deliverable" else "#0E7490"};color:{"#CFE3F5"}">{b}</span>' if b else ''}</div><div style="font-size:21px;color:#A9BDD3">{c}</div></div>''' for i,(a,b,c) in enumerate(rows)) + '</div>'
wjs,_ = waterfall_js(f"{cid}-r", len(rows), t0=1.7)
js = hjs + wjs
files["inter-2"] = scene(cid, D["inter-2"]+2*X, body, js)

# ---------- INTER-3: analysis ----------
cid="inter-3"
h, hjs = head(cid, "Chapter 4 · ask Claude Code to analyse its own run", "Reconstruct the session from its transcript")
body = h + f'''
<div class="card" id="{cid}-a" style="left:120px;top:520px;width:440px;padding:28px"><div class="t mono" style="font-size:22px">transcript_….jsonl</div><div class="d">73 turns, 72 tool calls, timestamps, every command and result</div></div>
<div class="card blue" id="{cid}-b" style="left:740px;top:520px;width:440px;padding:28px"><div class="t">The README's analysis prompt</div><div class="d">a second, separate Claude Code session: what happened, in what order, and why</div></div>
<div class="card teal" id="{cid}-c0" style="left:1360px;top:420px;width:440px"><div class="t mono" style="font-size:22px">analysis.md</div><div class="d">timeline, sources, isolation, testing, cost</div></div>
<div class="card teal" id="{cid}-c1" style="left:1360px;top:560px;width:440px"><div class="t mono" style="font-size:22px">session_workflow.png</div><div class="d">eight phases on one timeline</div></div>
<div class="card teal" id="{cid}-c2" style="left:1360px;top:700px;width:440px"><div class="t mono" style="font-size:22px">information_flow.png</div><div class="d">what it read, what it wrote</div></div>
<svg class="wires" id="{cid}-wires" viewBox="0 0 1920 1080"><path id="{cid}-w0" d="M560 600 L 740 600"/><path id="{cid}-w1" class="teal" d="M1180 590 C 1270 590, 1270 470, 1360 470"/><path id="{cid}-w2" class="teal" d="M1180 600 C 1270 600, 1270 610, 1360 610"/><path id="{cid}-w3" class="teal" d="M1180 610 C 1270 610, 1270 750, 1360 750"/></svg>'''
js = hjs + pop(f"#{cid}-a",1.5,0.6,0) + draw(cid,[f"{cid}-w0"],2.3,0.5) + pop(f"#{cid}-b",2.9,0.6,0) + draw(cid,[f"{cid}-w1",f"{cid}-w2",f"{cid}-w3"],4.6,0.6,0.15) + "".join(pop(f"#{cid}-c{i}",5.3+i*0.18,0.5,14) for i in range(3))
files["inter-3"] = scene(cid, D["inter-3"]+2*X, body, js)

# ---------- INTER-4: eight phases ----------
cid="inter-4"
h, hjs = head(cid, "Chapter 5 · the session, phase by phase", "Eight phases, 739 seconds, first file at minute seven")
phases=[("1","Orientation",4),("2","Identify the binary and its docs",12),("3","Find tooling (PaSh wheel, GitHub)",103),("4","Probe the binary · 85 runs",303),("5","Write the four files",63),("6","Build and run three check scripts",196),("7","Revise after testing",31),("8","Wrap up and report",25)]
MAXW=1000
body = h + '<div style="position:absolute;left:120px;top:400px;width:1680px">' + "".join(f'''<div id="{cid}-p{i}" style="display:flex;align-items:center;height:66px;opacity:0;will-change:transform"><div class="mono" style="width:60px;font-size:22px;color:#7DD3E8">{n}</div><div style="width:520px;font-size:24px;color:#F4F7FB">{name}</div><div style="width:{MAXW}px;height:22px;background:#102B49;border-radius:4px;overflow:hidden"><div id="{cid}-f{i}" style="width:{int(MAXW*s/303)}px;height:100%;background:{'#2563EB' if i in (3,5) else '#0E7490'};transform-origin:left center;border-radius:4px"></div></div><div class="mono" style="width:100px;text-align:right;font-size:22px;color:#CFE3F5">{s} s</div></div>''' for i,(n,name,s) in enumerate(phases)) + f'''</div>
<div id="{cid}-mlbl" style="position:absolute;left:120px;top:960px;font-size:26px;color:#CFE3F5;opacity:0;will-change:transform">Phases 1 to 4 ran for <b style="color:#F4F7FB">7 minutes</b> before the first file was written <span class="mono" style="color:#7DD3E8;font-size:22px">(19:41:53 · call 28)</span></div>'''
wjs,_ = waterfall_js(f"{cid}-p", len(phases), t0=1.6)
js = hjs + wjs + "".join(f'tl.fromTo("#{cid}-f{i}",{{scaleX:0}},{{scaleX:1,duration:0.9,ease:"power2.out"}},{3.0+i*0.12:.2f});\n' for i in range(8)) + f'''
tl.fromTo("#{cid}-mlbl",{{opacity:0,y:14}},{{opacity:1,y:0,duration:0.6,ease:"power2.out"}},9.6);'''
files["inter-4"] = scene(cid, D["inter-4"]+2*X, body, js)

# ---------- INTER-5: by the numbers ----------
cid="inter-5"
h, hjs = head(cid, "Chapter 6 · by the numbers", "What one naive run cost")
stats=[("739","s","wall clock"),("72","","tool calls"),("85","","probe runs of grep"),("0.96","$","list-price cost")]
body = h + "".join(f'''<div class="card" id="{cid}-s{i}" style="left:{120+i*430}px;top:430px;width:400px;height:250px;padding:30px"><div style="display:flex;align-items:baseline;justify-content:center;height:130px"><span class="mono" id="{cid}-pre{i}" style="font-size:44px;color:#7DD3E8;opacity:0">{sfx if sfx=='$' else ''}</span><span class="mono" id="{cid}-n{i}" style="font-size:96px;color:#F4F7FB;font-variant-numeric:tabular-nums;display:inline-block;transform-origin:center center">0</span><span class="mono" id="{cid}-suf{i}" style="font-size:44px;color:#7DD3E8;margin-left:10px;opacity:0">{sfx if sfx!='$' else ''}</span></div><div style="text-align:center;font-size:24px;color:#A9BDD3;margin-top:10px">{lbl}</div></div>''' for i,(v,sfx,lbl) in enumerate(stats)) + f'''
<div id="{cid}-chips" style="position:absolute;left:120px;top:730px;opacity:0;will-change:transform"><span class="chip">claude-haiku-5-5</span><span class="chip">Claude Code 2.1.296</span><span class="chip">Ubuntu 24.04 · aarch64</span><span class="chip">GNU grep 3.11</span></div>
<div id="{cid}-note" style="position:absolute;left:120px;top:810px;font-size:28px;color:#CFE3F5;opacity:0;will-change:transform;line-height:1.5">Unasked, it wrote <b style="color:#F4F7FB">3 test scripts</b> of its own and revised its output <b style="color:#F4F7FB">once</b> after a test failed.</div>'''
js = hjs + "".join(pop(f"#{cid}-s{i}",1.5+i*0.15,0.6,20) for i in range(4))
for i,(v,sfx,lbl) in enumerate(stats):
    dec = 2 if '.' in v else 0
    js += f'''(function(){{var el=document.getElementById("{cid}-n{i}");var st={{v:0}};tl.to(st,{{v:{v},duration:1.6,ease:"power2.out",onUpdate:function(){{el.textContent=st.v.toFixed({dec});}}}},{2.3+i*0.15:.2f});tl.fromTo(el,{{scale:0.7}},{{scale:1,duration:1.6,ease:"power2.out"}},{2.3+i*0.15:.2f});
tl.to("#{cid}-suf{i}",{{opacity:1,duration:0.3}},{3.9+i*0.15:.2f});tl.to("#{cid}-pre{i}",{{opacity:1,duration:0.3}},{2.3+i*0.15:.2f});}})();
'''
js += f'tl.fromTo("#{cid}-chips",{{opacity:0,y:14}},{{opacity:1,y:0,duration:0.5,ease:"power2.out"}},5.0);\ntl.fromTo("#{cid}-note",{{opacity:0,y:14}},{{opacity:1,y:0,duration:0.6,ease:"power2.out"}},9.5);\n'
files["inter-5"] = scene(cid, D["inter-5"]+2*X, body, js)

# ---------- OUTRO ----------
cid="outro"
od = D["outro"]+X
body = f'''
<div class="glow" id="{cid}-glow" style="left:560px;top:120px;width:800px;height:800px"></div>
<div class="chipmark" id="{cid}-mark" style="left:800px;top:230px;width:320px;height:230px"><img src="assets/logo.png" alt=""/></div>
<div id="{cid}-t" style="position:absolute;left:0;right:0;top:510px;text-align:center;font-size:72px;font-weight:700;letter-spacing:-0.02em;opacity:0;will-change:transform">Caruca v2</div>
<div id="{cid}-u" class="mono" style="position:absolute;left:0;right:0;top:615px;text-align:center;font-size:30px;color:#7DD3E8;opacity:0;will-change:transform">github.com/tirandagan/caruca_v2</div>
<div id="{cid}-p" class="mono" style="position:absolute;left:0;right:0;top:675px;text-align:center;font-size:20px;color:#A9BDD3;opacity:0;will-change:transform">naive_llm_caruca/runs/2026-10-13_193448_naive-run-grep_grep_PROMPT_v1 · analysis/analysis.md</div>
<div id="{cid}-by" style="position:absolute;left:0;right:0;top:760px;text-align:center;font-size:30px;color:#CFE3F5;opacity:0;will-change:transform">Recorded by Tiran Dagan · 2026-10-13 · interludes voiced with ElevenLabs</div>
<div id="{cid}-fade" style="position:absolute;inset:0;background:#0B1F33;opacity:0"></div>'''
js = f'''
tl.fromTo("#{cid}-mark",{{scale:0.7,opacity:0}},{{scale:1,opacity:1,duration:0.9,ease:"power3.out"}},0.5);
tl.fromTo("#{cid}-glow",{{opacity:0,scale:0.7}},{{opacity:0.4,scale:1,duration:1.1,ease:"power2.out"}},0.4);
tl.fromTo("#{cid}-t",{{opacity:0,y:20}},{{opacity:1,y:0,duration:0.5,ease:"power3.out"}},1.2);
tl.fromTo("#{cid}-u",{{opacity:0,y:16}},{{opacity:1,y:0,duration:0.5,ease:"power3.out"}},1.5);
tl.fromTo("#{cid}-p",{{opacity:0,y:12}},{{opacity:1,y:0,duration:0.5,ease:"power3.out"}},1.8);
tl.fromTo("#{cid}-by",{{opacity:0,y:12}},{{opacity:1,y:0,duration:0.5,ease:"power3.out"}},2.1);
tl.to("#{cid}-fade",{{opacity:1,duration:1.2,ease:"power1.in"}},{od-1.3:.2f});
'''
files["outro"] = scene(cid, od, body, js)

os.makedirs(f"{P}/compositions", exist_ok=True)
for k,v in files.items():
    open(f"{P}/compositions/{k}.html","w").write(v)
print("scenes written:", list(files))
