# Disk cleanup — 2026-10-03 (jtan)

Josh asked to clear unneeded files from the agents and El Cruce folders and older episodes, and to free as much
space as possible, once the finals were ready. Free space went from 4.1 GB to about 21 GB after pass 1.

## Rule used

In `01_EPISODES/E000`–`E004`, every video/audio/cache media file was deleted (`.mp4 .mov .wav .m4a .aac .mkv
.webm .flac .mp3 .ts .npy`), plus `__pycache__` and empty folders, **except** the two finals:

- `E003-ai-agents/edit/codex-proposed-cut-2026-10-03/feedback-revision-v5/agents-feedback-cut-v5-audio-matched.mp4`
- `E004-el-cruce/edit/codex-personality-pass-2026-10-03/full-v5/el-cruce-personality-v11.mp4`

All small records were kept: edit lists, manifests, scripts, captions, chapters, notes, review pages, stills.
Old versions can be re-rendered from the raws on Drive plus these records.

`deleted-pass1.tsv` lists every deleted file with its byte size (180 files, 19.92 GB). Deleted: E003 v1–v4,
v5 (pre-audio-match) and opening previews; E004 v1–v4, personality v6/v8–v10, hook previews, intermediates and
audio work; the local E002 no-pop-up master (on Drive, MD5-verified) and the unselected 30:03 alternative; E001
audit/colour-fix renders; all source-review WAVs.

## Pass 2: NOT DONE (blocked by permissions)

These are all MD5-verified on Drive and safe to delete, but jtan's delete commands were denied, so they are still
on disk (~5.8 GB): `E004 …/full-v5/source-media/screen-A/B/C.mov` (copies of the Desktop screen recordings,
whose originals are also in iCloud) and the camera originals in `~/Movies` (`Agents episode.mp4`,
`2026-10-02 *.mp4`).

## Where everything is now (Drive: `Out of Our Depth (OOOD)/`)

- `Video Files/Final/E000…E004/`: final MP4, SRT, description/chapters, current thumbnail (`-previous.jpg` = old)
- `Video Files/Raw/`: `Episode 0/1/2/3 Raw.mp4`, `Episode 1 Raw - vOld1/2`, `Episode 4 Raw/` (4 camera files + 3 screen recordings)
- `Channel Art/`: `Icon.jpg` (main), `YouTube Splash.png`, `Text Icon (old main icon).png`, `Thumbnails/`
- `OOOD project files backup 2026-10-03.zip`: the whole repo without video/audio, plus all of `03_ASSETS`
  (music stings, fonts, cards, templates), `.git`, the 99_ARCHIVE and the uncommitted working tree
