# Out of Our Depth — working instructions

This repository is the explicit operational memory for the Out of Our Depth project.

## Before substantive work

1. Read `00_CONTEXT/PROJECT_BRIEF.md`.
2. Read the relevant recent entries in `00_CONTEXT/DECISIONS.md`.
3. Review `00_CONTEXT/OPEN_QUESTIONS.md`.
4. Read the README for the folder you will change.
5. Treat direct instructions from Josh or Mary as authoritative. If a direct instruction changes the current state, update the context files as part of the work.

## Source-of-truth rules

- `PROJECT_BRIEF.md` contains the concise current state, not a full history.
- `DECISIONS.md` is the chronological ledger of durable decisions and their rationale.
- `OPEN_QUESTIONS.md` contains unresolved choices; do not silently decide them.
- `SYNC_STATE.md` records when the ChatGPT Project context was last reconciled into this repo.
- Current files and dated decisions take precedence over old conversation excerpts.
- Never invent a decision, quote, source, status, metric, handle, or publication result.
- Separate confirmed facts, working assumptions, recommendations, and hypotheses.

## When work changes the project

- Update the relevant working file.
- If the change is durable, add a dated entry to `00_CONTEXT/DECISIONS.md`.
- If it changes the current state, revise `00_CONTEXT/PROJECT_BRIEF.md`.
- If it resolves or creates an open question, update `00_CONTEXT/OPEN_QUESTIONS.md`.
- Do not erase superseded decisions. Mark them superseded and link or name the replacement.
- Archive obsolete substantive documents in `99_ARCHIVE/`; do not use the archive for trivial drafts.

## Sync protocol

When asked to **"sync OOOD"**:

1. Read `00_CONTEXT/SYNC_STATE.md`.
2. Review available Out of Our Depth ChatGPT Project context since the recorded sync point.
3. Capture only durable facts, decisions, changed status, and unresolved questions.
4. Exclude transient brainstorming, rejected options, and unsupported inferences.
5. Update the four context files.
6. Set the reconciliation date and summarize changed files in `SYNC_STATE.md`.

If the current environment cannot access the ChatGPT Project history, say so clearly and do not pretend the sync is complete.

## Research standards

- For claims that can change, verify against current primary or high-quality sources.
- Record source URL, publisher, publication date, access date, and the exact claim supported.
- Prefer original reports, official product documentation, datasets, and filings over summaries.
- Flag weak, vendor-sponsored, self-reported, or non-comparable evidence.
- Never write a statistic into a script without leaving a traceable source in `02_RESEARCH/`.

## Episode standards

- One folder per episode: `01_EPISODES/E###-short-slug/`.
- Every episode starts with an episode brief based on `templates/EPISODE_BRIEF_TEMPLATE.md`.
- Distinguish factual claims from host opinions and personal experience.
- Optimize for spoken clarity: plain English, short sentences, concrete examples, and minimal jargon.
- Preserve Josh and Mary's natural voices; do not make them sound like generic AI presenters.
- Mark scripts as drafts until the hosts approve them.
- Do not claim an episode is recorded, edited, scheduled, or published without confirmation.

## File hygiene

- Use descriptive kebab-case names, except the established uppercase context filenames.
- Use ISO dates: `YYYY-MM-DD`.
- Keep raw media out of Git unless explicitly requested. Track its location in `03_ASSETS/ASSET_MANIFEST.md`.
- Do not commit credentials, API keys, private participant data, or licensed media.
- Preserve unrelated user changes and avoid destructive Git operations.
