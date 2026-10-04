# Episode renumbering — 2026-10-03 (jtan handoff)

Josh directed this on 2026-10-03. jtan made the folder and Drive changes below but did **not** edit
PROJECT_BRIEF, DECISIONS, OPEN_QUESTIONS or ASSET_MANIFEST, because Codex was editing them at the time.
Codex: fold this into those files, then this note can move to `99_ARCHIVE/`.

## Why

Josh re-uploaded the full 52:25 no-pop-up AI basics episode to YouTube and Spotify. The re-upload made it
the newest upload, so it now appears **second** on both platforms, after "Make AI useful". Numbering now
follows the public order.

## Canonical numbering

| # | Episode | Status |
|---|---|---|
| 000 | Welcome / why we're here | published |
| 001 | Projects, connectors & skills (make AI useful) | published (formerly 002) |
| 002 | AI landscape / who's who in AI | published, re-uploaded no-pop-up 52:25 (formerly 001) |
| 003 | AI agents | in review |
| 004 | El Cruce with an AI coach | in production (no longer provisional) |
| 005 | Personalization | planned |
| 006 | Wedding planning with AI | planned |
| 007 | AGI | planned |

This resolves the E001 replacement choice (the 52:25 no-pop-up version, not the 30:03 alternative) and
the El Cruce public-numbering question.

## What jtan changed

**Local (`01_EPISODES/`):** `E001-ai-basics/` → `E002-ai-basics/`; `E002-make-ai-useful/` →
`E001-make-ai-useful/`. Contents untouched. Files inside keep their old names (e.g.
`edit/codex-no-popups-2026-10-03/episode-001-no-popups.mp4` is now under `E002-ai-basics/`), and
historical logs/JSON inside still cite the old paths. Links in the brief, OPEN_QUESTIONS, 01_EPISODES/README,
ASSET_MANIFEST, 02_RESEARCH and DECISIONS that point at the old folder names are now broken. Update the
live docs; leave DECISIONS history as written and add a dated entry.

**Drive (`Out of Our Depth (OOOD)/Video Files/`), renamed by file ID, contents unchanged:**
- `Final/E001-ai-basics` → `Final/E002-ai-basics`, its `episode-001.*` files → `episode-002.*`
- `Final/E002-make-ai-useful` → `Final/E001-make-ai-useful`, its `episode-002.*` files → `episode-001.*`
- `Raw/Episode 1 Raw.mp4` (AI basics) → `Episode 2 Raw.mp4`
- `Raw/Episode 2 Raw.mp4` (make-AI-useful reshoot) → `Episode 1 Raw.mp4`
- `Raw/Episode 2 Raw - vOld1` → `Episode 1 Raw - vOld1`; `Episode 2 Raw - vOld2.mp4` → `Episode 1 Raw - vOld2.mp4`

The `archive-manifest.json` inside each renamed Final folder still lists the old filenames (sizes and
MD5s are unchanged).

⚠ **The Drive backup for 002 is the 9/30 version with pop-ups (1,017 MB), not the re-uploaded no-pop-up
version.** The published file is only local, at `E002-ai-basics/edit/codex-no-popups-2026-10-03/`.

## Website, deployed to production 2026-10-03 ~19:40 PT (jtan)

Edited `website/` in place (on top of the uncommitted 9/30 changes, which were already live) and deployed
from a website-only staging copy, so `README.md` is not served. Production: `dpl_5fqPzc178RNv7G7vsac4kJT1MX4D`.
Rollback: `vercel rollback` to `oood-website-7r88s8o62` (the 9/30 deploy).
- **Socials:** only Instagram, X and email icons, per Josh. TikTok/LinkedIn/Facebook are commented out in `config.js`.
- **Episodes:** the featured latest episode is 002 Who's Who on the new ID `cp4P_2t5rRQ` (published 2026-10-03 12:37 PT).
  The old `-YWPmoWKbrM` returns 404 and was the live "More episodes" link until this deploy. More episodes is 001 Projects, then 000.
- **Phones (≤640px):** Josh's hero cutout is scaled up and raised (`left 45.5cqw; top .5cqw; width 70cqw`), so the stage
  bottom cuts at ~455px of `josh.webp`, above the diagonal edge (~475px). The chin stays at the old height relative to
  DEPTH. The tagline flows into two lines, breaking before "Stanford GSB" (measured with Teachers 700 at
  320–640px). More-episodes thumbnails are hidden.

## Drive backup for 002 (jtan)

Uploaded the re-uploaded no-pop-up master (`E002-ai-basics/edit/codex-no-popups-2026-10-03/episode-001-no-popups.mp4`,
2,058,534,021 bytes, MD5 `6bbda852ffc189906da26b5e8b1b22ea`) to `Final/E002-ai-basics/` as `episode-002.mp4`. The 9/30
pop-up version stays alongside it as `episode-002-with-popups-2026-09-30.mp4`. Nothing was deleted. The SRT and
description are byte-identical between the two versions, so they were left alone.

## Finals, raws, channel art and cleanup (jtan, evening)

Josh said the agents (003) and El Cruce (004) finals are ready: `agents-feedback-cut-v5-audio-matched.mp4` and
`el-cruce-personality-v11.mp4` (the same files as Codex's `codex-drive-review-upload-2026-10-03/local-inventory.json`;
the Drive "Episode Review — 2026-10-03" folder was empty when checked). Both are on Drive in
`Video Files/Final/E003-ai-agents` and `E004-el-cruce` with SRT and chapters, plus raws in `Video Files/Raw`, all
MD5-verified. All other local episode media was deleted at Josh's request; receipt and full Drive map in
`99_ARCHIVE/jtan-disk-cleanup-2026-10-03/README.md`. New channel art (photo icon, YouTube splash, five
thumbnails) is in `03_ASSETS/channel-art/`, mirrored to Drive `Channel Art/`; the blue tile is kept as
`Text Icon (old main icon).png`. Each episode folder has `thumbnail.png` (old ones are `thumbnail-previous.jpg`).
ASSET_MANIFEST needs these locations.

## Other state changes from Josh, same day

- TikTok @outofourdepthpod is live again. facebook.com/outofourdepthpod is live and accessible.
  LinkedIn is linkedin.com/company/outofourdepth.
- Captions: YouTube/Spotify auto-captions for now. Keep producing proofread SRTs with each episode as a
  backup, but don't upload them.
