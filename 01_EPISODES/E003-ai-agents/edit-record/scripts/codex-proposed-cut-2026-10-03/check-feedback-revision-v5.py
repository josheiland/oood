from pathlib import Path
import json, concurrent.futures, sys
R=Path(__file__).resolve().parent;D=R/'feedback-revision-v5'
M=json.loads((D/'edit-manifest-v5.json').read_text())
def helper(filename,stop):
    scope={'__file__':str(R/filename),'__name__':'feedback_checks'}
    exec((R/filename).read_text().split(stop)[0],scope);scope['R']=D;return scope
if '--preview' in sys.argv:
    q=helper('verify-exports.py','items=[')
    q['verify'](('selected-opening',D/'agents-selected-opening-v5.mp4',900))
else:
    q=helper('verify-exports.py','items=[')
    result=q['verify'](('main-v5',D/M['output_file'],M['total_frames']))
    c=helper('compare-source.py','items=[]')
    base_audio=c['get_audio']
    def matched_audio(path,t,mapidx,raw=False,inside=0):
        # The saved hook already contains the finished centered/high-passed mix.
        # Compare it directly instead of applying that filter a second time.
        if raw and str(path)!=M['source']:return base_audio(path,t+inside,mapidx,False)
        return base_audio(path,t,mapidx,raw,inside)
    c['get_audio']=matched_audio
    items=[(s['id'],D/M['output_file'],s) for s in M['segments'] if s['kind']=='camera']
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:comp=list(pool.map(c['compare'],items))
    assert all(x['passed'] for x in comp)
    (D/'qc/source-comparison.json').write_text(json.dumps(dict(passed=True,segments=comp,
        method='Sampled waveform/picture correspondence per retained camera excerpt; zero/near-zero introduced lag does not establish original camera lip sync or continuous listening.'),indent=2)+'\n')
    (D/'qc/summary.json').write_text(json.dumps(dict(passed=True,current_master=M['output_file'],
        duration=M['duration'],frames=M['total_frames'],sha256=result['sha256'],loudness=result['loudness'],
        selected_hook=M['selected_hook'],host_listening='Pending for this exact version',caption_words='ASR draft; auditory proof pending'),indent=2)+'\n')
