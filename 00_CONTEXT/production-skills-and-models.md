# OOOD skills and model guide

Prepared 2026-09-26. Recommendations are practical starting points, not comparative benchmark results. The skills do not switch models automatically. Select the model in the app where you run the task.

## Start here

Use the local Codex project as the production workspace. It can operate on the raw recordings already on this computer. Use Claude for a second editorial perspective or run the same skills in Claude Code with access to the repository. A web chat can help with a transcript and selected frames, but that alone does not render or review a full video.

The reusable skills have separate jobs so a short copy request doesn't load the whole editing workflow:

| Skill | What you get | Suggested default | When to spend more |
|---|---|---|---|
| `$oood-episode-planner` | Research-backed brief, entertaining outline, host prompts, short recording cue sheet; reshoot feedback when relevant | GPT-6 Sol, Medium; Claude Opus 5.5, Medium/High as an alternate | GPT-6 Astra, High/Extra high for a complex story or a difficult editorial rethink |
| `$oood-episode-producer` | Actual video assembly, dialogue finishing, branded graphic integration, captions/chapters, source checks, reproducible edit and review package | GPT-6 Sol, High in local Codex; Claude Opus 5.5, High/Extra high in Claude Code as an alternate | Astra, High/Extra high for difficult source reconciliation, nuanced cuts, or stubborn pipeline problems |
| `$oood-brand-visuals` | Popups, chapter cards, lower thirds, thumbnails, and social layouts using the supplied kit | GPT-6 Sol, Medium for execution; Claude Sonnet 5 or Opus 5.5 for design iteration | Astra for complex layout/asset reasoning. Use an image-generation tool only for a requested illustration/background; exact type and logos stay deterministic |
| `$oood-release-package` | Actual clips if requested, corrected captions, titles, thumbnails, descriptions, show notes and platform drafts | GPT-6 Sol, Medium; Claude Sonnet 5 for quick copy alternatives | Opus 5.5 or Astra for a high-stakes launch pass or a nuanced clip-selection review |

GPT-6 Luna is useful for tightly scoped mechanical changes to approved copy or inventories. Don't make it the sole judge of comic timing, ambiguous claims, or a final episode. Claude Fable 5.1 is another documented high-end option, but there is no demonstrated need to start there for OOOD. Use it only if available on your plan and Opus falls short on a concrete difficult task. These mappings are editorial/workflow recommendations, not claims that one vendor is proven funnier.

OpenAI describes Sol as an everyday model for writing/coding/judgment and Astra for demanding analysis; Anthropic describes Opus 5.5 for long-running knowledge/agent work, Sonnet 5 for speed/intelligence, and Fable 5.1 for more demanding reasoning. Actual model menus and access depend on account and surface. Checked official sources are in [the source log](../02_RESEARCH/production-model-source-log-2026-09-26.md).

## Subscription recommendation

**Start with the subscriptions you already have. Do not upgrade both just to run these skills.** Josh reports ChatGPT and Claude Pro; the exact ChatGPT tier has not been confirmed in this task.

- If ChatGPT is Plus and long local editing sessions repeatedly hit limits, upgrading the account doing the production work is the first thing to consider. OpenAI currently lists Pro from $100/month, with 5x or 20x higher limits than Plus. If already on Pro, use Sol for routine execution and Astra selectively before buying more capacity. [OpenAI pricing](https://learn.chatgpt.com/docs/pricing).
- Keep Claude Pro initially for planning, dialogue/outline alternatives, and a second editorial perspective. If that becomes daily heavy work and Pro repeatedly interrupts it, Claude Max 5x is $100/month; Max 20x is $200/month. Both remain limited plans. Start with 5x if an upgrade is actually needed. [Claude Max](https://support.claude.com/en/articles/11049741-what-is-the-max-plan).
- A higher plan buys usage/capability access, not a guarantee of a better edit. It does not make local FFmpeg encoding run faster. Rendering performance depends on the machine, encoder, source, and effects; agent reasoning and transcoding are different parts of the job.
- The included scripts run locally without model API calls. Any future paid transcription, image-generation, or model API workflow needs its own access/billing check. Do not assume a consumer subscription covers arbitrary external API calls.

Run one finished episode through the workflow before deciding on more spend. Note where the bottleneck was: model usage, source quality, transcription, render time, or editorial indecision. Upgrade only the part that is actually limiting you.

## How to use the skills

**In this Codex project:** use the `$` name or ask naturally. Canonical files are under `skills/`; project discovery links are under `.agents/skills/`. If the selector has not refreshed, open a new task in this project or reference the SKILL.md directly.

Examples:

```text
Use $oood-episode-planner to prepare Episode 0. Make the conversation fun and help people get to know us as a couple. Give us a short recording outline, not a memorized script.

Use $oood-episode-producer on [absolute raw-video path] for Episode 0. Make the complete episode and release-review package. Preserve our chemistry, use the OOOD brand, and flag anything that still needs our approval.

Use $oood-brand-visuals to create three brief popups for these moments. Keep our faces and captions clear and use the current brand kit.

Use $oood-release-package on [final episode path]. Make three strong clips if the footage supports them, plus titles, a thumbnail direction, show notes, and draft social copy.
```

**In Claude Code:** open this repository. The `.claude/skills/` links expose the same sources; invoke by name or ask naturally. Local media processing still requires the needed tools and file access.

**In Claude chat/Cowork:** first run `python3 scripts/package-oood-skills.py` to generate them (they are not committed, and the brand-visuals package needs the local `03_ASSETS/brand-fonts/`), then upload the individual ZIPs in `exports/skills/` through Customize → Skills → create/upload, then enable them. The ZIPs contain each skill and portable brand/editorial/context snapshots; the visual skill also includes the font files and licenses. Uploading was not performed in this task. Claude's official [skill instructions](https://support.claude.com/en/articles/12512180-use-skills-in-claude) describe setup and prerequisites. Local large-video production is best kept in Codex or Claude Code with direct file access; a skill upload alone does not grant that access.

Generated upload packages: `exports/skills/oood-episode-planner.zip`, `oood-episode-producer.zip` (with video color gate), `oood-brand-visuals.zip`, `oood-release-package.zip` (with Spotify chapter check).

Portable context can go stale. The live repository is authoritative. Rebuild packages after important context or brand changes with `scripts/package-oood-skills.py`; re-upload changed packages to Claude as needed. No automatic cross-app memory synchronization is implied.

## What “episode generator” means here

This is an agent workflow with tools, not a button that invents a finished episode from unseen media. Given a raw recording, it inventories and transcribes the source, chooses reversible cuts, preserves the hosts' interplay, finishes the sound, creates the required branded graphics, renders the episode, checks the output, and delivers captions/chapters and review notes. The included reusable renderer handles the baseline assembly and audio/QC mechanics; the agent handles editorial decisions and additional finishing.

An export is only called ready to publish after the relevant technical/factual checks and your approval of that exact version. The skill still completes the actual export before presenting it for review. It does not automatically post or send anything.

## Validation performed

**Shared description chapters (Josh, 2026-09-30):** Use the stricter Spotify-compatible spacing for OOOD YouTube/Spotify copy: first start 00:00, at least three chronological plain-text chapters, at least 30 seconds between chapter starts. Keep the final chapter at least 30 seconds long as an OOOD default, consistent with Spotify's advice to merge shorter chapters. Merge adjacent short topics while preserving their real final-export anchors; do not invent delayed starts. Verify these intervals before handoff. [Spotify's official guidance](https://support.spotify.com/us/creators/article/episode-chapters/) was checked 2026-09-30.

All four skills passed the skill-creator validator; portable ZIP integrity and repository discovery links were checked. The package has a tested baseline media renderer and a tested branded-card renderer. The media smoke test used a synthetic 8-second source, assembled two ranges into a 5-second export with chapters, and passed full decode, frame count, duration, chapter metadata, audio/video duration agreement, source-integrity, encoded loudness, and peak checks. An independent forward test also rendered the supplied test plan; its findings prompted stricter dimension validation and clearer timing documentation. Invalid dimensions, out-of-range cuts, and selecting video as audio are rejected. Static card exports were inspected using the actual Teachers font; a definition popup was checked over a frame of the prior recording. Motion and new-episode captions were not tested. This is not an end-to-end test on the as-yet-unrecorded weekend episodes, nor proof that every future source format will work unchanged.


## Video color export gate (2026-09-30)

Josh requested prevention after repeat Spotify rejections. The initial metadata-only E002 repair passed color checks but Josh reported the same rejection. Expanded audit found three unsupported MP4 edit lists and a changing aspect-ratio SPS declaration at the intro, despite uniform color tags. Every final H.264 SDR upload copy must now pass the producer's `scripts/color_qc.py`, which checks complete SPS/PPS configurations, MP4 color/sample boxes and absence of edit lists, and every decoded frame's color and picture properties. `media_job.py render` and `qc` enforce this gate. Spotify delivery uses a single continuous final encode, no B-frame timing delay, one-second keyframes and no edit lists; audio sync and final captions/chapters must be checked. Genuinely different colors require conversion, not relabeling. These are technical compatibility checks, not proof of successful platform processing or publication. See [Spotify's specifications](https://support.spotify.com/us/creators/article/video-specs/) (accessed 2026-09-30).
