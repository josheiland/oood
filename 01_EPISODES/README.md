# Episodes

Numbering follows the public order on YouTube and Spotify (changed 2026-10-03, see `00_CONTEXT/DECISIONS.md`).

| # | Folder | Title | Status |
|---|---|---|---|
| 000 | [E000-why-were-here](E000-why-were-here/README.md) | We Can't Keep Up With AI Either (So We Started a Podcast!) | Published |
| 001 | [E001-make-ai-useful](E001-make-ai-useful/README.md) | Projects, Connectors & Skills… Take Your AI From Fresh Intern to Full-Time Hire | Published |
| 002 | [E002-ai-basics](E002-ai-basics/README.md) | Who's Who in AI (Explained With a Toyota Prius) | Published (no-pop-up re-upload) |
| 003 | [E003-ai-agents](E003-ai-agents/README.md) | AI agents (title TBD) | Final cut ready, unpublished |
| 004 | [E004-el-cruce](E004-el-cruce/README.md) | El Cruce with an AI coach (title TBD) | Final cut ready, unpublished |

Planned next: 005 personalization, 006 wedding planning with AI, 007 AGI.

## Folder layout

Every episode uses the same layout. Create only what the episode needs.

```text
E00X-short-slug/
├── README.md                     status, links, what's here
├── BRIEF.md                      from templates/EPISODE_BRIEF_TEMPLATE.md
├── thumbnail.png                 current 1280x720 thumbnail
├── captions.srt                  proofread backup captions (not uploaded; platforms auto-caption)
├── description-and-chapters.txt  saved description and chapters
├── release-record.json           published episodes: IDs, checksums, Drive file IDs
├── prep/                         primers, recording cues
└── edit-record/                  record of the final cut: edit list, manifest, omitted ranges,
                                  claim checks, handoff, build scripts
```

Final videos and raw recordings never go in Git. They live in Drive `Out of Our Depth (OOOD)/Video Files/Final/` and `Raw/` (see `03_ASSETS/ASSET_MANIFEST.md`). While an episode is being edited, put working renders and versions in `edit/` (the media is gitignored). When the cut is final, keep the record in `edit-record/` and move the rest out.

`edit-record/scripts/` holds every script from the original working folders, under their original folder names. That covers transcription, cut planning, rendering, captions, review pages and verification, so the full pipeline can be rerun or adapted. Other `edit-record/` files were copied from those folders. Links inside them may point at files that are now only in the Drive backup zip (see `99_ARCHIVE/README.md`).

## Status vocabulary

`idea` → `researching` → `outlined` → `scripted` → `ready-to-record` → `recorded` → `editing` → `scheduled` → `published`

Never advance status without confirmation or direct evidence.
