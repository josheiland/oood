# Asset manifest

Current as of 2026-10-03. This lists what exists now and where. The full history of earlier, mostly deleted assets is in [`99_ARCHIVE/notes/asset-manifest-history-to-2026-10-03.md`](../99_ARCHIVE/notes/asset-manifest-history-to-2026-10-03.md).

**In Git** means the file is in this repository. **Local only** means it's gitignored. It's on the production laptop and in the Drive backup zip, but a fresh clone won't have it.

## Brand and production assets

| Asset | Location | In Git? | Notes |
|---|---|---|---|
| Brand rules digest | `03_ASSETS/brand-guidelines.md`, `brand-tokens.json` | Yes | Kit rules plus later host overrides. Read before any graphic or public copy. |
| Brand kit source (design kit HTML, banners, icons, Mary's uploads) | `03_ASSETS/brand-kit/` | Local only | Extracted from `Out of Our Depth Brand Kit.zip`, SHA-256 `39224df9937d2101eac0d1c48c67b1e95a68942b1d5813dc06f57af3b82341db`. Visual source of truth. |
| Fonts: Teachers, JetBrains Mono | `03_ASSETS/brand-fonts/` | Local only | Google Fonts, OFL licences included. Needed by the card and thumbnail renderers and the brand-visuals skill package. |
| Intro/outro cards ("Mono, Mirrored", three-digit) | `03_ASSETS/intro-outro-cards/` | Yes | SVG templates, JSON copy, renderer, 1080p PNG stills. Tagline FIGURING OUT AI TOGETHER. |
| Thumbnail format (Mary's paired-host layout) | `03_ASSETS/thumbnail-template/` | Yes | Editable SVG, JSON, renderer, Josh's clean photo (SHA-256 `3ff8be1e751231d5c809399223c24791cb744ad79777c0d6bc96006630bc0298`). |
| Caption glossary and fixer | `03_ASSETS/caption-glossary/` | Yes | Fixes recurring ASR mistakes (Chad→Chat, cloud→Claude, etc.). |
| Channel art | `03_ASSETS/channel-art/` | Yes | `Icon.jpg` (main icon), `YouTube Splash.png`, `Text Icon (old main icon).png`. Mirrored in Drive `Channel Art/`. |
| Episode thumbnails | `01_EPISODES/E00X-*/thumbnail.png` | Yes | Current 1280×720 thumbnails. Also in Drive `Channel Art/Thumbnails/` and each Final folder. Earlier thumbnails are in Drive only. |
| Theme music, sting, outro | `03_ASSETS/music/` (`oood-theme-option-1-original.m4a`, `oood-sting-5s.wav`, `oood-outro-11s.wav`) | Local only | "OOOD - Option 1", 24.8 s, generator Free plan. Josh confirmed rights 2026-09-28; the rights document is not in the repo. |
| OBS scene collection | — | — | Not yet exported. Sanitize paths and devices before committing. |

## Episode media (all in Drive, nothing local)

Drive root: **Out of Our Depth (OOOD)** (`1Go6MaIuE0OY_ZePvNVdQgehdh8uZGtf-`) in Josh's personal Google Drive.

| Episode | Final folder (`Video Files/Final/`) | Contents |
|---|---|---|
| 000 | [`E000-why-were-here`](https://drive.google.com/drive/folders/1BtzCXPB2v8w1y7SWS3PoUIzOsoKfaAqy) | Final MP4, SRT, description/chapters, thumbnail, manifest |
| 001 | [`E001-make-ai-useful`](https://drive.google.com/drive/folders/1OdHgDxylP4Rs_zQ7_U8PHSlKTZZbnRBt) | Same. Files renamed `episode-001.*` on 2026-10-03; the `archive-manifest.json` inside still lists the old names. |
| 002 | [`E002-ai-basics`](https://drive.google.com/drive/folders/1VKme1NR8TNqgaR5JnTBqswkwIV6lgXCX) | `episode-002.mp4` is the published no-pop-up master (2,058,534,021 bytes, MD5 `6bbda852ffc189906da26b5e8b1b22ea`). `episode-002-with-popups-2026-09-30.mp4` is the original release. |
| 003 | `E003-ai-agents` (`1x13Xf0pxoNfRLQbx186768qaIkAic227`) | `agents-feedback-cut-v5-audio-matched.mp4` final (MD5 `a30e2648171ff0c1fb0d5eb4824560ff`), SRT, chapters |
| 004 | `E004-el-cruce` (`1H7yxliI3nsJjYiMyQLcAnFOUw1fdG5wX`) | `el-cruce-personality-v11.mp4` final (MD5 `8e34965ba5ee812a5f70d52fcc1e1190`), SRT, chapters |

Raw recordings are in [`Video Files/Raw/`](https://drive.google.com/drive/folders/1KrXgS2Ms6MSz6KXF5YWz1M3fZ_6_fshm):

- `Episode 0/1/2/3 Raw.mp4` and `Episode 1 Raw - vOld1/2`
- `Episode 4 Raw/`, which holds four camera files and three screen recordings (screen-A/B/C MD5 `d81930d7…`, `84d2643f…`, `1ebe894e…`)

Raw numbering was swapped on 2026-10-03 to match the episodes.

## Recovery

- **OOOD project files backup 2026-10-03.zip** (Drive root, MD5 `0d7c369d14e686b44473c62d461be4fa`, 9,020 entries): the whole repository as of 2026-10-03 ~20:00 PT, without video/audio. It includes every versioned edit folder, QC record, review page and comparison that was removed from the working tree in the cleanup, plus brand kit, fonts, music and `.git`.
- **`99_ARCHIVE/2026-09-30-completed-launch-work.zip`** (local only, and inside the Drive backup): byte-for-byte launch-era records. Restore with `scripts/restore-completed-work.py`.
- **`production-records-2026-09-30.zip`** (Drive `Video Files/Final/`): the older compact production-records archive.
