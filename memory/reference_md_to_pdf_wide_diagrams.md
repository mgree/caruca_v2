---
name: reference-md-to-pdf-wide-diagrams
description: The repo's md-to-pdf converter downscales relative-path images to 1,600 px, which blurs wide Excalidraw diagrams; absolute paths bypass it
metadata:
  type: reference
---

`npm run convert -- <file.md> [--title] [--subtitle]` (`scripts/md-to-pdf.ts`, Letter, portrait) is the
repo's Markdown-to-PDF converter; it writes the PDF beside the source and puts the source path on the cover.

Observed 2026-10-20 converting run 4's analysis (`naive_llm_caruca/runs/2026-10-20_112956_…/analysis/`):
`optimizeLocalImages` in `scripts/md-to-pdf/converter.ts` resizes every **relative** `.png/.jpg/.webp`
over `MAX_WIDTH = 1600` px, and skips any `src` starting with `/`. The run's Excalidraw renders are
7,000-8,400 px wide, so at 1,600 px their text is blurry even when zoomed. Workaround used (the converter
was not changed): temporarily rewrite the image links to absolute paths, convert, restore the `.md`
(checked with `cmp`). The result embedded all four diagrams at about 1,100 ppi (`pdfimages -list`),
crisp when zoomed; the PDF grew from 0.95 MB to 4.5 MB.

Not solved by this: wide landscape diagrams are still small on a printed portrait page (body text around
3-4 pt). They read well only on screen, zoomed.
