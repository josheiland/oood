"""Apply host feedback reversibly; retain finished v4 picture and all original files."""
from pathlib import Path
import json,copy,hashlib,csv,shutil,sys

R=Path(__file__).resolve().parent;D=R/'feedback-revision-v5'
RAW='/Users/je/Movies/Agents episode.mp4'
# The host-saved file lives under E004; picture matching establishes it is E003.
HOOK=R.parents[2]/'E004-el-cruce/AI agents hook final.mp4'

def helper(filename,stop):
    s={'__file__':str(R/filename),'__name__':'feedback_helpers'}
    exec((R/filename).read_text().split(stop)[0],s);return s

def camera(ident,source,a,b,reason):
    af,bf=round(a*30),round(b*30)
    return dict(id=ident,kind='camera',source=str(source),audio_stream=1,
        source_start_frame=af,source_end_frame=bf,frames=bf-af,**{'in':af/30,'out':bf/30},reason=reason)

def positions(segs):
    pos=0
    for s in segs:s['timeline_in']=pos/30;pos+=s['frames'];s['timeline_out']=pos/30
    return pos

def prepare():
    D.mkdir(exist_ok=False);(D/'qc').mkdir();(D/'source-review').mkdir()
    assert HOOK.is_file(),HOOK
    saved=D/'source-review/host-selected-400-agents-hook.mp4';shutil.copy2(HOOK,saved)
    O=json.loads((R/'edit-manifest-v4.json').read_text());M=copy.deepcopy(O)
    selected=camera('selected-hook',saved,0,145/30,'Host-selected saved shortened 400-agents hook; all 145 frames retained.')
    selected['caption_source_in']=1512.2666666666667;selected['caption_source_out']=1517.1
    S=[selected,copy.deepcopy(O['segments'][2])]+copy.deepcopy(O['segments'][3:])
    S[1]['reason']='Recurring intro card and complete music sting after the host-selected hook.'
    for s in S:
        if s['id']=='s005':
            s['in']=120.66666666666667;s['source_start_frame']=3620;s['frames']=s['source_end_frame']-3620
            s['reason']='Restore the entire lead-in to the would-piss-you-off reaction; no mid-sentence entrance.'
        if s['id']=='s022':
            s['out']=2193.6666666666665;s['source_end_frame']=65810;s['frames']=65810-s['source_start_frame']
            s['reason']='Restore the guard/checker/guardrails exchange and natural lead-out into Anyways; continuous with s023.'
        if s['id']=='s035':
            s['out']=3907.5333333333333;s['source_end_frame']=117226;s['frames']=117226-s['source_start_frame']
            s['reason']='Restore the explicit gym-to-AI-tool-provider comparison and usage-pricing setup; continuous with s036.'
    idx=next(i for i,s in enumerate(S) if s['id']=='s034')
    S.insert(idx,camera('pricing-bridge',RAW,3559.9333333333334,3567.9666666666667,
        'Move Mary\'s complete request to explore outcome pricing here as an explicit topic bridge; omit the following Bain/general-industry claims.'))
    frames=positions(S);M.update(segments=S,total_frames=frames,duration=frames/30,
        output_file='agents-feedback-cut-v5.mp4',status='Feedback revision; selected hook incorporated; exact-version host review pending',
        selected_hook={'source':str(HOOK),'preserved_copy':str(saved),'sha256':hashlib.file_digest(HOOK.open('rb'),'sha256').hexdigest(),
                      'frames':145,'duration':145/30,'source_match_start_frame':45368,'host_choice':'Shortened me and my 400 agents'},
        provisional_hook=None,hooks=O['hooks'],body=[s for s in S if s['kind']=='camera' and s['id']!='selected-hook'])
    oldby={s['id']:s for s in O['segments']};newby={s['id']:s for s in S}
    chapters=[]
    for c in O['chapters']:
        if c['time']==0:chapters.append(dict(time=0,title='400 agents and the opening'));continue
        if c['title']=='Opening':continue # Merge sub-30-second opening chapter for platform compatibility.
        old=next(s for s in O['segments'] if s['timeline_in']<=c['time']<s['timeline_out'])
        new=newby[old['id']];time=new['timeline_in']+c['time']-old['timeline_in']
        if old['id']=='s034':time=newby['pricing-bridge']['timeline_in']
        chapters.append(dict(time=time,title=c['title']))
    M['chapters']=chapters
    # Fast assembly uses the finished v4 for unchanged pictures and audio, including
    # its message-list mask and actual covered-lens outro. New speech comes from raw.
    v4=R/O['output_file'];A=[copy.deepcopy(selected),copy.deepcopy(S[1])]
    patches=[
        ('unchanged-opening',v4,30,104.93333333333334,'Unchanged v4 topic introduction and generic egg example.'),
        ('reaction-complete',RAW,120.66666666666667,139.76666666666668,'Complete reaction lead-in.'),
        ('unchanged-core',v4,121.56666666666666,1119.1,'Unchanged components, examples and Vend.'),
        ('guardrails-complete',RAW,2144.6666666666665,2193.6666666666665,'Complete guardrails exchange through natural transition.'),
        ('unchanged-personal',v4,1159,1832.2333333333333,'Unchanged personal-agent examples; includes v4 phone mask.'),
        ('pricing-bridge',RAW,3559.9333333333334,3567.9666666666667,'Explicit pricing topic bridge.'),
        ('unchanged-pricing',v4,1832.2333333333333,1925.6666666666667,'Existing Sierra example and gym setup.'),
        ('gym-ai-link',RAW,3883.9666666666667,3907.5333333333333,'Explicit gym/model/provider mapping and per-minute setup.'),
        ('unchanged-ending',v4,1925.6666666666667,2233.6666666666665,'Unchanged payoff, recap, eggs, complete signoff and covered-lens outro.'),
    ]
    for ident,src,a,b,reason in patches:
        s=camera(ident,src,a,b,reason);s['mix_raw']=str(src)==RAW;A.append(s)
    assert positions(A)==frames,(positions(A),frames)
    M['assembly_segments']=A
    phone=newby['s025'];M['picture_finishing']['phone_mask'].update(output_in=phone['timeline_in'],output_out=phone['timeline_in']+5.5)
    M['picture_finishing']['closing_cover']=newby['s039b'];M['picture_finishing']['audio']='v4 audio preserved in unchanged source ranges; restored raw dialogue pan/highpass matched; final full-program loudness normalization.'
    (D/'edit-manifest-v5.json').write_text(json.dumps(M,indent=2)+'\n')
    with (D/'edit-decision-list-v5.csv').open('x') as f:
        w=csv.writer(f);keys=['id','kind','source','source_start_frame','source_end_frame','timeline_in','timeline_out','frames','reason'];w.writerow(keys)
        for s in S:w.writerow([s.get(k,'') for k in keys])
    cap=helper('make-sidecars.py','checks={');CS=copy.deepcopy(S)
    CS[0]['in']=selected['caption_source_in'];CS[0]['out']=selected['caption_source_out']
    result=cap['captions'](CS,D/M['output_file']);(D/'qc/caption-structure.json').write_text(json.dumps(result,indent=2)+'\n')
    (D/'chapters.txt').write_text('\n'.join(cap['tc'](c['time'])[3:]+' '+c['title'] for c in chapters)+'\n')
    assert chapters[0]['time']==0 and all(b['time']-a['time']>=30 for a,b in zip(chapters,chapters[1:]))
    assert M['duration']-chapters[-1]['time']>=30
    (D/'source-review/selected-hook.json').write_text(json.dumps(M['selected_hook'],indent=2)+'\n')
    print('Plan:',frames,'frames;',frames/30,'seconds; hook',145/30,'seconds',flush=True)
    return M

def render(M):
    text=(R/'render-proposal.py').read_text().split("if __name__=='__main__':")[0]
    text=text.replace("if s['kind']=='camera':af+=", "if s['kind']=='camera':\n    if s.get('mix_raw'):af+=")
    text=text.replace("'-threads','4','-preset'", "'-threads','8','-preset'").replace("'-crf','19'","'-crf','18'")
    scope={'__file__':str(R/'render-proposal.py'),'__name__':'feedback_render'};exec(text,scope)
    scope['render'](M['assembly_segments'],D/M['output_file'],D/'work/full-v5',M['chapters'])

if __name__=='__main__':render(prepare())
