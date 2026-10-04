# Out of Our Depth

Working repository for **Out of Our Depth**, an AI show hosted by Josh Eiland and Mary. Newlyweds at Stanford GSB learn AI out loud for curious, busy professionals. It's on YouTube and Spotify as @OutOfOurDepthPod, with the website at [outofourdepth.com](https://outofourdepth.com).

This repo is the project's memory: current state, durable decisions, the record of every episode, research, brand assets, production skills and the website. Final videos and raw recordings live in Google Drive, not here.

## Start here

1. [`AGENTS.md`](AGENTS.md): working rules for any AI collaborator (ChatGPT/Codex, Claude)
2. [`00_CONTEXT/PROJECT_BRIEF.md`](00_CONTEXT/PROJECT_BRIEF.md): current state of the show, episodes and standing choices
3. [`00_CONTEXT/OPEN_QUESTIONS.md`](00_CONTEXT/OPEN_QUESTIONS.md): what's undecided (don't decide it silently)
4. The newest entries at the bottom of [`00_CONTEXT/DECISIONS.md`](00_CONTEXT/DECISIONS.md)
5. [`00_CONTEXT/editorial-direction.md`](00_CONTEXT/editorial-direction.md) before any episode or editorial work

## Episodes at a glance

| # | Episode | Status |
|---|---|---|
| 000 | We Can't Keep Up With AI Either (So We Started a Podcast!) | Published |
| 001 | Projects, Connectors & Skills… Take Your AI From Fresh Intern to Full-Time Hire | Published |
| 002 | Who's Who in AI (Explained With a Toyota Prius) | Published |
| 003 | AI agents | Final cut ready, unpublished |
| 004 | El Cruce with an AI coach | Final cut ready, unpublished |
| 005–007 | Personalization · Wedding planning with AI · AGI | Planned |

Numbering follows public order. Before 2026-10-03, 001 and 002 were swapped, and older records use those old numbers.

## Structure

| Folder | What's in it |
|---|---|
| `00_CONTEXT/` | Project brief, decisions ledger, open questions, editorial direction, skills/model guide, sync state |
| `01_EPISODES/` | One folder per episode with the same layout: README, brief, thumbnail, captions, description/chapters, release record, `prep/`, `edit-record/`. See [its README](01_EPISODES/README.md). |
| `02_RESEARCH/` | Claim-level source logs and fact checks, indexed by episode |
| `03_ASSETS/` | Brand guidelines, intro/outro card templates, thumbnail template, channel art, caption glossary. [ASSET_MANIFEST.md](03_ASSETS/ASSET_MANIFEST.md) lists where everything lives, including Drive. |
| `04_PUBLISHING/` | Launch primer and episode slate |
| `skills/` | Four reusable production skills: episode planner, episode producer, brand visuals, release package. Linked for Codex in `.agents/skills/` and for Claude Code in `.claude/skills/`. |
| `templates/` | Episode brief, research note, publishing checklist |
| `scripts/` | Skill packager; launch-archive restore helper |
| `website/` | outofourdepth.com source (Vercel project `oood-website`) |
| `99_ARCHIVE/` | Notes on how the repo got here, plus pointers to the full Drive backup |

## Not in Git

These are gitignored and kept in Drive:

- video and audio
- the brand-kit source, the fonts and the theme music (`03_ASSETS/brand-kit/`, `brand-fonts/`, `music/`)
- the archive zips

A fresh clone has everything needed to understand the show and plan or write episodes. To render cards or thumbnails, or edit video, first copy those assets from the Drive backup (see [`99_ARCHIVE/README.md`](99_ARCHIVE/README.md)).

## Core rule

Keep the current truth concise. Record durable changes in `DECISIONS.md`, and don't silently rewrite history.
