from pathlib import Path
import json,re
Q=Path(__file__).resolve().parent;E=Q.parents[2];ROOT=Q.parents[4];H=Q.parent
m=json.loads((Q/'edit-manifest-v8-final.json').read_text());qc=json.loads((Q/'qc-v8/report.json').read_text())
assert qc['color_container_passed'] and qc['full_av_decode_passed'] and qc['frames']==80695
assert (Q/m['output_file']).stat().st_size==qc['bytes']
assert (Q/'picture-review-v8/covered-ending.jpg').exists()
status='Rendered and technically checked; ready for host review. Exact-version approval, continuous audiovisual review and auditory caption proof remain pending.'
handoff={'current_master':str(Q/m['output_file']),'current_review_page':str(Q/'review-v8.html'),'local_review_url':'http://127.0.0.1:8771/review-v8.html','status':status,'duration_seconds':qc['duration'],'frames':qc['frames'],'bytes':qc['bytes'],'sha256':qc['sha256'],'selected_layout':'C','selected_hook':'Shortened singing hook with an extra half-second laugh','caption_status':'649 retimed draft cues; structural checks passed, auditory proof pending','chapter_count':11,'all_originals_and_prior_outputs_preserved':True,'new_external_delivery_or_publication':False,'verification_evidence':['qc-v8/report.json','qc-v8/color-consistency.json','picture-review-v8/','source-integrity-v8.json','finishing-asset-integrity-v8.json','caption-review-status-v8.json','review-server-check-v8.json']}
(Q/'handoff-record-v8.json').write_text(json.dumps(handoff,indent=2)+'\n')
readme=f'''# El Cruce — current full review cut

**44:49.833 · 1080p30 · {status}**

Start with the [review player](http://127.0.0.1:8771/review-v8.html), or open [the full episode](el-cruce-personality-v8.mp4). The local player includes eleven chapter jumps, draft captions and playable original ranges left out of this proposal. [Include/cut guide](include-and-cut-notes-v8.md) · [Omitted transcript excerpts](omitted-transcript-excerpts-v8.md) · [Title/thumbnail text options](title-and-thumbnail-options.txt).

## What changed

- Your selected **C** format is used throughout screen scenes: inset screen, 800 × 450 host picture, limited overlap, foam background/border and no added teaching cards/headings/logos. Referenced screens are synchronized using the verified source offsets; crops follow the relevant content. Camera-only scenes stay full-screen.
- Restore the opening banter, geography story, race stakes and **Mary's complete coach/logistics and AI brief**, including approval before buying. Keep the different goals, personal context and substantive contributions from both hosts. The camera begins on the actual covered frame at A 00:44.200, then skips the abandoned going-live setup.
- Preserve the useful process and entertainment: voice experiment/tree joke, written-versus-spoken discovery, slow-reading reaction, shopping story, working-style banter, mental-load/last-20% insights, output-format reflection, real website inspection and sharing payoff.
- Remove requested arguing/brushing-off exchanges, extended waiting, repetitive troubleshooting, profanity-bearing passages and unsupported claims. Keep the explicit clinician boundary. Training outputs are not medically verified.
- Use your selected **9.1-second singing hook**, including the extra half-second laugh, followed by the recurring intro card/song. End on the fully covered camera before the recurring outro/music; no hand withdrawal.
- Boost the quiet AI readings while preserving timing and human interjections, then master the complete episode. No synthetic host speech or fabricated demonstrations.

## Verification

The exact master has **80,695 frames**, SHA-256 `{qc['sha256']}`, {qc['bytes']:,} bytes. Complete audiovisual decode and the coded SPS/PPS, MP4 structure and every-frame color gate passed. Single continuous H.264 encode, no B-frame delay or MP4 edit lists; limited BT.709, 1920 × 1080, square pixels, progressive. Encoded audio: **{float(qc['loudness']['input_i']):.2f} LUFS / {float(qc['loudness']['input_tp']):.2f} dBTP**. Audio/video duration difference: {qc['audio_video_duration_difference']:.6f}s. Packet checks and source-to-export audio correspondence samples passed. See [exact report](qc-v8/report.json).

Every edit boundary and each screen scene was sampled in the actual master; card/hook/covered-camera frames are included in `picture-review-v8/`. These are sampled picture checks and focused transcript/audio checks, **not continuous listening/viewing**. Source-relative timing does not establish original camera lip sync. Complete host viewing should confirm subjective joins, voice balance, personal context and caption words/names before exact-version approval. Any detected black/silent spans are documented in the report and reviewed against intended covered-lens transitions.

649 caption cues are nonoverlapping and within the exact timeline. Eleven shared-platform chapters start at 00:00, remain chronological, have starts at least 30 seconds apart and a final chapter longer than 30 seconds. Captions and publishing copy remain drafts.

## Source and edit trail

[Frame-based manifest](edit-manifest-v8-final.json) · [Retained ranges and reasons](edit-decision-list-v8.csv) · [Every omitted range](omitted-source-ranges-v8.csv) · [Source/claim review](claims-and-accuracy-review-v8.md) · [Graphics/screen cue list](graphics-and-screen-cues-v8.json) · [Draft description/chapters](description-and-chapters-draft-v8.txt).

Movies camera originals and Desktop screen originals remain unchanged. Three checksum-identical local screen working copies prevent iCloud offloading from interrupting production. Source and finishing-asset hashes are recorded locally. All earlier cuts, hook/layout comparisons, render stages and other-agent outputs remain intact. This folder's `full-v5` name describes the work pass; **the current complete export is v8**. V5–v7 are earlier work records, not separate completed episode masters.

Title/thumbnail text, public numbering/release order and exact full-cut approval remain open. No new external sharing, upload or publication occurred. The local review server is allowlisted to review assets and the three original camera files; unrelated files are blocked.
'''
assert not (Q/'README.md').exists();(Q/'README.md').write_text(readme)

brief=ROOT/'00_CONTEXT/PROJECT_BRIEF.md';text=brief.read_text()
old='The complete personality/context pass is in production in `edit/codex-personality-pass-2026-10-03/full-v5/`; no new full render or approval is claimed yet.'
new='The [new full personality/context cut](../01_EPISODES/E004-el-cruce/edit/codex-personality-pass-2026-10-03/full-v5/README.md) is rendered and technically checked at **44:49.833**, with selected C screen scenes, the 9.1-second singing hook/laugh extension, the full opening/AI brief, useful host chemistry/reflections, louder AI readings and a covered-camera ending. Its current export is `el-cruce-personality-v8.mp4`; draft captions, eleven chapters, reversible include/cut notes and playable omitted camera ranges accompany it. Continuous host audiovisual/caption review, title/thumbnail copy and exact-version approval remain open; no new external delivery or publication.'
assert old in text;text=text.replace(old,new);brief.write_text(text)

op=ROOT/'00_CONTEXT/OPEN_QUESTIONS.md';text=op.read_text()
text,n=re.subn(r'- For the recorded October 2 El Cruce episode,.*?(?=\n\n)', '- For the recorded October 2 El Cruce episode, will Josh and Mary approve the new **44:49.833 personality/context v8** after continuous viewing/listening, original-camera lip-sync review and auditory caption proof? C and the shortened singing hook are selected and assembled. Confirm subjective voice balance, joins, personal context and exact laugh timing; choose title/thumbnail text and public numbering/release order. Current full package: `01_EPISODES/E004-el-cruce/edit/codex-personality-pass-2026-10-03/full-v5/`. Prior 29:18 v4 and hook/layout comparisons remain preserved; no new publication or external delivery.',text,count=1,flags=re.S)
assert n==1
text=re.sub(r'\n- El Cruce: review the new C-layout personality pass after rendering,.*?\n','\n',text);op.write_text(text)

p=E/'README.md';text=p.read_text()
text=text.replace('Status: recorded (Josh confirmation, 2026-10-02), refined v4 rendered and technically checked for host review.', 'Status: recorded (Josh confirmation, 2026-10-02); new 44:49.833 personality/context v8 rendered and technically checked for host review.')
text=text.replace('Current work: [Codex review package](edit/codex-review-2026-10-02/).','Current package: [New full episode and review guide](edit/codex-personality-pass-2026-10-03/full-v5/README.md).')
text=text.replace('Start with the [revised review page]', 'Previous compact proposal (preserved): [revised review page]')
text=text.replace('Full v4 remains the current full proposal with its earlier placeholder hook; this request produces a separate preview.', 'The new personality/context v8 assembles this selected hook; the prior v4 with its earlier placeholder hook remains preserved.')
text=text.replace('Exact laugh timing and full-episode assembly remain open.', 'Full-episode assembly is complete; subjective exact-version approval remains open.')
text=text.replace('Layout options come first; the revised full episode is not rendered yet.', 'Josh selected C; the new [44:49.833 full review cut](edit/codex-personality-pass-2026-10-03/full-v5/el-cruce-personality-v8.mp4) restores that context and incorporates the feedback. [Review guide and verification](edit/codex-personality-pass-2026-10-03/full-v5/README.md).')
p.write_text(text)
p=H/'README.md';text=p.read_text();text=re.sub(r'Status:.*?(?=\n\n)', 'Status: **new full episode rendered and technically checked at 44:49.833**. [Watch/review the current personality/context cut](full-v5/README.md). Josh selected C (largest host window) and the shortened singing hook. All earlier format comparisons are preserved; exact full-version host approval remains open.',text,count=1,flags=re.S)
text=text.replace('Layout C is selected; the complete new version is in production in `full-v5/`.', 'Layout C is selected; the complete new v8 is in `full-v5/`.')
p.write_text(text)

entry=f'''\n\n## 2026-10-03 — Fuller El Cruce C-layout episode completed for review

Josh requested the complete new episode with selected layout C and all prior feedback. The current [personality/context v8](../01_EPISODES/E004-el-cruce/edit/codex-personality-pass-2026-10-03/full-v5/README.md) is **44:49.833**, 80,695 frames, 1080p30. It supersedes the compact 29:18 v4 as the current editorial proposal, preserving that file and all earlier comparisons.

Restore continuous opening personality, Mary's complete AI/coach/logistics brief, both hosts' goals/judgment, the real voice experiment, useful reactions, working-style banter, mental-load/last-20% insights, output-format reflection and result/sharing payoff. Remove the requested arguments/brushing-off stretches, repetition/build waits, profanity-bearing passages and unsupported race/model/hosting/deadline claims. Preserve the clinician boundary. Screen scenes use C without added teaching text; source crops follow the evidence. Mary's separate-device shoe screenshot story uses the actual hosts/phone footage because the desktop capture does not contain those screenshots. The chosen 9.1-second singing hook/laugh extension and exact recurring cards/music are assembled; the closing cut ends on the covered hand before withdrawal.

The exact master passes complete A/V decode, coded SPS/PPS/MP4/every-frame color, expected-frame/duration, packet and source-relative audio correspondence checks. Encoded sound: {float(qc['loudness']['input_i']):.2f} LUFS / {float(qc['loudness']['input_tp']):.2f} dBTP. Every join and screen scene was sampled visually. Retimed 649-cue English drafts, eleven chapters, reversible retained/omitted ranges, reasons, omitted transcript excerpts and a playable local review page accompany the master. SHA-256: `{qc['sha256']}`. Three local screen working copies match the unchanged iCloud Desktop originals; all source/prior/other-agent files remain preserved, with no deletion.

**Status:** ready for host review; continuous audiovisual viewing, perceptual balance/joins, original-camera lip sync, caption auditory proof and exact-version approval remain open. Title/thumbnail text and public numbering/order remain undecided. No new Slack delivery, upload or publication. Sampled picture checks and waveform correspondence do not constitute continuous listening or prove original camera lip sync.
'''
with (ROOT/'00_CONTEXT/DECISIONS.md').open('a') as f:f.write(entry)
with (ROOT/'03_ASSETS/ASSET_MANIFEST.md').open('a') as f:f.write(f'\n\n## 2026-10-03 — Current fuller El Cruce C-layout review episode\n\n- Current master: `01_EPISODES/E004-el-cruce/edit/codex-personality-pass-2026-10-03/full-v5/el-cruce-personality-v8.mp4`, **44:49.833**, 80,695 frames, 1080p30, {qc["bytes"]:,} bytes; SHA-256 `{qc["sha256"]}`. Exact complete decode, coded-header/container/every-frame color, frame/duration, packet and source-audio alignment checks pass; encoded levels {float(qc["loudness"]["input_i"]):.2f} LUFS / {float(qc["loudness"]["input_tp"]):.2f} dBTP. Host approval remains pending.\n- Uses selected C, current shortened singing hook with laugh extension, recurring cards/music, no teaching overlays, boosted AI readings and covered-camera ending. 649 draft cues, eleven chapters and reversible playable cut review accompany it.\n- Three screen working copies are in `full-v5/source-media/`; their hashes match the unchanged Desktop originals. Original camera hashes also rechecked unchanged. Exact inputs/finishing hashes and full QC are in the new package. All earlier versions and source media remain intact; no cleanup, new external sharing or publication.\n')
print('Current handoff and project records updated')
