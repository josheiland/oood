# Archive

Superseded material kept for history. Day-to-day work never needs anything here. Use the live context, episode folders, skills and assets.

## Notes (in Git)

`notes/` has short records that explain how the repository got to its current state:

- `2026-10-03-episode-renumbering.md`: why 001 and 002 swapped, what was renamed locally and in Drive, and the website deploy
- `2026-10-03-jtan-disk-cleanup/`: media deleted on 2026-10-03, with a full file list, plus the Drive map at that time
- `2026-10-03-codex-disk-cleanup.md`: render caches deleted on 2026-10-03
- `asset-manifest-history-to-2026-10-03.md`: the old asset manifest, with every earlier version of every asset
- `project-brief-before-2026-10-03-cleanup.md`: the long-form brief before it was rewritten

## Full recovery (Drive)

**`OOOD project files backup 2026-10-03.zip`** is in the root of the OOOD Drive folder (MD5 `0d7c369d14e686b44473c62d461be4fa`, 9,020 entries). It is the complete repository as of 2026-10-03 ~20:00 PT, minus video/audio. That includes every versioned edit folder, hook and layout comparison, QC record and review page removed in the 2026-10-03 cleanup, plus a copy of the brand kit, fonts and music. Unzip it somewhere outside the repo and copy back only what you need.

Final videos and raw recordings are in Drive `Video Files/` (see `03_ASSETS/ASSET_MANIFEST.md`).

## Launch-era records

`2026-09-30-completed-launch-work.zip` (31 MB, in Git) preserves 1,075 launch-era files byte-for-byte at their original paths. `2026-09-30-consolidation-receipt.json` records its checksums. The helper lists entries by default and refuses to overwrite:

```sh
python3 scripts/restore-completed-work.py 01_EPISODES/E001-ai-basics/
python3 scripts/restore-completed-work.py 01_EPISODES/E001-ai-basics/ --restore
```

Restores land in `99_ARCHIVE/restored-launch-work/`. Paths inside it use the **old** episode numbers: `E001-ai-basics` is today's 002 and `E002-make-ai-useful` is today's 001. Never treat archived status or research as current without checking the live context.
