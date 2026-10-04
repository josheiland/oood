"""Compact hook comparisons; preserve all earlier exports and manifests."""
from pathlib import Path
import json, importlib.util, concurrent.futures, argparse

R = Path(__file__).resolve().parent
D = R / 'hook-transition-previews-v2'
SOURCE = '/Users/je/Movies/Agents episode.mp4'

def module_prefix(filename, stop):
    scope = {'__file__': str(R / filename), '__name__': 'preview_helpers'}
    exec((R / filename).read_text().split(stop)[0], scope)
    return scope

def prepare():
    D.mkdir(exist_ok=False)
    (D / 'qc').mkdir()
    old = json.loads((R / 'edit-manifest-v4.json').read_text())
    ranges = [
        [(1291.533333,1296.4),(1394.4,1397.8)],
        [(2236.966667,2246.9)],
        [(2021.733333,2032.233333)],
        [(1512.266667,1521.0)],
        [(1915.066667,1917.133333),(1940.733333,1947.033333)],
        [(2407.2,2412.833333),(2428.6,2434.166667)],
        [(4157.6,4167.666667)],
        [(193.9,198.2),(132.333333,139.766667)],
    ]
    titles = ['Big Egg / too many eggs','Too many tools, too little life','I just want a baby',
              'Me and my 400 coworkers','Bring back the mathematicians','She has to be a she',
              'A runny boil?','Credit card permission / Uber Eats forever']
    hooks=[]
    for h, clips, title in zip(old['hooks'], ranges, titles):
        segs=[]
        for i,(a,b) in enumerate(clips):
            af,bf=round(a*30),round(b*30)
            segs.append(dict(kind='camera',source=SOURCE,audio_stream=1,
                source_start_frame=af,source_end_frame=bf,frames=bf-af,in_=af/30,out=bf/30,
                reason='Compact authentic joke; complete setup or punchline.'))
        hook_frames=sum(s['frames'] for s in segs)
        card=dict(old['hooks'][0]['segments'][-1])
        card.update(frames=158,out=158/30,source_start_frame=0,source_end_frame=158,
                    reason='Recurring intro card and complete song sting.')
        segs.append(card)
        body_frames=900-hook_frames-158
        segs.append(dict(kind='camera',source=SOURCE,audio_stream=1,source_start_frame=1920,
            source_end_frame=1920+body_frames,frames=body_frames,in_=64.0,out=64+body_frames/30,
            reason='Identical beginning of the proposed episode body; starts at v4 output 00:30.'))
        pos=0
        for s in segs:
            if 'in_' in s:s['in']=s.pop('in_')
            s['timeline_in']=pos/30;pos+=s['frames'];s['timeline_out']=pos/30
        assert pos==900
        hooks.append(dict(id=h['id'],title=title,file=h['id']+'-transition-v2.mp4',frames=900,
            duration=30.0,hook_duration=hook_frames/30,card_duration=158/30,
            opening_duration=body_frames/30,segments=segs))
    plan=dict(version='hook-transition-previews-v2',source=SOURCE,fps=30,
              format='Compact hook → recurring card/song → same episode opening',
              master='agents-proposed-cut-v4.mp4; unchanged; provisional longer Big Egg hook pending selection',hooks=hooks)
    (D/'preview-manifest.json').write_text(json.dumps(plan,indent=2)+'\n')
    cap=module_prefix('make-sidecars.py','checks={')
    checks={h['id']:cap['captions'](h['segments'],D/h['file']) for h in hooks}
    (D/'qc/captions.json').write_text(json.dumps(checks,indent=2)+'\n')
    return plan

def render(plan):
    spec=importlib.util.spec_from_file_location('render_helpers',R/'render-proposal.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    def one(h):m.render(h['segments'],D/h['file'],D/'work'/h['id'],[])
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(one,plan['hooks']))

def verify(plan):
    q=module_prefix('verify-exports.py','items=[');q['R']=D
    items=[(h['id'],D/h['file'],900) for h in plan['hooks']]
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        results=list(pool.map(q['verify'],items))
    c=module_prefix('compare-source.py','items=[]');c['R']=D
    items=[(h['id']+f'-{i}',D/h['file'],s) for h in plan['hooks']
           for i,s in enumerate(h['segments']) if s['kind']=='camera']
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        comparison=list(pool.map(c['compare'],items))
    assert all(x['passed'] for x in comparison)
    (D/'qc/source-comparison.json').write_text(json.dumps(comparison,indent=2)+'\n')
    (D/'qc/summary.json').write_text(json.dumps(dict(passed=True,exports=len(results),
        frames_each=900,duration_each=30,source_ranges_compared=len(comparison),
        host_listening='Pending',results=[{k:r[k] for k in ['file','sha256','loudness','passed']} for r in results]),indent=2)+'\n')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--verify',action='store_true');a=p.parse_args()
    if a.verify:verify(json.loads((D/'preview-manifest.json').read_text()))
    else:render(prepare())
