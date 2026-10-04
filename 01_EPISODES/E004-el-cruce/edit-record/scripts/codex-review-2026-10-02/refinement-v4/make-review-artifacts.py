from pathlib import Path
import json,csv,re,textwrap,html,copy
H=Path(__file__).resolve().parent;R=H.parent
m=json.loads((H/'edit-manifest-v4-final.json').read_text())
# Reuse only pure caption helpers; the prior script's top-level writes are excluded.
src=(R/'make-sidecars-v3.py').read_text().split('for file,segments in ')[0]
src=src.replace("R=Path(__file__).resolve().parent;m=json.loads((R/'edit-manifest-v3.json').read_text());names=",'names=')
src=src.replace("a<s['out']","a<s.get('audio_out',s['out'])")
ns={'__file__':str(R/'make-sidecars-v3.py'),'R':R,'m':m};exec(src,ns)
focused=json.loads((H/'source-review/focused-clips-map.json').read_text())
def shifted(rows,base):
 rows=copy.deepcopy(rows)
 for row in rows:
  row['offsets']={k:v+round(base*1000) for k,v in row['offsets'].items()}
  for t in row['tokens']:t['offsets']={k:v+round(base*1000) for k,v in t['offsets'].items()}
 return rows
for clip in focused:
 if clip['name'] not in ('opening','instructions','baseline','output-options','learning-together'):continue
 sid=clip['source_id'];rows=shifted(json.loads((H/'source-review/focused'/f'{clip["name"]}.json').read_text())['transcription'],clip['in'])
 tokens=[t for row in ns['db'][sid] for t in row['tokens'] if not clip['in']<=t['offsets']['from']/1000<clip['out']]
 tokens += [t for row in rows for t in row['tokens'] if t['offsets']['to']>=t['offsets']['from'] and not (clip['name']=='instructions' and t['offsets']['from']>=748050)]
 ns['db'][sid]=[{'tokens':sorted(tokens,key=lambda t:t['offsets']['from'])}]
ns['corrections'] += [(r'\bChad\b','Chat'),(r'\bchat gbt\b','ChatGPT'),(r'\bRunYourCity\b','Run Your City'),(r'\bvision taping through it\b','vision. Take me through it')]
cc=ns['cues'](m['segments']);ts=ns['ts']
stem=H/'el-cruce-refined-v4'
stem.with_suffix('.srt').write_text('\n\n'.join(f'{i+1}\n{ts(a)} --> {ts(b)}\n'+'\n'.join(textwrap.wrap(t,42)) for i,(a,b,t) in enumerate(cc))+'\n')
stem.with_suffix('.vtt').write_text('WEBVTT\n\n'+'\n\n'.join(f'{ts(a,".")} --> {ts(b,".")}\n'+'\n'.join(textwrap.wrap(t,42)) for a,b,t in cc)+'\n')
assert all(0<=a<b<=m['duration'] for a,b,t in cc)
assert all(cc[i][0]>=cc[i-1][1] for i in range(1,len(cc)))
(H/'caption-review-status.json').write_text(json.dumps({'status':'Draft; source terminology corrected and exact final timeline retimed; auditory wording proof pending','full_cue_count':len(cc),'structural_checks':'Nonnegative, nonoverlapping, within final duration'},indent=2))
with (H/'edit-decision-list-v4.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['clip','prior_clip','source','source_in','source_out','final_in','final_out','picture','reason'])
 for s in m['segments']:w.writerow([s['id'],s['prior_segment_id'],s['source'],ts(s['in']),ts(s['out']),ts(s['timeline_in']),ts(s['timeline_out']),'screen and hosts' if s.get('screen') else 'card' if s.get('still') else 'hosts',s['reason']])
lengths={'A':4409.966667,'B':1011.733333,'C':1898.4}
with (H/'omitted-source-ranges-v4.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['source_id','source_in','source_out','seconds','status'])
 for sid,total in lengths.items():
  ranges=sorted((s['in'],s['out']) for s in m['segments'] if s.get('source_id')==sid);merged=[]
  for a,b in ranges:
   if merged and a<=merged[-1][1]+.001:merged[-1][1]=max(b,merged[-1][1])
   else:merged.append([a,b])
  last=0
  for a,b in merged+[[total,total]]:
   if a-last>.001:w.writerow([sid,ts(last),ts(a),round(a-last,3),'Preserved original; omitted from proposed full cut'])
   last=b
chapters=['EL CRUCE | PROPOSED REFINEMENT V4','Host approval and final hook selection pending.','', 'Give AI your goals and constraints, ask what is missing, and decide what a usable result looks like before building.','', 'Josh and Mary turn race preparation into a practical test of AI planning: context, instructions, effort settings, gear comparisons, calendar corrections, logistics and a website on a phone. The additions preserve their disagreements, reversals and working-style banter.','', 'CHAPTERS']
for c in m['chapters']:
 t=round(c['time']);chapters.append(f'{t//60:02}:{t%60:02} {c["title"]}')
assert m['chapters'][0]['time']==0
assert all(m['chapters'][i]['time']-m['chapters'][i-1]['time']>=30 for i in range(1,len(m['chapters'])))
assert m['duration']-m['chapters'][-1]['time']>=30
chapters+=['','Recorded October 2, 2026. Training outputs remain this experiment’s artifacts; medical decisions stay with qualified clinicians. The calendar, messaging and evolving-plan alternatives are proposed workflows, not verified completed automations.','', 'SOURCE REGISTER','https://elcruce.com.ar/en/edicion-2026/','https://learn.chatgpt.com/docs/projects','https://learn.chatgpt.com/docs/models','https://learn.chatgpt.com/docs/enterprise/chatgpt-work-overview']
(H/'description-and-chapters-draft.txt').write_text('\n'.join(chapters)+'\n')
buttons=''.join(f'<button data-time="{c["time"]}"><span>{int(c["time"])//60:02}:{int(c["time"])%60:02}</span> {html.escape(c["title"])}</button>' for c in m['chapters'])
page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>El Cruce • Revised episode</title><style>@font-face{font-family:Teachers;src:url('../../../../../03_ASSETS/brand-fonts/teachers.ttf')}*{box-sizing:border-box}body{background:#FDF8F2;color:#0b2a45;font:18px Teachers,system-ui;margin:0}main{max-width:1160px;margin:auto;padding:32px 24px}header{display:flex;justify-content:space-between;align-items:center;gap:20px}.logo{background:#38B6FF;color:#FBF1E5;width:146px;height:146px;display:flex;flex-direction:column;justify-content:center;padding:12px;font-weight:800;line-height:.88;flex:none}.logo span{font-size:17px;white-space:nowrap}.logo b{font-size:37px;white-space:nowrap}h1{font-size:clamp(30px,5vw,54px);line-height:1.05;margin:24px 0 8px}p{line-height:1.5}video{width:100%;background:#0b2a45;border-radius:12px;margin:12px 0}a{color:#0E6FC0}section{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:24px;margin-top:24px}button{display:block;width:100%;text-align:left;padding:12px;margin:6px 0;border:1px solid #A9DCFF;background:#fff;border-radius:7px;cursor:pointer;color:#0b2a45;font:inherit}button:hover{background:#A9DCFF}button span{font-variant-numeric:tabular-nums;margin-right:8px}.tag{font-size:14px;background:#A9DCFF;padding:8px 12px;border-radius:20px}li{margin:10px 0;line-height:1.4}@media(max-width:700px){section{grid-template-columns:1fr}main{padding:22px 16px}}</style><main><header><div class="logo"><span>OUT OF OUR</span><b>DEPTH</b></div><span class="tag">Proposed refinement • host review pending</span></header><h1>El Cruce, with more of the good stuff.</h1><p><b>29:18</b> • A shorter introduction, useful restored moments, and a signoff that ends on the covered camera.</p><video id="episode" controls preload="metadata"><source src="el-cruce-refined-v4.mp4" type="video/mp4"><track label="English draft" kind="captions" srclang="en" src="el-cruce-refined-v4.vtt"></video><section><div><h2>Jump into the episode</h2>BUTTONS</div><div><h2>What changed</h2><ul><li>Removed the first, repeated El Cruce introduction.</li><li>Restored useful disagreement about verbosity, effort settings, missing context and output choices.</li><li>Restored the ten-minute constraint and your working-style banter.</li><li>Added context before the calendar and account-routing mistakes.</li><li>Tightened sentence boundaries and a long calendar-inspection pause.</li><li>Cut to the recurring outro while the lens is fully covered.</li></ul><p>The full-cut cold open is still an editorial placeholder. Your <a href="../hook-shortlist-2026-10-02/compare.html">two funny hook finalists</a> remain available for selection; the previews sent to Mary are preserved.</p><p><a href="../title-and-thumbnail-options.txt">Title and thumbnail options</a> · <a href="description-and-chapters-draft.txt">Chapters</a> · <a href="README.md">Review notes</a></p><p>All joins were checked against transcripts, source audio timing and sampled frames. Continuous listening and caption wording still need host review.</p><p><a href="../start-here-v3-preserved.html">Original ten-hook comparison page</a> · <a href="../el-cruce-proposed-cut-v3.mp4">Earlier 22:58 cut</a></p></div></section></main><script>const p=document.querySelector('#episode');document.querySelectorAll('[data-time]').forEach(b=>b.addEventListener('click',()=>{p.currentTime=Number(b.dataset.time);p.play()}));</script></html>'''.replace('BUTTONS',buttons)
(H/'review.html').write_text(page)
print('Wrote',len(cc),'draft caption cues and review sidecars')
