from pathlib import Path
import json,re,textwrap,csv
R=Path(__file__).resolve().parent;m=json.loads((R/'edit-manifest-v2.json').read_text());names={'A':'093614','B':'142133','C':'145211'}
db={k:json.loads((R/'source-review'/f'{n}-transcript.json').read_text())['transcription'] for k,n in names.items()}
corrections=[(r'\b[Cc]hat G[Bb][Tt]\b','ChatGPT'),(r'\b[Cc]hat GPT\b','ChatGPT'),(r'\b[Cc]hat gbt\b','ChatGPT'),(r'\bget hub\b','GitHub'),(r'\bgithub\b','GitHub'),(r'\b[Vv]er[cs]el\b','Vercel'),(r'\bversatile\b','Vercel'),(r'\b[Vv]ersail(?:les)?\b','Vercel'),(r'\b[Ee]l [Cc]ru(?:ce|se|sade|sades)\b','El Cruce'),(r'\belk crusade\b','El Cruce'),(r'\bgranola\b','Granola'),(r'\b[Cc]omposio\b','Composio'),(r'\bsick of Antic\b','sycophantic'),(r'\bclawed\b','Claude'),(r'\bclod\b','Claude'),(r'\bChina and Claude\b','Chat and Claude'),(r'\bTaping through it\b','Take me through it'),(r'\bin value\b','and valued'),(r'\bElle crusade\b','El Cruce'),(r'\bher no law\b','Granola'),(r'\btrack across country\b','track and cross country')]
def clean(s):
 for a,b in corrections:s=re.sub(a,b,s)
 s=re.sub(r'\s+([,.?!;:])',r'\1',s)
 return re.sub(r'\s+',' ',s).strip()
def ts(t,sep=','):
 ms=max(0,round(t*1000));h,ms=divmod(ms,3600000);mi,ms=divmod(ms,60000);se,ms=divmod(ms,1000);return f'{h:02}:{mi:02}:{se:02}{sep}{ms:03}'
def cues(segments):
 out=[];cursor=0
 for s in segments:
  dur=s['out']-s['in']
  if s.get('source_id'):
   selected=[]
   for row in db[s['source_id']]:
    for t in row['tokens']:
     if t['id']>=50000:continue
     a=t['offsets']['from']/1000;b=t['offsets']['to']/1000
     if s['in']-.025<=a<s['out'] and b>=s['in']:
      selected.append((max(cursor,cursor+a-s['in']),min(cursor+dur,cursor+max(a+.03,b)-s['in']),t['text']))
   group=[]
   for t in selected:
    if group and t[2].startswith(' ') and t[2].strip() not in ['.', ',', '?', '!', ';', ':'] and (t[0]-group[0][0]>4.6 or len(''.join(x[2] for x in group))+len(t[2])>82):
     out.append([group[0][0],max(x[1] for x in group),clean(''.join(x[2] for x in group))]);group=[]
    group.append(t)
   if group:out.append([group[0][0],max(x[1] for x in group),clean(''.join(x[2] for x in group))])
  cursor+=dur
 fixed=[]
 for i,(a,b,s) in enumerate(out):
  if not s:continue
  nxt=out[i+1][0] if i+1<len(out) else cursor
  b=min(max(b,a+.35),nxt-.02,cursor)
  if b>a:fixed.append((a,b,s))
 return fixed
for file,segments in [('el-cruce-proposed-cut-v2',m['segments'])]+[(f'captions/{Path(h["file"]).stem}',h['segments']) for h in m['hooks']]:
 dest=R/file;dest.parent.mkdir(exist_ok=True)
 cc=cues(segments)
 dest.with_suffix('.srt').write_text('\n\n'.join(f'{i+1}\n{ts(a)} --> {ts(b)}\n'+ '\n'.join(textwrap.wrap(s,42)) for i,(a,b,s) in enumerate(cc))+'\n')
 dest.with_suffix('.vtt').write_text('WEBVTT\n\n'+'\n\n'.join(f'{ts(a,".")} --> {ts(b,".")}\n'+ '\n'.join(textwrap.wrap(s,42)) for a,b,s in cc)+'\n')
 for i,(a,b,s) in enumerate(cc):
  assert 0<=a<b<=sum(x['out']-x['in'] for x in segments)+.001
  if i:assert a>=cc[i-1][1]
(R/'caption-review-status-v2.json').write_text(json.dumps({'status':'Draft sidecars corrected for terminology, retimed to exact edit; auditory proof still required','engine':'local whisper.cpp small.en, full-source transcripts','corrections':corrections,'full_cue_count':len(cues(m['segments'])),'structural_checks':'All cues nonnegative, nonoverlapping and inside corresponding output duration'},indent=2))
with (R/'edit-decision-list-v2.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['clip','source','source_in','source_out','final_in','final_out','picture','reason'])
 for s in m['segments']:w.writerow([s['id'],s['source'],ts(s['in']),ts(s['out']),ts(s['timeline_in']),ts(s['timeline_out']),'screen and hosts' if s.get('screen') else 'card' if s.get('still') else 'hosts',s['reason']])
lines=['EL CRUCE | PROPOSED CUT V1','Host review pending. Captions need auditory proof.','', 'Try this: Before asking AI to build, give it your goals and constraints, ask what is missing, and define the smallest useful output.','', 'Josh and Mary use their El Cruce preparation to test ChatGPT as a planning partner: shared context, gear comparisons, a training calendar, a logistics checklist and a website they can open on a phone. The useful lesson is in the corrections, not a claim that AI can safely replace a qualified coach.','', 'CHAPTERS']
for c in m['chapters']:
 t=round(c['time']);lines.append(f'{t//60:02}:{t%60:02} {c["title"]}')
lines+=['','SOURCES','El Cruce organizer, 2026 edition: https://elcruce.com.ar/en/edicion-2026/','ChatGPT projects: https://learn.chatgpt.com/docs/projects','Prompting: https://learn.chatgpt.com/docs/prompting','Work capabilities and permissions: https://learn.chatgpt.com/docs/enterprise/chatgpt-work-overview','','Recorded October 2, 2026. Tool interfaces and account access shown are those used during the recording. Training outputs are this experiment\'s artifacts, not verified coaching or medical guidance. No flight purchase or form submission is established by this cut.']
(R/'description-and-chapters-draft.txt').write_text('\n'.join(lines)+'\n')
print('Caption and timeline sidecars written:',len(cues(m['segments'])),'full cues')
