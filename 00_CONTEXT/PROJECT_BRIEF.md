# Project brief

Last updated: 2026-10-03 (repository cleanup and episode renumbering folded in)

## Show and hosts

**Out of Our Depth** is Josh Eiland and Mary's AI-focused show. Josh is a Stanford GSB MBA student and COO of Run Your City; Mary is Run Your City's founder and CEO. They are newlyweds at Stanford GSB learning AI out loud, with real experience building and operating organizations.

Help curious, busy professionals understand what is changing in AI, why it matters, and how to use it. Nonprofits and lean organizations supply examples; they do not define the whole audience. The hosts ask good questions, test tools honestly, and translate useful findings without pretending to be frontier researchers.

## Editorial rules

Make the show fun, accessible, and worth watching for Josh and Mary's relationship. Preserve real reactions, affectionate disagreement, interruptions and both hosts' substantive judgment. Mary is not a clueless sidekick. A useful lesson should support the conversation, not replace it.

Use plain spoken English, concrete examples and minimal jargon. Strong opinions may be spicy, but factual claims must be accurate, sourced and distinguished from personal experience. Direct host choices govern cuts; preserve the requested conversation and remove clear mistakes, mishaps, repetition or specifically unwanted material. Full direction: [editorial-direction.md](editorial-direction.md).

No emojis by default. Website episode titles match YouTube exactly, including capitalization and punctuation. Descriptions and chapters use visible HTTPS links; shared YouTube/Spotify chapters start at 00:00, have at least three chronological entries with at least 30 seconds between starts, and a final chapter at least 30 seconds long.

Standing production choices from Josh:

- **No pop-ups.** No definition/correction overlays over camera footage, and no teaching side notes on screen shares (2026-10-03).
- **Screen shares use layout C:** a large host window with an inset screen share and limited overlap, with no added teaching cards (2026-10-03).
- **Length:** most episodes land near 30 minutes. That's guidance, not a cap.
- **Covered-lens transitions:** begin after the intro with the hand already covering the lens, then uncover. At the close, end on the fully covered lens and cut to the outro before the hand withdraws.
- **Captions:** use YouTube/Spotify auto-captions for now. Still produce a proofread SRT with each episode as a backup, but don't upload it (2026-10-03).

Working content model: two main videos per week, one current-developments episode and one deep dive. This cadence remains a working assumption whose sustainability is open.

## Episodes

Numbering follows the public order on YouTube and Spotify (Josh, 2026-10-03). Every episode folder in [`01_EPISODES/`](../01_EPISODES/README.md) has the same layout; final videos and raw recordings live in Drive.

| # | Episode | Status | Length |
| --- | --- | --- | --- |
| 000 | We Can't Keep Up With AI Either (So We Started a Podcast!) | Published 2026-09-30 | 11:20.867 |
| 001 | Projects, Connectors & Skills… Take Your AI From Fresh Intern to Full-Time Hire | Published 2026-09-30 | 33:14.267 |
| 002 | Who's Who in AI (Explained With a Toyota Prius) | Published; re-uploaded without pop-ups 2026-10-03 | 52:25.733 |
| 003 | AI agents | Final cut ready per Josh; not yet published | 37:36.933 (v5) |
| 004 | El Cruce with an AI coach | Final cut ready per Josh; not yet published | 44:49.833 (v11) |
| 005 | Personalization | Planned | |
| 006 | Wedding planning with AI | Planned | |
| 007 | AGI | Planned | |

Before 2026-10-03, 001 and 002 were the other way round. Josh re-uploaded the no-pop-up AI basics cut, which made it the newest upload and moved it to second place on both platforms, so the numbering was changed to match. Older records and the decisions ledger use the old numbers and folder names (`E001-ai-basics`, `E002-make-ai-useful`).

The 002 re-upload has a new YouTube ID, `cp4P_2t5rRQ` (published 2026-10-03, 12:37 PT). The old ID `-YWPmoWKbrM` now returns 404, and the `release-record.json` in that folder still carries it as the original release.

Episode 003 was recorded 2026-10-03 from `Agents episode.mp4` (70:24.567). The cut uses Josh's shortened "me and my 400 agents" hook. Episode 004 was recorded 2026-10-02. Its cut uses layout C and the 9.1-second singing hook. On 2026-10-03 Josh said both cuts are ready and they were uploaded to Drive with captions and chapters. Public titles, release dates and publication for both remain open.

## Brand and reusable assets

The supplied brand kit is the visual source of truth; [brand-guidelines.md](../03_ASSETS/brand-guidelines.md) records kit rules and later host overrides. Use Teachers typography, the square two-line logo and blue/cream waterline. General kit colors: blue #38B6FF, cream #FBF1E5, foam #FDF8F2 and navy #0B2A45.

- **Intro/outro cards:** [`03_ASSETS/intro-outro-cards/`](../03_ASSETS/intro-outro-cards/README.md) ("Mono, Mirrored", three-digit). The intro tagline is **FIGURING OUT AI TOGETHER**, with no episode-number label. The outro has no top show label, and its three footer prompts are raised 48 pixels. The prompts read: LOVE IT? TELL MARY; HATE IT? TELL JOSH; HAVE AN IDEA FOR WHAT TO COVER NEXT? LET US KNOW.
- **Thumbnails:** Mary's paired-host format. [`03_ASSETS/thumbnail-template/`](../03_ASSETS/thumbnail-template/README.md) holds the editable format, and the current thumbnail for each episode is `thumbnail.png` in its folder.
- **Channel art:** [`03_ASSETS/channel-art/`](../03_ASSETS/channel-art/README.md). The main icon is a photo of Josh and Mary.
- **Caption glossary and fixer:** [`03_ASSETS/caption-glossary/`](../03_ASSETS/caption-glossary/README.md).
- **Brand kit, fonts and music** are in the repo (`03_ASSETS/brand-kit/`, `brand-fonts/`, `music/`). Josh confirmed music rights on 2026-09-28; the rights document itself is not in this repo.

Where every asset lives: [ASSET_MANIFEST.md](../03_ASSETS/ASSET_MANIFEST.md).

## Production

Use OBS and the Logitech camera at 1920 × 1080, with both OBS and Logi Tune set to 1080p. Leaving Logi Tune at 4K caused accumulating delay. A roughly 15-minute test at matching resolution showed little or no delay. Final microphone/gain/filter settings and a full-length sync check remain unresolved.

Use the four [production skills](../skills/README.md) and the [usage guide](production-skills-and-models.md) for planning, editing, visuals and release assets. Final exports require full decode, audio/sync/caption/chapter checks and the color and container compatibility gate. A technical pass does not establish platform acceptance or host approval.

Open questions are in [OPEN_QUESTIONS.md](OPEN_QUESTIONS.md). The chronological [DECISIONS.md](DECISIONS.md) holds the full history. [SYNC_STATE.md](SYNC_STATE.md) records the last ChatGPT Project reconciliation.

## Accounts, website and shared documents

Handles: YouTube/Instagram/TikTok @OutOfOurDepthPod (TikTok live again as of 2026-10-03), X @OutOfOurDepthX, [facebook.com/outofourdepthpod](https://facebook.com/outofourdepthpod) (live), [linkedin.com/company/outofourdepth](https://linkedin.com/company/outofourdepth).

[outofourdepth.com](https://outofourdepth.com) deploys from `website/` through the Vercel project `oood-website`. As of the 2026-10-03 deploy, it features 002 at the top, with 001 and then 000 under "More episodes". It shows only Instagram, X and email icons per Josh. TikTok, LinkedIn and Facebook are commented out in `website/config.js`. Details: [website/README.md](../website/README.md).

Josh planned a coordinated public announcement for October 3–4. The [October 1 launch primer](../04_PUBLISHING/codex-public-launch-primer-2026-10-01.md) has recommended channels and sequencing; those are recommendations, not adopted decisions.

Source documents: the [launch recording primer](https://docs.google.com/document/d/1gWK3_jPo7-Y5J_zjiGggAhPWY-EtNpHh5X3jszLH6bY/edit) and the [Marketing & Episodes Brainstorm](https://docs.google.com/document/d/1AvDfSBg6xxMyGNH7D9JhbGEzm3NP46459uxMoQDLSXc/edit). The brainstorm calls the launch episodes 1/2/3.
