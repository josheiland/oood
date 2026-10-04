---
name: oood-brand-visuals
description: Create or review OOOD podcast popups, chapter cards, lower thirds, thumbnails, and social graphics using the supplied blue-and-cream Teachers brand kit.
---

# OOOD brand visuals

Read live `03_ASSETS/brand-guidelines.md` and `brand-tokens.json` when available; otherwise use [brand guide](references/brand-guide.md) and `assets/brand-tokens.json`. The source ZIP was supplied and adopted by Josh on 2026-09-25. Read [editorial direction](references/editorial-direction.md) for tone. Live instructions override snapshots.

Inspect original artwork and the actual target frame before modifying or compositing it. The kit contains older assets that conflict with its current instructions: the primary icon is square and two-line, not `icon-circle.png`. Preserve originals; do not infer approved variants from filenames. Do not invent host photos or redraw the logo with generative imagery.

Use Teachers, the kit colors, and the cream/foam waterline. Render typography and exact brand geometry deterministically in vector/layout tools. AI image generation may help a specifically requested illustration or background, but must not replace exact type/logo composition or fabricate documentary evidence. If fonts are missing, resolve them or report the blocker; no silent font substitution in final assets.

## Decide what the graphic does

Choose one job: explain a term, identify a speaker, mark a chapter, clarify a source, reveal a real result, or support an actual joke. Don't plaster a lesson over host interaction. A reaction aside is editorial commentary, not an attributed quote. Never mock the audience. Let a joke land before adding an optional callback. Don't add effects to every sentence.

Use the kit's specific dimensions, safe areas, type rules, and motion for the relevant surface. Keep captions and faces unobstructed. On a transparent popup, the waterline belongs within the card. Ensure text contrast after reduction to the real viewing size. A title/card in all caps does not imply all prose should be uppercase.

## Generate and check

`scripts/render_card.py` makes a transparent definition/reaction popup or full-screen chapter card from the actual Teachers font. It produces editable JSON alongside PNG. It is a static asset helper; the kit's 24px chapter movement and 300ms lower-third wipe must be implemented and checked in the timeline if that motion is used. Read its `--help`. Use local `03_ASSETS/brand-fonts/teachers.ttf`, or bundled `assets/fonts/teachers.ttf` in a portable package.

For other layouts, author editable SVG/HTML/design files using the kit; rasterize/export as needed. Use real source-approved host cutouts. Do not use copyrighted example copy, invented episode outcomes, or sample “out now” labels as current facts.

Inspect the actual exports and one representative composite over footage. Check face/caption overlap, small-screen legibility, palette, type, logo clear space, and timing. Deliver editable sources, final exports, dimensions, cue timings when applicable, and a short QA note. State which checks ran. Preserve the original kit; propose additions as extensions rather than silently changing brand rules.
