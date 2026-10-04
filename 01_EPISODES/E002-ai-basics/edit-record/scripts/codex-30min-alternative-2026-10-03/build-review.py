from pathlib import Path
import json,html,shutil
H=Path(__file__).resolve().parent
P=json.loads((H/'edit-decisions.json').read_text());C=json.loads((H/'source-caption-cues.json').read_text())
def hms(t,precise=False):
 m=int(t)//60;s=t-m*60;return f'{m:02d}:{s:06.3f}' if precise else f'{m:02d}:{int(s):02d}'
def srtstamp(t):
 ms=round(t*1000);hr,ms=divmod(ms,3600000);mi,ms=divmod(ms,60000);s,ms=divmod(ms,1000);return f'{hr:02d}:{mi:02d}:{s:02d},{ms:03d}'
# Cue repairs only at newly edited boundaries; original caption proof status remains.
first_after={1:140.680,2:312.960,3:748.314,4:1287.773,5:1499.053,6:1985.500,7:2508.567,8:2650.013,9:2756.267,10:2817.607,11:2874.147,12:2931.187}
retimed=[];caption_repairs=[]
for i,s in enumerate(P['segments']):
 a=s['source_start_frame']/30;b=s['source_end_frame']/30;new=s['output_start_frame']/30
 cues=[]
 for original in C:
  c=dict(original)
  if i and c['start']<first_after[i]-0.002:continue
  if c['end']<=a or c['start']>=b:continue
  overlap=min(b,c['end'])-max(a,c['start'])
  if overlap/(c['end']-c['start'])<0.45 and c['end']>b:continue
  if i and abs(c['start']-first_after[i])<0.002:
   c['start']=a
   if i==3:c['text']="I'm "+c['text']
   caption_repairs.append({'segment':i+1,'source_first_cue':original['start'],'retained_start':a,'text':c['text']})
  if i==11 and c['start']>2880 and 'But it is a little' in c['text']:
   c['text']=c['text'].split('But it is a little')[0].strip()
  x=max(a,c['start']);y=min(b,c['end'])
  if y-x<0.12:continue
  cues.append({'start':new+x-a,'end':new+y-a,'text':c['text']})
 if cues and b-a>1 and b-(a+cues[-1]['end']-new)<0.8:cues[-1]['end']=new+b-a
 retimed+=cues
retimed.sort(key=lambda c:c['start'])
for i,c in enumerate(retimed[:-1]):c['end']=min(c['end'],retimed[i+1]['start'])
retimed=[c for c in retimed if c['end']-c['start']>=0.10]
assert all(0<=c['start']<c['end']<=P['duration_seconds']+.001 for c in retimed)
srt='\n\n'.join(f"{i}\n{srtstamp(c['start'])} --> {srtstamp(c['end'])}\n{c['text']}" for i,c in enumerate(retimed,1))+'\n'
(H/'episode-001-30min-alternative.srt').write_text(srt)
(H/'episode-001-30min-alternative.vtt').write_text('WEBVTT\n\n'+'\n\n'.join(f"{srtstamp(c['start']).replace(',','.')} --> {srtstamp(c['end']).replace(',','.')}\n{c['text']}" for c in retimed)+'\n')
(H/'retimed-caption-cues.json').write_text(json.dumps(retimed,indent=2)+'\n')
(H/'caption-boundary-repairs.json').write_text(json.dumps(caption_repairs,indent=2)+'\n')
md=['# Episode 001: what this 30:03 alternative removes','', 'This is an **alternative**, not a selected replacement. It uses the 52:25.733 pop-up-free version as its source. All source times below refer to that version, **not the raw shoot**. The 52-minute version remains intact.','',f"The new cut is {hms(P['duration_seconds'],True)}. Twelve content cuts remove {hms(P['removed_content_seconds'],True)}; short dissolves overlap another {P['transition_overlap_seconds']:.3f} seconds. Total reduction: 22:22.200.",'','The car analogy, model training, tokens, full math disagreement, coding-midterm story, human-skills perspective, on-prem/cloud explanation, leader introductions/rankings and recent-chat examples remain. The selected hook, covered-lens opening, recurring intro/music, exact Episode 000 outro and no-pop-up choice remain.','', 'These are pacing/topic-focus choices. Removed content is not being classified as unusable or definitively wrong. The largest tradeoffs are Cuts 04–07.','', '| Cut | Time in full version | Removed | New join | What is removed |','| --- | --- | --- | --- | --- |']
transcript=['Episode 001: removed-material transcript','Times refer to the 52:25.733 full cut. Caption text is an existing draft, not certified verbatim audio.','']
reviewcuts=[]
for c in P['cuts']:
 a,b=c['start'],c['end'];join=c['new_join_midpoint_seconds'];ex=[r for r in C if r['end']>a and r['start']<b]
 d={**c,'start_label':hms(a,True),'end_label':hms(b,True),'removed_label':hms(c['removed_seconds'],True),'join_label':hms(join,True),'transcript':[dict(time=hms(r['start']),text=r['text']) for r in ex]};reviewcuts.append(d)
 md.append(f"| {c['number']:02d} | {hms(a,True)}–{hms(b,True)} | {hms(c['removed_seconds'],True)} | {hms(join,True)} | {c['title']} |")
for c in reviewcuts:
 md+=['',f"## Cut {c['number']:02d}: {c['title']}",'',f"**Full version:** {c['start_label']}–{c['end_label']}. **Alternative join:** {c['join_label']}.",'',c['reason'],'', '**Removed material begins:** '+c['transcript'][0]['text'], '**Removed material ends:** '+c['transcript'][-1]['text']]
 transcript += [f"CUT {c['number']:02d}: {c['title']}",f"{c['start_label']}–{c['end_label']}",c['reason'],'']+[f"[{r['time']}] {r['text']}" for r in c['transcript']]+['']
md+=['','## Review efficiently','','Open `review.html`, or use the local review page opened in Codex. Each cut has **Play removed**, **Play new join**, and **Read removed transcript** controls. Start with Cuts 06 (6:24 economics) and 07 (4:15 safety), then Cuts 04–05 (jobs/access discussion). If you prefer any material restored, refer to its numbered cut.','', 'Technical checks and sampled picture/word-boundary review do not establish continuous human listening, caption auditory proof or exact-version host approval. This alternative is not uploaded or published.']
(H/'removed-footage.md').write_text('\n'.join(md)+'\n');(H/'removed-material-transcript.txt').write_text('\n'.join(transcript)+'\n')
(H/'review-data.json').write_text(json.dumps({'runtime':P['duration_seconds'],'cuts':reviewcuts},indent=2)+'\n')
for name in ['teachers.ttf','teachers-OFL.txt']:
 target=H/name
 if not target.exists():shutil.copy2(H.parents[3]/'03_ASSETS/brand-fonts'/name,target)
data=json.dumps({'runtime':P['duration_seconds'],'cuts':reviewcuts},ensure_ascii=False).replace('</','<\\/')
page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Episode 001: review the shorter cut</title>
<style>@font-face{font-family:Teachers;src:url(teachers.ttf)}*{box-sizing:border-box}body{margin:0;background:#FBF1E5;color:#0B2A45;font-family:Teachers,system-ui,sans-serif;font-size:18px;line-height:1.45}header{background:#38B6FF;padding:28px max(20px,calc((100vw - 1180px)/2));}h1{font-size:clamp(30px,4vw,52px);line-height:1.02;font-weight:800;margin:0 0 12px}h2{margin:0;font-size:25px;line-height:1.1}p{margin:12px 0}main{max-width:1180px;margin:auto;padding:24px 20px}.playerbox{position:sticky;top:0;background:#FBF1E5;border-bottom:2px solid #0B2A45;padding:12px 0 16px;z-index:2}video{display:block;background:#0B2A45;width:100%;max-height:55vh;aspect-ratio:16/9}button,a.button{border:2px solid #0B2A45;background:#0B2A45;color:#FDF8F2;font:600 17px Teachers,system-ui;cursor:pointer;padding:10px 14px;text-decoration:none;display:inline-block}button.secondary{background:#FDF8F2;color:#0B2A45}.buttons{display:flex;gap:10px;flex-wrap:wrap;margin:12px 0 0}.status{font-weight:600;margin:6px 0 0}.note{font-size:16px}section.cut{border:2px solid #0B2A45;padding:20px;margin:20px 0;background:#FDF8F2}section.cut.flagged{border-color:#0E6FC0;background:#E9F5FF}.times{font-weight:600;color:#0E6FC0;font-size:17px;margin-top:10px}.number{font-weight:800;color:#0E6FC0}.reason{max-width:85ch}details{margin-top:14px}summary{cursor:pointer;font-weight:600}blockquote{border-left:3px solid #A9DCFF;margin:14px 0;padding-left:14px;max-height:360px;overflow:auto}blockquote p{margin:0 0 8px;font-size:17px}label{display:block;margin-top:14px;cursor:pointer}input{width:18px;height:18px;margin-right:8px;vertical-align:middle}.footer{padding:18px;background:#0B2A45;color:#FDF8F2;margin-top:30px}a{color:#0E6FC0}@media(max-width:650px){.playerbox{position:static}h2{font-size:23px}.cut{padding:16px!important}button{font-size:16px}}</style>
<header><h1>EPISODE 001<br>REVIEW THE SHORTER CUT</h1><p>30:03 instead of 52:25. Same hook, intro/outro and no pop-ups.</p></header><main>
<p>This is one alternative. The full version is preserved. These cuts focus the episode on the AI landscape and your best exchanges; they do not label the removed material unusable.</p>
<div class="playerbox"><video id="player" controls preload="metadata" src="episode-001-30min-alternative.mp4"></video><p id="status" class="status">Alternative version · 30:03</p><div class="buttons"><button id="fullAlt">Watch full alternative</button><button class="secondary" id="fullOriginal">Watch full 52-minute version</button><button class="secondary" id="stop">Stop clip</button></div></div>
<p><strong>Fastest review:</strong> start with Cuts 06 and 07, which remove the economics and safety detours. Then review Cuts 04–05, which shorten the jobs/access discussion. “Play removed” uses the full version; “Play new join” gives six seconds before and after the transition.</p><p class="note">Times are from the 52:25 full cut, not the raw shoot. Flag any cut you want restored, then download your review notes. Text uses the existing captions; the playable clip is the reference for exact wording.</p>
<div id="cuts"></div><div class="footer"><button id="download" class="secondary">Download my restoration notes</button><p class="note">The flags are review notes; they do not change the video. This local alternative has not been uploaded or published. Captions are retimed drafts.</p></div>
</main><script>
const DATA=__DATA__, player=document.getElementById('player'),status=document.getElementById('status');
const sources={alt:'episode-001-30min-alternative.mp4',original:'../codex-no-popups-2026-10-03/episode-001-no-popups.mp4'};
let activeMode='alt',stopAt=null;const flags=new Set();try{JSON.parse(localStorage.getItem('e001-30min-restore')||'[]').forEach(n=>flags.add(n))}catch{}
async function playRange(mode,start,end,label){stopAt=end;status.textContent=label;if(activeMode!==mode){activeMode=mode;player.src=sources[mode];player.load();await new Promise((resolve,reject)=>{player.addEventListener('loadedmetadata',resolve,{once:true});player.addEventListener('error',reject,{once:true})})}player.currentTime=Math.max(0,start);try{await player.play()}catch{status.textContent=label+' · press play to begin'}}
player.addEventListener('timeupdate',()=>{if(stopAt!==null&&player.currentTime>=stopAt){player.pause();stopAt=null}});
document.getElementById('fullAlt').onclick=()=>playRange('alt',0,null,'Alternative version · 30:03');document.getElementById('fullOriginal').onclick=()=>playRange('original',0,null,'Full pop-up-free version · 52:25');document.getElementById('stop').onclick=()=>{player.pause();stopAt=null};
for(const c of DATA.cuts){const section=document.createElement('section');section.className='cut'+(flags.has(c.number)?' flagged':'');section.id='cut-'+c.number;const title=document.createElement('h2');title.textContent=String(c.number).padStart(2,'0')+' · '+c.title;section.append(title);const times=document.createElement('p');times.className='times';times.textContent='Full version: '+c.start_label+'–'+c.end_label+' · Removed: '+c.removed_label+' · New join: '+c.join_label;section.append(times);const reason=document.createElement('p');reason.className='reason';reason.textContent=c.reason;section.append(reason);const buttons=document.createElement('div');buttons.className='buttons';const removed=document.createElement('button');removed.textContent='Play removed';removed.onclick=()=>{playRange('original',c.start,c.end,'Cut '+c.number+' removed material · full version');player.scrollIntoView({behavior:'smooth',block:'center'})};const join=document.createElement('button');join.className='secondary';join.textContent='Play new join';join.onclick=()=>{playRange('alt',c.new_join_midpoint_seconds-6,Math.min(DATA.runtime,c.new_join_midpoint_seconds+6),'Cut '+c.number+' new transition · alternative');player.scrollIntoView({behavior:'smooth',block:'center'})};buttons.append(removed,join);section.append(buttons);const details=document.createElement('details');const summary=document.createElement('summary');summary.textContent='Read removed transcript';details.append(summary);const quote=document.createElement('blockquote');for(const r of c.transcript){const p=document.createElement('p');p.textContent=r.time+' · '+r.text;quote.append(p)}details.append(quote);section.append(details);const label=document.createElement('label');const check=document.createElement('input');check.type='checkbox';check.checked=flags.has(c.number);check.onchange=()=>{if(check.checked)flags.add(c.number);else flags.delete(c.number);section.classList.toggle('flagged',check.checked);try{localStorage.setItem('e001-30min-restore',JSON.stringify([...flags]))}catch{}};label.append(check,document.createTextNode('Flag this cut to restore'));section.append(label);document.getElementById('cuts').append(section)}
document.getElementById('download').onclick=()=>{const selected=DATA.cuts.filter(c=>flags.has(c.number));const lines=['Episode 001: review of 30:03 alternative','Restore these numbered cuts:',...selected.map(c=>String(c.number).padStart(2,'0')+' · '+c.start_label+'–'+c.end_label+' · '+c.title)];if(!selected.length)lines.push('No cuts flagged for restoration.');const link=document.createElement('a');const url=URL.createObjectURL(new Blob([lines.join('\\n')+'\\n'],{type:'text/plain'}));link.href=url;link.download='episode-001-restoration-notes.txt';link.click();setTimeout(()=>URL.revokeObjectURL(url),1000)};
</script></html>'''.replace('__DATA__',data)
(H/'review.html').write_text(page)
print('Created review page, complete removed transcripts, numbered cut list, retimed SRT/VTT and chapter sidecars.',len(retimed),'cues.')
