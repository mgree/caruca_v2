---
format: 1920x1080
duration: ~9 min
message: "A fresh Claude Code session, given only a problem statement, describes grep well enough for a shell parallelizer — here is how run #1 went"
arc: Cover → What a naive run is → six recorded chapters, each introduced by a narrated graphic → By the numbers → End card
audience: YouTube visitors: researchers and engineers curious about LLM-driven specification mining
mode: autonomous
---

Design truth (no frame.md exists; brand from the caruca-design skill): background ink #0B1F33 tinted navy;
foreground #F4F7FB; accent blue #2563EB; secondary teal #0E7490; type Lexend Deca 700/400 for statements,
JetBrains Mono for commands, files and numbers. Decoratives: faint teal concentric rings bleeding off a
corner, hairline rules, the Caruca mark. Motion: restrained; the recording is the hero.
Transitions: blur crossfade (medium) between interstitials and recording segments; cut inside the recording.

## Frame 1 — Cover

- scene: Caruca mark, "Caruca: Naive LLM Run #1", "by Tiran Dagan", date and command chips
- duration: 5s
- poster: 3s
- transition_in: cut
- status: outline
- src: compositions/cover.html
- rules: waterfall-entry, ambient-glow-bloom

The title the user asked for, in the brand. Also exported as the YouTube thumbnail.

## Frame 2 — What a naive run is

- scene: Three inputs (problem statement, two format docs, worked examples) flow into a VM box holding Claude Code, which emits four files for grep
- duration: narration vo0
- transition_in: blur crossfade
- status: outline
- src: compositions/inter-0.html
- voiceover: vo0
- rules: spring-pop-entrance, svg-path-draw

## Frame 3 — Recording · Setup

- scene: recording 0:00–0:33.5, lower-third "1 · Setup: the README and the golden VM"
- transition_in: blur crossfade
- status: outline
- src: index.html (video clip seg1)

## Frame 4 — Clone and run

- scene: golden VM → clone → `naive-run-grep`, then a terminal line starting the run with prompt v1
- duration: narration vo1
- transition_in: blur crossfade
- status: outline
- src: compositions/inter-1.html
- voiceover: vo1
- rules: spring-pop-entrance, svg-path-draw, discrete-text-sequence (typed command)

## Frame 5 — Recording · Clone and start the run

- scene: recording 0:33.5–2:00.8, lower-third "2 · Clone the VM and start the run"
- status: outline
- src: index.html (video clip seg2)

## Frame 6 — Collect

- scene: a file tree of the run folder builds in: output/grep.py, output/pash/grep.json, two generator classes, stream.jsonl, transcript.jsonl, environment.txt
- duration: narration vo2
- transition_in: blur crossfade
- status: outline
- src: compositions/inter-2.html
- voiceover: vo2
- rules: waterfall-entry

## Frame 7 — Recording · Collect the output

- scene: recording 2:00.8–3:39.0, lower-third "3 · Collect the output and look at the run folder"
- status: outline
- src: index.html (video clip seg3)

## Frame 8 — Generate the analysis

- scene: transcript.jsonl → prompt → analysis.md + two diagrams
- duration: narration vo3
- transition_in: blur crossfade
- status: outline
- src: compositions/inter-3.html
- voiceover: vo3
- rules: spring-pop-entrance, svg-path-draw

## Frame 9 — Recording · Run the analysis prompt

- scene: recording 3:39.0–5:01.2, lower-third "4 · Ask Claude Code to analyse its own run"
- status: outline
- src: index.html (video clip seg4)

## Frame 10 — Eight phases

- scene: horizontal bar timeline of the eight phases with durations (4, 12, 103, 303, 63, 196, 31, 25 s), a marker at "first file written, 7 min"
- duration: narration vo4
- transition_in: blur crossfade
- status: outline
- src: compositions/inter-4.html
- voiceover: vo4
- rules: stat-bars-and-fills (progress fill, scaleX), waterfall-entry

## Frame 11 — Recording · The session timeline diagram

- scene: recording 5:01.2–6:26.9, lower-third "5 · The eight-phase session diagram"
- status: outline
- src: index.html (video clip seg5)

## Frame 12 — By the numbers

- scene: four stat tiles count up: 739 s, 72 tool calls, 85 probe runs, $0.96; model chip claude-haiku-5-5
- duration: narration vo5
- transition_in: blur crossfade
- status: outline
- src: compositions/inter-5.html
- voiceover: vo5
- rules: counting-dynamic-scale, spring-pop-entrance

## Frame 13 — Recording · The analysis document

- scene: recording 6:26.9–7:31.0, lower-third "6 · The written analysis and the final output"
- status: outline
- src: index.html (video clip seg6)

## Frame 14 — End card

- scene: mark, "Caruca v2", github.com/tirandagan/caruca_v2, "Run 2026-10-13 · grep · prompt v1"; fades to ink
- duration: narration vo6 + 2s
- transition_in: blur crossfade
- status: outline
- src: compositions/outro.html
- voiceover: vo6
- rules: spring-pop-entrance, ambient-glow-bloom
