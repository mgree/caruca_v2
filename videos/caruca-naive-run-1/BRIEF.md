---
workflow: general-video
flow: automation
storyboard: no
message: "A fresh Claude Code session, given only a problem statement, describes grep well enough for a shell parallelizer — here is how run #1 went"
destination: youtube
aspect: 1920x1080
language: en
audience: "YouTube visitors: researchers and engineers curious about LLM-driven specification mining"
length: "~9 min (7.5 min source recording plus narrated interstitials)"
angle: walkthrough
voice: elevenlabs-brian
---

## Intent

A YouTube edit of Tiran Dagan's screen recording of the first naive Claude Code run of Caruca v2
(the `grep` command, prompt version 1, 2026-10-13). The recording keeps its own narration; the edit
adds a branded cover in the first 5 seconds ("Caruca: Naive LLM Run #1, by Tiran Dagan"), a music bed
that never competes with speech, short narrated interstitials between chapters with graphics that
visualise what the walkthrough shows (clone → run → collect, the output files, the eight-phase
session timeline, the run's numbers), chapter lower-thirds, and an end card. Tone: the Caruca brand —
a rigorous, academic instrument; precise, no hype.

## Assets

- assets/walkthrough.mp4 — the 7:31 screen recording (1614x1080, 60 fps, with Tiran's narration); the spine of the edit.
- assets/transcript.srt — regenerated, accurate transcript of the recording (source of the chapter cuts and the YouTube transcript).
- assets/logo.png — Caruca mark (pickaxe mining a navy cube).
- assets/fonts/ — Lexend Deca 400/600/700 + JetBrains Mono (brand type, embedded via @font-face).
- ../../naive_llm_caruca/runs/2026-10-13_193448_naive-run-grep_grep_PROMPT_v1/analysis/analysis.md — facts for the interstitial graphics (phases, durations, cost, tool calls).

## Customizations

- Cover card 0–5 s with the title; the same frame exported as the YouTube thumbnail (1280x720 PNG).
- ElevenLabs TTS narration (voice "Brian", eleven_multilingual_v2) on each interstitial; ElevenLabs Music instrumental bed, carved under both Tiran's voice and the narrator.
- Chapter lower-thirds at the start of each recording segment.
- YouTube description file with clickable chapter timecodes and the full transcript (adjusted to the edit's timeline).

## Notes

- Autonomous run: the user is not available mid-task. Decisions with receipts are listed in the handoff.
- Brand: ink #0B1F33, blue #2563EB, teal #0E7490; Lexend Deca + JetBrains Mono; no emoji, no exclamation marks, sentence case.
- Recording is 1614 px wide: letterboxed on an ink background inside 1920x1080, never cropped or stretched.
- Recording audio leveled (user feedback 2026-10-13, "not balanced"): the source swings from about -38 LUFS (first two minutes) to -23 LUFS. `assets/audio/recording_voice.m4a` is a mono rebuild (high-pass 90 Hz, adaptive denoise, slow leveling, soft gate, two-pass loudnorm to -21 LUFS); every segment now measures -20.7 to -22.2 LUFS. Video clips play muted; this track plays in their place. Narrator at full level (-21.6 LUFS).
- Narration voice changed to ElevenLabs voice id zs057lc0shdaAFXkm2Fm (user request).
