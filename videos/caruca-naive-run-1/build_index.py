import json, os, html as H
def A(o): return '"'+H.escape(json.dumps(o,separators=(',',':')),quote=True)+'"'
P = os.path.dirname(os.path.abspath(__file__))
T = json.load(open(f"{P}/timeline.json"))
plan, vo, TOTAL = T["plan"], T["vo"], T["total"]
X, LEAD = 0.5, 1.2
VX, VW = 153, 1614
hosts, videos, vos, lthirds, marks, js = [], [], [], [], [], ['tl.set("#stage-fx",{filter:"blur(10px)"},0);']
track_g = 2
for kind, cid, start, dur, extra in plan:
    if kind == "g":
        hs = start if cid == "cover" else start - X
        hd = dur + (X if cid in ("cover", "outro") else 2 * X)
        hosts.append(f'''      <div id="host-{cid}" class="scene-host" data-composition-id="{cid}" data-composition-src="compositions/{cid}.html" data-start="{hs:.3f}" data-duration="{hd:.3f}" data-track-index="{track_g}" data-width="1920" data-height="1080"></div>''')
        track_g = 3 if track_g == 2 else 2
        if cid != "cover":
            js.append(f'tl.fromTo("#host-{cid}",{{opacity:0,filter:"blur(10px)",scale:0.98}},{{opacity:1,filter:"blur(0px)",scale:1,duration:{X},ease:"power2.inOut"}},{hs:.3f});')
        if cid != "outro":
            js.append(f'tl.to("#host-{cid}",{{opacity:0,filter:"blur(10px)",scale:1.02,duration:{X},ease:"power2.inOut"}},{hs+hd-X:.3f});')
        if extra:
            vos.append(f'''      <audio id="{extra}" class="clip" src="assets/audio/{extra}.mp3" data-start="{start+LEAD:.3f}" data-duration="{vo[extra]:.3f}" data-track-index="20" data-volume="0.75" data-audio-group="voices"></audio>''')
    else:
        a, label = extra
        n = cid[3:]
        lane = {"version":1,"lanes":[{"target":"volume","points":[{"t":0,"v":0},{"t":0.35,"v":1},{"t":round(dur-0.35,3),"v":1},{"t":round(dur,3),"v":0}]}]}
        videos.append(f'''        <video id="{cid}" class="clip rec" src="assets/walkthrough.mp4" data-start="{start:.3f}" data-duration="{dur:.3f}" data-media-start="{a:.3f}" data-track-index="1" data-audio-group="voices" playsinline data-has-audio="true" data-automation={A(lane)}></video>''')
        js.append(f'tl.to("#stage-fx",{{filter:"blur(0px)",duration:{X},ease:"power2.inOut"}},{start-X:.3f});')
        js.append(f'tl.to("#stage-fx",{{filter:"blur(10px)",duration:{X},ease:"power2.inOut"}},{start+dur:.3f});')
        num, text = label.split(" · ", 1)
        lthirds.append(f'''      <div id="lt-{n}" class="clip lthird" data-start="{start+0.8:.3f}" data-duration="7" data-track-index="5"><div class="lt-inner" id="lt-{n}-in"><div class="lt-num">Chapter {num}</div><div class="lt-text">{text}</div><div class="lt-bar" id="lt-{n}-bar"></div></div></div>''')
        js.append(f'tl.fromTo("#lt-{n}-in",{{opacity:0,x:-40}},{{opacity:1,x:0,duration:0.5,ease:"power3.out"}},{start+0.9:.3f});')
        js.append(f'tl.fromTo("#lt-{n}-bar",{{scaleX:0}},{{scaleX:1,duration:0.6,ease:"power3.out"}},{start+1.1:.3f});')
        js.append(f'tl.to("#lt-{n}-in",{{opacity:0,x:-20,duration:0.4,ease:"power2.in"}},{start+7.3:.3f});')
        if False: marks.append(f'''      <img id="wm-{n}" class="clip wm" src="assets/logo.png" alt="" data-start="{start:.3f}" data-duration="{dur:.3f}" data-track-index="6"/>''')

# music beds: 180 s track, looped with 1 s crossfades
beds = []
starts = [0.0, 179.0, 358.0, 537.0]
LOW, HIGH = 0.09, 0.30
for i, s in enumerate(starts):
    d = min(180.0, TOTAL - s)
    if i == 0:
        pts = [(0,0),(1.0,HIGH),(5.4,HIGH),(6.6,LOW),(179,LOW),(180,0)]
    elif i < 3:
        pts = [(0,0),(1,LOW),(179,LOW),(180,0)]
    else:
        vo6_end = (plan[-1][2] + LEAD + vo["vo6"]) - s
        pts = [(0,0),(1,LOW),(vo6_end+0.1,LOW),(vo6_end+0.7,0.2),(d-1.6,0.2),(d,0)]
    lane = {"version":1,"lanes":[{"target":"volume","points":[{"t":round(t,3),"v":v} for t,v in pts]}]}
    beds.append(f'''      <audio id="music-bed-{i+1}" class="clip" src="assets/audio/music_bed.mp3" data-start="{s:.3f}" data-duration="{d:.3f}" data-track-index="{30+i%2}" data-audio-group="music" data-automation={A(lane)}></audio>''')

master = {"version":1,"nodes":[
  {"type":"gain","id":"m1","label":"Loudness lift","params":{"gain":8}},
  {"type":"compressor","id":"m2","label":"Glue","params":{"threshold":-20,"ratio":2.5,"attack":15,"release":200,"knee":2.83,"makeup":0,"mix":1}},
  {"type":"truepeak","id":"m3","label":"Delivery ceiling","params":{"ceiling":-3,"lookahead":3,"release":80}}]}

html = f'''<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <title>Caruca: Naive LLM Run #1</title>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      @font-face {{ font-family: "Lexend Deca"; src: url("assets/fonts/LexendDeca-Regular.ttf") format("truetype"); font-weight: 400; font-style: normal; }}
      @font-face {{ font-family: "Lexend Deca"; src: url("assets/fonts/LexendDeca-SemiBold.ttf") format("truetype"); font-weight: 600; font-style: normal; }}
      @font-face {{ font-family: "Lexend Deca"; src: url("assets/fonts/LexendDeca-Bold.ttf") format("truetype"); font-weight: 700; font-style: normal; }}
      @font-face {{ font-family: "JetBrains Mono"; src: url("assets/fonts/JetBrainsMono-Regular.woff2") format("woff2"); font-weight: 400; font-style: normal; }}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1920px; height: 1080px; overflow: hidden; background: #0b1f33; }}
      #main {{ position: relative; width: 100%; height: 100%; overflow: hidden; font-family: "Lexend Deca", sans-serif; }}
      #main .backdrop {{ position: absolute; inset: 0; background: radial-gradient(900px 700px at 0% 100%, rgba(14,116,144,0.25), rgba(11,31,51,0) 70%), #0b1f33; }}
      #main #stage {{ position: absolute; left: {VX}px; top: 0; width: {VW}px; height: 1080px; overflow: hidden; }}
      #main #stage-fx {{ position: absolute; inset: 0; will-change: filter; }}
      #main video.rec {{ position: absolute; left: 0; top: 0; width: {VW}px; height: 1080px; object-fit: contain; }}
      #main .scene-host {{ position: absolute; inset: 0; z-index: 10; }}
      #main .lthird {{ position: absolute; left: 190px; bottom: 64px; z-index: 8; }}
      #main .lt-inner {{ position: relative; background: rgba(11,31,51,0.92); border: 1px solid #27476e; border-radius: 6px; padding: 18px 28px 22px; min-width: 620px; }}
      #main .lt-num {{ font-family: "JetBrains Mono", monospace; font-size: 18px; letter-spacing: 0.08em; text-transform: uppercase; color: #7dd3e8; }}
      #main .lt-text {{ font-size: 34px; font-weight: 600; color: #f4f7fb; margin-top: 6px; letter-spacing: -0.01em; }}
      #main .lt-bar {{ position: absolute; left: 28px; bottom: 10px; width: 120px; height: 4px; border-radius: 2px; background: linear-gradient(to right, #0e7490, #2563eb); transform-origin: left center; }}
      #main .wm {{ position: absolute; left: 1790px; top: 990px; width: 108px; height: 72px; object-fit: contain; opacity: 0.55; z-index: 6; }}
    </style>
  </head>
  <body>
    <div id="main" data-composition-id="main" data-start="0" data-width="1920" data-height="1080" data-duration="{TOTAL:.3f}" data-fx-chain={A(master)}>
      <div class="backdrop"></div>
      <div id="stage"><div id="stage-fx">
{chr(10).join(videos)}
      </div></div>
{chr(10).join(marks)}
{chr(10).join(lthirds)}
{chr(10).join(hosts)}
{chr(10).join(vos)}
{chr(10).join(beds)}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      {chr(10).join("      "+l for l in js).lstrip()}
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
'''
open(f"{P}/index.html","w").write(html)
print("index written, total", TOTAL)
