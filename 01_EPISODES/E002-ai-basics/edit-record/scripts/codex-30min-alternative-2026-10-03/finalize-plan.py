from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent
SOURCE=(H.parent/'codex-no-popups-2026-10-03/episode-001-no-popups.mp4').resolve()
rows=json.loads((H/'provisional-cuts.json').read_text())
bounds=[(104.833333,140.666667),(253.866667,312.6),(665.433333,748.2),(1113.466667,1287.266667),(1355.533333,1499.0),(1601.466667,1985.333333),(2252.6,2507.9),(2590.5,2650.333333),(2704.633333,2756.033333),(2788.933333,2817.6),(2852.1,2874.5),(2886.033333,2931.233333)]
# These are proposals against the 52:25.733 clean cut, not against the raw shoot.
cuts=[]
for n,(r,(a,b)) in enumerate(zip(rows,bounds),1):
 c={**r,'number':n,'start_frame':round(a*30),'end_frame':round(b*30),'transition_frames':4 if n in (6,7) else 2}
 c['start']=c['start_frame']/30;c['end']=c['end_frame']/30;c['removed_seconds']=(c['end_frame']-c['start_frame'])/30
 c['retained_before_and_after']='Complete clause boundaries checked using source captions, local audio re-transcription/token alignment and the original picture.'
 cuts.append(c)
segments=[];cursor=0;out=0
for i,end in enumerate([c['start_frame'] for c in cuts]+[94372]):
 transition=0 if i==0 else cuts[i-1]['transition_frames']
 out-=transition
 seg={'id':f'{i+1:02d}','source_start_frame':cursor,'source_end_frame':end,'output_start_frame':out,'incoming_transition_frames':transition}
 out+=end-cursor;seg['output_end_frame']=out
 segments.append(seg)
 if i<len(cuts):
  cuts[i]['new_join_start_frame']=out-cuts[i]['transition_frames'];cuts[i]['new_join_midpoint_seconds']=(out-cuts[i]['transition_frames']/2)/30
  cursor=cuts[i]['end_frame']
plan={'title':'Episode 001: 30-minute alternative','status':'editorial proposal; not selected or published','source':str(SOURCE),'source_sha256':'e5ee8b93c9a621f6700e6df1d311fe5289321eaf58c95002087a98a5f6656bea','source_frames':94372,'fps':30,'total_frames':out,'duration_seconds':out/30,'removed_content_seconds':sum(c['removed_seconds'] for c in cuts),'transition_overlap_seconds':sum(c['transition_frames'] for c in cuts)/30,'cuts':cuts,'segments':segments,'popups':0,'reordered_speech':False,'retained_hook_and_recurring_cards':True}
with (H/'edit-decisions.json').open('x') as f:json.dump(plan,f,indent=2);f.write('\n')
def mapped(t):
 frame=round(t*30)
 for s in segments:
  if s['source_start_frame']<=frame<s['source_end_frame']:return s['output_start_frame']+frame-s['source_start_frame']
 return None
# Chapter boundaries are at real retained topic changes; platform spacing checked below.
rawchap=[(0,'Data centers on the moon? + AI intro'),(69.2,'Who actually builds the models'),(140.8,'Claude vs. ChatGPT: what we use'),(313.0,'Gemini, the Dodgers of AI'),(380.5,'Open vs. closed: how models learn'),(529.1,'The car analogy: models vs. apps'),(748.4,'Why are the model names so bad?'),(806.0,'Tokens are gas'),(875.4,'Are mathematicians out of a job?'),(1287.6,'Mary’s coding midterm (29 or 92?)'),(1499.2,'What we’re betting on: being human'),(1985.6,'On-prem vs. the cloud (and the moon)'),(2105.4,'Dario and the Anthropic origin story'),(2509.0,'Sam, Zuck, and Elon'),(2756.4,'Ranking the AI leaders'),(2961.5,'Mary’s last three AI chats and goodbye')]
chapters=[{'frame':mapped(t),'title':title,'source_seconds':t} for t,title in rawchap];assert all(c['frame'] is not None for c in chapters)
assert all(b['frame']-a['frame']>=900 for a,b in zip(chapters,chapters[1:]));assert out-chapters[-1]['frame']>=900
(H/'chapters.json').write_text(json.dumps(chapters,indent=2)+'\n')
def stamp(f):
 sec=f/30;return f'{int(sec)//60:02d}:{int(sec)%60:02d}'
(H/'chapters.txt').write_text('\n'.join(f"{stamp(c['frame'])} {c['title']}" for c in chapters)+'\n')
meta=[';FFMETADATA1','title=Out of Our Depth | Episode 001 | 30-minute alternative','comment=Local editorial alternative; no definition or correction pop-ups; not published']
for i,c in enumerate(chapters):
 end=chapters[i+1]['frame'] if i+1<len(chapters) else out
 meta+=['[CHAPTER]','TIMEBASE=1/30000',f'START={c["frame"]*1000}',f'END={end*1000}',f'title={c["title"]}']
(H/'alternative.ffmeta').write_text('\n'.join(meta)+'\n')
source_desc=(H.parents[1]/'description-and-chapters.txt').read_text();before,after=source_desc.split('Chapters\n',1);after=after[after.index('Out of Our Depth:'):]
(H/'description-and-chapters.txt').write_text(before+'Chapters\n'+(H/'chapters.txt').read_text()+'\n'+after)
print(json.dumps({'total_frames':out,'runtime_seconds':out/30,'content_removed_seconds':plan['removed_content_seconds'],'cuts':len(cuts)},indent=2))
print((H/'chapters.txt').read_text())
