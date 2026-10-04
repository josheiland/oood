"""Run only after exact v4 export and comparison checks pass."""
from pathlib import Path
import json,re,hashlib
R=Path(__file__).resolve().parent;M=json.loads((R/'edit-manifest-v4.json').read_text());Q=R/'qc'
names=['main-v4']+[h['id'] for h in M['hooks']];reports=[json.loads((Q/f'{n}-report.json').read_text()) for n in names];assert all(r['passed'] for r in reports)
comparisons=[json.loads((Q/n).read_text()) for n in ['main-v4-source-comparison.json','hooks-source-comparison.json']];assert all(c['passed'] for c in comparisons)
source=json.loads((Q/'source-integrity.json').read_text());assert source['matches_pre_edit_source']
captions=json.loads((Q/'caption-structure.json').read_text());assert captions['main']['nonoverlapping']
def payload_hash(path):
 import subprocess
 p=subprocess.run(['ffmpeg','-nostdin','-v','error','-i',str(path),'-map','0:a:0','-c:a','copy','-f','hash','-hash','sha256','-'],capture_output=True,text=True,check=True)
 return p.stdout.strip()
a=payload_hash(R/'agents-proposed-cut-v3.mp4');b=payload_hash(R/M['output_file']);assert a==b
audio={'v3':a,'v4':b,'exact_aac_payloads_preserved':True,'dialogue_and_music_changed':False};(Q/'v4-audio-identity.json').write_text(json.dumps(audio,indent=2)+'\n')
picture=json.loads((Q/'picture-review-status.json').read_text());assert picture['final_v4_export_picture_sampling']=='reviewed'
main=reports[0]
summary={'version':M['output_file'],'status':'Rendered and technically checked; proposed for exact-version host review','duration_seconds':M['duration'],'frames':M['total_frames'],'dimensions':[1920,1080],'fps':30,'master_sha256':main['sha256'],'master_bytes':main['bytes'],'master_lufs':main['loudness']['input_i'],'master_true_peak_dbtp':main['loudness']['input_tp'],'master_full_decode_passed':not main['full_decode_errors'],'master_black_spans':main['black_spans'],'master_silence_events':main['silence_events'],'coded_h264_mp4_all_frame_color_gate_passed':True,'packet_timing_passed':True,'main_source_audio_max_absolute_lag_samples':max(abs(s['audio_lag_samples']) for s in comparisons[0]['segments']),'main_source_min_audio_correlation':min(s['audio_correlation'] for s in comparisons[0]['segments']),'main_source_min_picture_similarity':min(s['picture_similarity'] for s in comparisons[0]['segments']),'source_unchanged':True,'captions':captions['main'],'chapter_count':len(M['chapters']),'hook_count':len(M['hooks']),'hooks':[{'id':h['id'],'title':h['title'],'file':h['file'],'seconds':30,'frames':900,'sha256':r['sha256'],'lufs':r['loudness']['input_i'],'true_peak_dbtp':r['loudness']['input_tp'],'passed':r['passed']} for h,r in zip(M['hooks'],reports[1:])],'picture_finishing':M['picture_finishing'],'audio_identity':audio,'pending':['Host continuous viewing/listening and original camera lip sync','Perceptual edit-join/pacing review','Auditory caption/name proof','Hook choice','Public title/release order/date','Exact-version host approval'],'external_upload_or_delivery':False,'published':False,'platform_acceptance':'not tested or claimed'}
(Q/'verification-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
files=[R/M['output_file'],*(R/h['file'] for h in M['hooks']),R/'agents-proposed-cut-v4.srt',R/'agents-proposed-cut-v4.vtt',R/'chapters.txt',R/'edit-manifest-v4.json',R/'edit-decision-list-v4.csv',R/'review.html',R/'README.md',R/'edit-notes.md',R/'removed-ranges.csv',R/'removed-material-transcript.txt',R/'proposed-cut-transcript.md',Q/'verification-summary.json']
package={'current_master':M['output_file'],'status':summary['status'],'source':M['source'],'source_sha256':M['source_sha256'],'files':[{'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':hashlib.file_digest(p.open('rb'),'sha256').hexdigest()} for p in files],'preserved_work_versions':{'v1':'superseded complete work render; not current','v2':'interrupted/incomplete; not current','v3':'technically checked, superseded by v4 picture finishing'},'no_deletion':True,'no_publication':True}
(R/'package-manifest.json').write_text(json.dumps(package,indent=2)+'\n')
for name in ['review.html','build-review.py']:
 p=R/name;x=p.read_text().replace('Ready for host review once export checks complete.','Rendered and technically checked; ready for host review.').replace('Current master: v3.','Current master: v4.');p.write_text(x)
handoff=f'''# Agents — current proposed cut

Current version: `{M['output_file']}`, **37:13.667**, 1080p30, 67,010 frames. Eight hook-only comparisons are exactly 30 seconds each, including their card/music tail. Recommend Big Egg, Five-minute audition, and Baby, in that order; the opening remains a host choice.

Source: `{M['source']}` — 70:24.567. Original hash matches the pre-edit inventory. All sources, earlier work renders and other-agent outputs are preserved. No deletion, external delivery, upload or publication occurred.

V4 keeps the selected complete conversations from v3, masks the brief front-facing message list, and reaches the actual fully covered camera before the recurring outro card. V3's audio packets are preserved exactly. Repeated attempts, unsupported historical/product/statistical assertions and diffuse medical/legal/pricing detours were removed. Personal experiences and hypothetical examples retain their original qualification.

Exact-version checks: full H.264 SPS/PPS, MP4 structure, all 67,010 decoded frames, packet timing, full A/V decode and loudness pass. Audio is {main['loudness']['input_i']} LUFS / {main['loudness']['input_tp']} dBTP; no black spans or extended silences. Retained-source waveform and picture samples pass. Every edit boundary and finishing change has sampled picture evidence. Caption structure passes; words/names remain an ASR draft needing host listening.

Review: `review.html` / the private local server in `review-server.json`. Includes all eight hooks, chapter jumps, join playback and 33 playable removed ranges with restoration flags. Edit choices, source references and all QC details are local and reversible.

Remaining: choose the hook and review the exact full cut continuously, including original camera lip sync, perceived audio balance, pacing and captions. Approve public title/release order/date separately. Technical checks establish a reviewable export, not host approval or platform acceptance.
'''
(R/'HANDOFF.md').write_text(handoff)
p=R/'README.md';x=p.read_text()+f'\nExact current-master result: **{main["loudness"]["input_i"]} LUFS / {main["loudness"]["input_tp"]} dBTP**, 67,010 frames; all nine video exports pass their full coded-color/container/frame/timing/audio gates. See `HANDOFF.md` and `qc/verification-summary.json`.\n';p.write_text(x)
# Refresh hashes after final handoff text/status updates.
package['files']=[{'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':hashlib.file_digest(p.open('rb'),'sha256').hexdigest()} for p in files+[R/'HANDOFF.md']];(R/'package-manifest.json').write_text(json.dumps(package,indent=2)+'\n')
print(json.dumps({'master':M['output_file'],'duration':M['duration'],'frames':M['total_frames'],'lufs':summary['master_lufs'],'true_peak':summary['master_true_peak_dbtp'],'hooks':len(M['hooks']),'sha256':main['sha256']},indent=2))
