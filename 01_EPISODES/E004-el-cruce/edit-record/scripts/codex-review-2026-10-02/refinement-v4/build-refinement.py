from pathlib import Path
import copy,json,importlib.util
H=Path(__file__).resolve().parent
R=H.parent
m=json.loads((R/'edit-manifest-v3.json').read_text())
old=copy.deepcopy(m['segments'])
def revised(i,a=None,b=None,reason=None):
 s=copy.deepcopy(old[i]);s['prior_segment_id']=s.pop('id');s.pop('timeline_in');s.pop('timeline_out')
 if a is not None:s['in']=round(a*30)/30
 if b is not None:s['out']=round(b*30)/30
 if reason:s['reason']=reason
 return s
def addition(i,a,b,reason):
 s=revised(i,a,b,reason)
 for k in ('popup','popup_in','popup_out'):s.pop(k,None)
 s['restored_from_raw']=True
 return s
changes={
 2:(None,74.8,'Keep the energetic welcome; remove the first, repeated race introduction.'),
 4:(186.8,212.333333,'Start at the two coaching jobs; finish the question about preparation before logistics.'),
 5:(None,269.133333,'Protect the final purchase-approval word.'),
 9:(None,525.0,'Protect the complete shared-training sentence.'),
 12:(661.266667,None,'Start with the complete dictated instruction.'),
 13:(877.3,None,'Start at the decision after the recording reset.'),
 14:(None,929.6,'Protect the complete save-instructions sentence.'),
 15:(None,1004.666667,'Include the complete I love it response; stop before the next question.'),
 16:(None,2261.7,'End after the acknowledgment, before the unfinished next setup.'),
 17:(2306.866667,None,'Keep the whole opening acknowledgment and plan request.'),
 18:(None,2701.4,'Restore the race-demand and training-baseline questions continuously, including the clinician boundary.'),
 20:(None,2889.966667,'End before the next unrelated WhatsApp question.'),
 21:(None,3373.433333,'Protect the last acknowledgment about speaker labels.'),
 22:(3623.3,3657.733333,'Restore the complete dynamic-plan setup and acknowledgment.'),
 23:(None,4031.666667,'Protect the complete gear-chat sentence.'),
 24:(None,47.333333,'Keep the complete update and AI-shopping question.'),
 25:(None,173.4,'Restore the hosts checking whether this new chat actually knows Josh; retain their real uncertainty.'),
 26:(173.4,None,'Continue the same source without duplicating a frame.'),
 27:(None,255.433333,'Keep the complete aesthetic acknowledgment.'),
 28:(256.966667,319.933333,'Restore the calendar-view lead-in so the Friday/tomorrow error has visible context.'),
 31:(461.933333,None,'Restore the complete request to gather logistics and outline actions before executing.'),
 34:(219.533333,None,'Start with the complete spoken sheet request.'),
 36:(None,380.4,'Protect the last word of the sycophancy explanation.'),
 37:(None,875.666667,'Keep the acknowledgment after checking the source instructions.'),
 39:(None,1328.633333,'End the result inspection before the next unretained question.'),
 42:(None,1575.166667,'End the GitHub explanation after its sentence and brief breath.'),
 43:(1577.2,1603.3,'Keep the full deployment setup and device-test sentence.'),
 49:(1485.366667,1508.1,'Start after the discarded meeting aside and retain the complete acknowledgment.'),
 50:(1847.466667,None,'Restore the database possibility so stopping at good enough has context.'),
 51:(1510.466667,1516.633333,'Cut to the branded outro while the hand fully covers the camera; exclude withdrawal.'),
}
segs=[]
for i in range(len(old)):
 if i in (19,29):continue
 s=revised(i,*changes[i]) if i in changes else revised(i)
 if i==28:
  for k in ('screen','screen_offset','layout','crop'):s[k]=copy.deepcopy(old[29][k])
 if i==33:s['out']=216.3;s['reason']='Allow the full ask-it phrase and breath before dictation.'
 segs.append(s)
 if i==12:segs.append(addition(11,728.533333,748.2,'Restore Mary and Josh comparing useful detail with verbosity; retain the correction.'))
 if i==17:
  segs.append(addition(17,2520.133333,2550.2,'Restore the reasoning-effort tradeoff and Mary realizing higher effort is not faster.'))
  segs.append(addition(17,2583.433333,2600.933333,'Restore Mary reflecting on her reversed assumption and the practical thinking-time takeaway.'))
 if i==31:segs.append(addition(33,19.2,77.333333,'Restore the ten-minute constraint, affectionate working-style banter, and usable-version standard.'))
 if i==36:segs.append(addition(33,389.7,414.0,'Restore permissions and the two connected account contexts before later routing mistakes.'))
 if i==48:segs.append(addition(48,943.933333,1030.433333,'Restore calendar/text/weekly-plan alternatives and pausing to decide what support is useful.'))
frames=0;chapters=[]
chapter_by_old={0:m['chapters'][0]['title'],6:m['chapters'][1]['title'],16:m['chapters'][2]['title'],24:m['chapters'][3]['title'],28:m['chapters'][4]['title'],32:m['chapters'][5]['title'],35:m['chapters'][6]['title'],38:m['chapters'][7]['title'],47:m['chapters'][8]['title']}
for j,s in enumerate(segs):
 s['id']=f'v4-{j:03}'
 s['timeline_in']=frames/30
 oi=int(s['prior_segment_id'][1:])
 if oi in chapter_by_old and not s.get('restored_from_raw'):chapters.append({'time':frames/30,'title':chapter_by_old[oi]})
 frames+=round((s['out']-s['in'])*30);s['timeline_out']=frames/30
m.update(version=4,status='Proposed refinement; host review and final hook selection pending',segments=segs,chapters=chapters,duration=frames/30,output_file='refinement-v4/el-cruce-proposed-cut-v4.mp4',work_folder='refinement-v4-full')
m['hooks']=[]
p=H/'edit-manifest-v4.json'
if p.exists():raise FileExistsError(p)
p.write_text(json.dumps(m,indent=2)+'\n')
print(len(segs),'segments',frames/30,'seconds; net',frames/30-1378.466667,flush=True)
spec=importlib.util.spec_from_file_location('renderer',R/'render-review.py');renderer=importlib.util.module_from_spec(spec);spec.loader.exec_module(renderer)
renderer.render(segs,H/'el-cruce-proposed-cut-v4.mp4',H/'render-work',chapters)
