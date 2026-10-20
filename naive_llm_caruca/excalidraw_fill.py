#!/usr/bin/env python3
"""Expand a compact, hand-placed element list into a full .excalidraw file for a run analysis.

Fills only Excalidraw's per-element boilerplate (ids are yours; seeds, versions and flags are filled in)
and sizes free-floating text from its character count. Every position, colour and point is taken as
written, so the layout stays hand-made, as the Excalidraw skill asks.

    ./excalidraw_fill.py spec.json out.excalidraw
    cd ../.claude/skills/excalidraw-diagram/references && uv run python render_excalidraw.py <out.excalidraw>

Spec: a JSON list of elements, each {"type", "id", "x", "y", ...}:
  text       "text", optional "fs" (font size, default 16), "stroke" (colour), "align" ("left"; "center"
             and "right" treat x as the centre line or right edge)
  rectangle  "w", "h", optional "stroke", "fill", "style" ("solid"/"dashed"), "sw" (stroke width)
  ellipse    as rectangle
  line/arrow "points" [[0,0],[dx,dy],...] relative to x,y; arrows end in an arrowhead
Colours come from the skill's references/color-palette.md. Examples: every runs/*/analysis/<name>.spec.json
(runs 4 and 5) is the spec its <name>.excalidraw was built from; copy one to start a new diagram.
"""
import json, sys

spec = json.load(open(sys.argv[1]))
out, seed = [], 100000
for e in spec:
    seed += 2
    t = e["type"]
    base = {
        "id": e["id"], "type": t, "x": e["x"], "y": e["y"],
        "strokeColor": e.get("stroke", "#1e3a5f"), "backgroundColor": e.get("fill", "transparent"),
        "fillStyle": "solid", "strokeWidth": e.get("sw", 2), "strokeStyle": e.get("style", "solid"),
        "roughness": 0, "opacity": 100, "angle": 0, "seed": seed, "version": 1, "versionNonce": seed + 1,
        "isDeleted": False, "groupIds": [], "boundElements": None, "link": None, "locked": False,
    }
    if t == "text":
        lines = e["text"].split("\n"); fs = e.get("fs", 16)
        base.update({
            "text": e["text"], "originalText": e["text"], "fontSize": fs, "fontFamily": 3,
            "textAlign": e.get("align", "left"), "verticalAlign": "top", "containerId": None, "lineHeight": 1.25,
            "width": e.get("w", round(max(len(l) for l in lines) * fs * 0.6)), "height": round(len(lines) * fs * 1.25),
            "strokeWidth": 1,
        })
        if e.get("align") == "center":  # x given as the centre line
            base["x"] = e["x"] - base["width"] / 2
        if e.get("align") == "right":   # x given as the right edge
            base["x"] = e["x"] - base["width"]
    elif t in ("rectangle", "ellipse"):
        base.update({"width": e["w"], "height": e["h"]})
        if t == "rectangle": base["roundness"] = {"type": 3}
    elif t in ("line", "arrow"):
        pts = e["points"]
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        base.update({"points": pts, "width": max(xs) - min(xs), "height": max(ys) - min(ys)})
        if t == "arrow":
            base.update({"startBinding": None, "endBinding": None, "startArrowhead": None,
                         "endArrowhead": e.get("head", "arrow")})
            if len(pts) > 2: base["roundness"] = {"type": 2}
    out.append(base)

json.dump({"type": "excalidraw", "version": 2, "source": "https://excalidraw.com", "elements": out,
           "appState": {"viewBackgroundColor": "#ffffff", "gridSize": 20}, "files": {}},
          open(sys.argv[2], "w"), indent=1)
print(f"{len(out)} elements -> {sys.argv[2]}")
