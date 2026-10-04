from pathlib import Path
import copy,json,importlib.util,time
H=Path(__file__).resolve().parent;R=H.parent
original=json.loads((H/'edit-manifest-v4.json').read_text())
m=copy.deepcopy(original);segs=[]
for s in m['segments']:
 if s['id']=='v4-030':
  a=copy.deepcopy(s);b=copy.deepcopy(s)
  a.update(id='v4-030a',out=277.4)
  b.update(id='v4-030b',**{'in':280.6})
  a['reason']+=' Remove 3.2 seconds of silent calendar inspection after the hosts finish their exchange.'
  b['reason']='Continue the calendar reveal at the complete Friday/tomorrow correction after the inspection pause.'
  segs.extend([a,b])
 else:segs.append(s)
frames=0;old_chapters={round(c['time']*30):c['title'] for c in original['chapters']};chapters=[]
for s in segs:
 old_start=round(s['timeline_in']*30)
 if old_start in old_chapters and not s['id'].endswith('b'):chapters.append({'time':frames/30,'title':old_chapters[old_start]})
 s['timeline_in']=frames/30;frames+=round((s['out']-s['in'])*30);s['timeline_out']=frames/30
m.update(segments=segs,chapters=chapters,duration=frames/30,output_file='refinement-v4/el-cruce-proposed-cut-v4-tightened.mp4')
p=H/'edit-manifest-v4-tightened.json'
if p.exists():raise FileExistsError(p)
p.write_text(json.dumps(m,indent=2)+'\n')
spec=importlib.util.spec_from_file_location('renderer',R/'render-review.py');renderer=importlib.util.module_from_spec(spec);spec.loader.exec_module(renderer)
render_one=renderer.render_segment
def key(s):return json.dumps({k:v for k,v in s.items() if k not in ('id','prior_segment_id','reason','timeline_in','timeline_out','restored_from_raw')},sort_keys=True)
prior={key(s):s for s in original['segments']}
def cached(s,folder):return render_one(prior.get(key(s),s),folder)
renderer.render_segment=cached
print('Tightened final duration:',frames/30,flush=True)
renderer.render(segs,H/'el-cruce-proposed-cut-v4-tightened.mp4',H/'tightened-render-work',chapters)
