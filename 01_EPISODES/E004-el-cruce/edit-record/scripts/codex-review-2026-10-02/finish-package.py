from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parent;repo=Path('/Users/je/oood');m=json.loads((R/'edit-manifest-v3.json').read_text());q=R/'qc'
full=json.loads((q/'el-cruce-proposed-cut-v3-report.json').read_text());assert full['passed']
hooks=json.loads((q/'hooks-summary-v2.json').read_text());special=json.loads((q/'hook04-summary-delivery.json').read_text())[0]
for i,d in enumerate(hooks):
 if d['file'].endswith('04-credit-cards.mp4'):hooks[i]=special
for d in hooks:
 d['file']='hooks-final/'+Path(d['file']).name
 p=R/d['file'];assert d['passed'] and p.is_file() and not p.is_symlink();assert hashlib.file_digest(p.open('rb'),'sha256').hexdigest()==d['sha256']
(q/'hooks-final-summary.json').write_text(json.dumps(hooks,indent=2))
assert len(list((R/'hooks-final').iterdir()))==10
assert all(x['sha256_matches'] for x in json.loads((q/'originals-unchanged-full-v3.json').read_text()))
current=['el-cruce-proposed-cut-v3.mp4','el-cruce-proposed-cut-v3.srt','el-cruce-proposed-cut-v3.vtt','start-here.html','title-and-thumbnail-options.txt','hook-guide.txt','description-and-chapters-draft.txt','editorial-review-notes.txt','edit-manifest-v3.json','edit-decision-list-v3.csv','omitted-source-ranges-v3.csv']+[d['file'] for d in hooks]
manifest={'current_full':'el-cruce-proposed-cut-v3.mp4','current_hooks_folder':'hooks-final','duration':m['duration'],'status':'Technically checked proposed edit; host audiovisual and caption approval pending','artifacts':[]}
for name in current:
 p=R/name;manifest['artifacts'].append({'path':name,'bytes':p.stat().st_size,'sha256':hashlib.file_digest(p.open('rb'),'sha256').hexdigest()})
(R/'package-manifest.json').write_text(json.dumps(manifest,indent=2))
low=min(x['integrated_lufs'] for x in hooks);high=max(x['integrated_lufs'] for x in hooks)
(R/'README.md').write_text(f'''# El Cruce — current review package

**Current full episode: [proposed cut v3](el-cruce-proposed-cut-v3.mp4), 22:58.467.** Start with the [review page](start-here.html) to watch it, choose among ten hooks and compare title options. The page can also be opened in a browser; the videos work independently in a media player.

## Requested deliverables

- [Full proposed episode](el-cruce-proposed-cut-v3.mp4): 1920 × 1080, 30 fps, recurring intro/outro cards, sting/outro music, eleven synchronized screen inserts, both hosts visible during demos and restrained Teachers takeaway graphics.
- [Ten opening previews](hooks-final/): this folder contains only the ten current MP4 files, approximately 32–38 seconds each. Each combines a genuine immediate hook, the recurring intro/sting and the same complete episode opening. [Hook guide](hook-guide.txt). Full cut uses 01; shortlist 01, 02 and 03.
- [Eight title / thumbnail-text pairings](title-and-thumbnail-options.txt): recommended title **We Asked ChatGPT to Coach Us. Then We Had to Coach It.** Thumbnail text **COACHING OUR COACH**. These are text proposals, not rendered thumbnails.
- [Draft chapters and description](description-and-chapters-draft.txt), [draft SRT](el-cruce-proposed-cut-v3.srt) and [draft VTT](el-cruce-proposed-cut-v3.vtt).
- [Editorial notes](editorial-review-notes.txt), [reversible retained-range list](edit-decision-list-v3.csv), [omitted source ranges](omitted-source-ranges-v3.csv) and [editable full manifest](edit-manifest-v3.json).

## Editorial proposal

Just over two hours of camera material is reduced to about 23 minutes. The race provides the stakes; the teaching arc is context → desired output → proposed plan → critical review → specific feedback → a usable result. Keep different goals, Mary's shortlist technique and calendar judgment, Josh's workflow explanations, genuine jokes and the phone payoff. Remove waiting, resets, repeated personal race questions and model/news tangents. Recorded reflection is moved after the result. The cold open deliberately repeats a later moment.

## Verification tied to these files

The full export has **{full['actual_frames']:,} frames**, measured **{full['integrated_lufs']:.2f} LUFS / {full['true_peak_dbtp']:.2f} dBTP**, audio/video duration difference **{full['audio_video_delta']*1000:.1f} ms**, and nine embedded chapters. All eleven delivered videos passed complete audio/video decoding, frame/duration checks, nonnegative monotonic packet times, coded H.264 SPS/PPS consistency, every-frame limited BT.709 color checks and MP4 structure checks. Hook loudness ranges from {low:.2f} to {high:.2f} LUFS. See [full report](qc/el-cruce-proposed-cut-v3-report.json) and [ten-hook summary](qc/hooks-final-summary.json).

All seven raw source SHA-256 hashes still match the initial inventory. Screen offsets were established by waveform correlation at the start, middle and end of each paired recording. The four audio mixes in each camera file matched in the sampled 30-second compressed-audio check; only one mix was used. Caption timing is structurally checked against the current timeline; wording remains a machine-transcription draft with contextual terminology corrections.

Source and export frame sampling covers the cards, every segment boundary, screen inserts and all ten hook/card/opening combinations. The first website reveal crop was corrected and rechecked. The local comparison page was checked visually and its hook selector tested. Nine chronological chapter starts satisfy the shared 30-second spacing rule, including the last chapter.

**Still for host playback:** continuous listening, original camera lip sync, joins by ear, dialogue/music balance, caption auditory proof, retained personal details and exact-version editorial approval. This environment cannot directly hear audio. Technical verification is not platform acceptance or host approval. Nothing was uploaded, scheduled or published.

## Sources and current-version rules

Camera originals: Movies, October 2 recordings 09-36-14, 14-21-33 and 14-52-11. The 09-16-14 test was excluded. Three matching screen recordings remain on Desktop. Exact paths/hashes: `source-review/inventory.json` and `source-review/screens-inventory.json`. [Claim-level research log](../../../../02_RESEARCH/codex-el-cruce-edit-source-log-2026-10-02.md).

Brand cards/music use the live recurring assets in `03_ASSETS`; no public episode-number label was added. E004 is a provisional repository sequence; public numbering remains open.

Use **v3 for the full episode and hooks-final for comparisons**. Earlier v1, incomplete v2 and intermediate hook files are preserved as working history and are not the handoff versions. No raw media or other agents' outputs were deleted, moved or overwritten. [Package manifest with hashes](package-manifest.json).
''')
p=repo/'01_EPISODES/E004-el-cruce/README.md';s=p.read_text().replace('proposed v1','proposed v3').replace('Codex review v1','Codex review v3').replace('22:57','22:58').replace('el-cruce-proposed-cut-v1.mp4','el-cruce-proposed-cut-v3.mp4').replace('2026-10-02/hooks/','2026-10-02/hooks-final/');p.write_text(s)
p=repo/'01_EPISODES/E004-el-cruce/BRIEF.md';s=p.read_text().replace('proposed v1','proposed v3').replace('- [ ] Full review export and all hooks technically checked','- [x] Full review export v3 and all ten hooks technically checked (version-specific reports in review package)');p.write_text(s)
p=repo/'00_CONTEXT/PROJECT_BRIEF.md';s=p.read_text().replace('The rendered v1 is 22:57.433;', 'The technically checked v3 is 22:58.467;');p.write_text(s)
p=repo/'00_CONTEXT/OPEN_QUESTIONS.md';s=p.read_text().replace('proposed 22:57.433 cut','proposed 22:58.467 v3 cut');p.write_text(s)
p=repo/'00_CONTEXT/DECISIONS.md';entry=f'''

## 2026-10-02 — Produce an El Cruce episode proposal and ten opening comparisons

**Authority:** Josh confirmed a new recording on El Cruce and using Chat for planning, logistics and coaching. He requested an engaging proposed cut emphasizing transferable AI skills over extended personal race questions, with flexible duration, recurring branding/cards/music, ten hook-intro-opening previews, and title/thumbnail-text options. He clarified the matching screen recordings are on Desktop.

**Result:** `01_EPISODES/E004-el-cruce/edit/codex-review-2026-10-02/` contains current `el-cruce-proposed-cut-v3.mp4` (22:58.467), ten standalone MP4s in `hooks-final/`, a local comparison page, eight title/thumbnail-copy pairings, draft captions/chapters and reversible cut records. E004 is only a working repository sequence; E003 remains the agents preparation. Three camera takes and three matching screen recordings supply the cut; the short camera test is excluded. The proposal focuses on context, output selection, checking mistakes, specific feedback and stopping at useful while preserving both hosts' judgment and relationship. Recorded reflection is moved after the result. Hook 01 is the editor's recommendation, not a host selection.

**Checks:** All eleven handoff videos passed full decoding, exact frame/duration checks, audio levels and the full coded-color/container gate. Full cut: {full['actual_frames']:,} frames, {full['integrated_lufs']:.2f} LUFS / {full['true_peak_dbtp']:.2f} dBTP; SHA-256 `{full['sha256']}`. All seven original source hashes remain unchanged. Source waveform correlation, transcript review, visual samples and version-specific reports are recorded in the package.

**Status:** Technically checked local proposal, not host-approved or published. Continuous host listening/viewing, original lip sync and caption proof remain open; the environment cannot directly hear audio. Public numbering, release order, title, thumbnail text and hook selection remain unresolved. No uploads, messages, publication or deletion occurred.
''';assert 'Produce an El Cruce episode proposal' not in p.read_text();p.write_text(p.read_text()+entry)
p=repo/'03_ASSETS/ASSET_MANIFEST.md';entry=f'''

## 2026-10-02 — El Cruce source and review assets

- Camera originals (read only): `/Users/je/Movies/2026-10-02 09-36-14.mp4`, `2026-10-02 14-21-33.mp4`, `2026-10-02 14-52-11.mp4`. The 37.7-second `2026-10-02 09-16-14.mp4` test is excluded from the edit.
- Matching screen originals (read only): Desktop's October 2 Screen Recording files at 9.36.12 AM, 2.21.28 PM and 2.51.59 PM. Exact Unicode filenames, media metadata and SHA-256 hashes are in `01_EPISODES/E004-el-cruce/edit/codex-review-2026-10-02/source-review/screens-inventory.json`; camera inventory is adjacent. All seven source hashes rechecked unchanged. No backup/upload was performed for these new sources.
- Current full proposed cut: `01_EPISODES/E004-el-cruce/edit/codex-review-2026-10-02/el-cruce-proposed-cut-v3.mp4`, 22:58.467, 1080p30, {full['bytes']} bytes, SHA-256 `{full['sha256']}`. Uses current recurring cards and sting/outro music. Full decode, levels and coded-color/container checks passed; host audiovisual/caption review pending.
- Current ten hook previews: `hooks-final/` within the same package, approximately 32–38 seconds, technically checked. Only these ten MP4s are in that handoff folder. File hashes and exact current artifacts are recorded in `package-manifest.json`.
- Supporting assets: eleven synchronized screen inserts with Teachers graphics, current full SRT/VTT drafts, nine chapters, eight title/thumbnail-copy pairings, local comparison page, retained/omitted source ranges and editable render manifest. Thumbnail copy only; no new thumbnail image was claimed or rendered.
- Earlier Codex production versions are preserved as working history. Other agents' outputs and original media were not changed. Public episode number and release order are not confirmed; no publication or external delivery is claimed.
''';assert '## 2026-10-02 — El Cruce source and review assets' not in p.read_text();p.write_text(p.read_text()+entry)
print('PACKAGE FINISHED',full['file'],full['integrated_lufs'],full['true_peak_dbtp'])
