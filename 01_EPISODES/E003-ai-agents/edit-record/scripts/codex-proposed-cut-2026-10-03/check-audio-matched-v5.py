from pathlib import Path
import json,subprocess,shutil,concurrent.futures,numpy as np
R=Path(__file__).resolve().parent;D=R/'feedback-revision-v5'
M=json.loads((D/'edit-manifest-v5.json').read_text())
assert M['output_file']=='agents-feedback-cut-v5-audio-matched.mp4'
def helper(name,stop):
    scope={'__file__':str(R/name),'__name__':'matched_checks'}
    exec((R/name).read_text().split(stop)[0],scope);scope['R']=D;return scope

def rms(path,t):
    b=subprocess.run(['ffmpeg','-nostdin','-v','error','-ss',str(t),'-i',str(path),'-t','1','-map','0:a:0','-ac','1','-ar','48000','-f','f32le','-'],capture_output=True,check=True).stdout
    a=np.frombuffer(b,dtype='<f4');return float(np.sqrt(np.mean(a*a)))
items=[]
for raw in [125,130,134]:items.append(('reaction',raw,104.933333333+(raw-123.133333333),85.033333333+(raw-120.666666667)))
for raw in [2145,2150,2165,2180]:items.append(('guardrails',raw,1119.1+(raw-2144.666666667),1101.666666667+(raw-2144.666666667)))
def level(x):
    section,source,old,new=x;delta=float(20*np.log10(rms(D/M['output_file'],new)/rms(R/'agents-proposed-cut-v4.mp4',old)))
    return dict(section=section,source_time=source,old_time=old,new_time=new,level_delta_db=delta,passed=abs(delta)<=2)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:levels=list(pool.map(level,items))
(D/'qc/matched-dialogue-levels.json').write_text(json.dumps(levels,indent=2)+'\n')
print('Restored dialogue level deltas',[(x['section'],round(x['level_delta_db'],2)) for x in levels],flush=True)
assert all(x['passed'] for x in levels),'Restored dialogue still differs by more than 2dB.'

preview=D/'agents-selected-opening-v5-audio-matched.mp4';assert not preview.exists()
subprocess.run(['ffmpeg','-nostdin','-v','error','-n','-i',str(D/M['output_file']),'-t','30','-map','0:v:0','-map','0:a:0','-map_metadata','0','-map_chapters','-1','-c','copy','-use_editlist','0','-movflags','+faststart',str(preview)],check=True)
for ext in ['srt','vtt']:shutil.copy2(D/('agents-selected-opening-v5.'+ext),preview.with_suffix('.'+ext))
q=helper('verify-exports.py','items=[')
q['verify'](('selected-opening-audio-matched',preview,900))
print('Starting exact audio-matched master checks.',flush=True)
result=q['verify'](('main-v5-audio-matched',D/M['output_file'],M['total_frames']))
c=helper('compare-source.py','items=[]')
items=[(s['id'],D/M['output_file'],s) for s in M['segments'] if s['kind']=='camera']
by={s['id']:s for s in M['segments']}
for name,ident,a,b in [('restored-guard-tail','s022',2184.5666666666666,2193.6666666666665),('restored-gym-ai-link','s035',3883.9666666666667,3907.5333333333333)]:
    parent=by[ident];sample=dict(parent)
    sample.update(**{'in':a,'out':b,'timeline_in':parent['timeline_in']+a-parent['in'],'timeline_out':parent['timeline_in']+b-parent['in']})
    items.append((name,D/M['output_file'],sample))
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:comp=list(pool.map(c['compare'],items))
(D/'qc/audio-matched-source-comparison.json').write_text(json.dumps(dict(passed=all(x['passed'] for x in comp),segments=comp),indent=2)+'\n')
assert all(x['passed'] for x in comp)
prior=D/'qc/summary-before-audio-match.json';assert not prior.exists();shutil.copy2(D/'qc/summary.json',prior)
summary=dict(passed=True,current_master=M['output_file'],duration=M['duration'],frames=M['total_frames'],sha256=result['sha256'],loudness=result['loudness'],
    selected_hook=M['selected_hook'],selected_preview=preview.name,audio_level_match='Passed: restored dialogue within 2dB of v4 references',
    picture_review=json.loads((D/'qc/picture-review-observations.json').read_text()),
    video_identity=json.loads((D/'qc/video-identity-audio-match.json').read_text()),
    host_listening='Pending for this exact version',caption_words='ASR draft; auditory proof pending')
(D/'qc/summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print('Audio-matched master and selected opening: all required checks passed.',flush=True)
