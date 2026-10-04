from pathlib import Path
import json,copy,csv
R=Path(__file__).resolve().parent
P=R/'edit-manifest-v2.json';assert not P.exists()
O=json.loads((R/'edit-manifest-v1.json').read_text());M=copy.deepcopy(O)
changes={'s010':(None,1135.1),'s012':(1193.2,1327.0333333333),'s014':(1348.2,1405.8333333333),'s015':(1429.9666666667,1494.6666666667),'s018':(None,1832.6666666667),'s019':(None,1947.0333333333),'s025':(2353.2,None),'s026':(2404.16,2475.7333333333),'s027':(2476.3333333333,None),'s029':(2575.0,None),'s033':(3038.4,None),'s034':(None,3400.9666666667)}
M['segments']=[s for s in M['segments'] if s['id']!='s013']
for s in M['segments']:
 if s['id'] in changes:
  a,b=changes[s['id']]
  if a is not None:s['source_start_frame']=round(a*30);s['in']=s['source_start_frame']/30
  if b is not None:s['source_end_frame']=round(b*30);s['out']=s['source_end_frame']/30
  s['frames']=s['source_end_frame']-s['source_start_frame']
  s['reason']+=' Join refinement v2: retain complete spoken clauses and necessary setup; omit dangling transitions.'
pos=0
for s in M['segments']:s['timeline_in']=pos/30;pos+=s['frames'];s['timeline_out']=pos/30
M['total_frames']=pos;M['duration']=pos/30;M['output_file']='agents-proposed-cut-v2.mp4';M['status']='Proposed for host review; v2 refines complete clauses and joins; v1 preserved as superseded work file.'
M['body']=[s for s in M['segments'] if s['kind']=='camera' and s['id'] not in ('s000','s001')]
for c in M['chapters']:
 if c['time'] in (0,30):continue
 old=next(s for s in O['segments'] if abs(s['timeline_in']-c['time'])<.001)
 new=next((s for s in M['segments'] if s['id']==old['id']),None)
 if new:c['time']=new['timeline_in']
 else:
  new=next(s for s in M['segments'] if s['kind']=='camera' and s['in']<=old['in']<s['out']);c['time']=new['timeline_in']+old['in']-new['in']
P.write_text(json.dumps(M,indent=2)+'\n')
with (R/'edit-decision-list-v2.csv').open('x') as f:
 w=csv.DictWriter(f,fieldnames=['id','kind','source','source_start_frame','source_end_frame','timeline_in','timeline_out','frames','reason']);w.writeheader()
 for s in M['segments']:w.writerow({k:s[k] for k in w.fieldnames})
print(M['total_frames'],M['duration'],M['duration']/60)
