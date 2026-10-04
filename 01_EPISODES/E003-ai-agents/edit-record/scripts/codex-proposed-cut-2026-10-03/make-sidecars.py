"""Caption drafts and a reversible editorial review package, from the exact manifest."""
from pathlib import Path
import json,re,textwrap,csv,html
R=Path(__file__).resolve().parent
M=json.loads((R/'edit-manifest-v4.json').read_text())
T=json.loads((R/'source-review/transcript-full.json').read_text())['segments']
G=json.loads((R.parents[3]/'03_ASSETS/jtan-captions/glossary.json').read_text())
def tc(t,ms=False):
 n=round(t*1000);h,n=divmod(n,3600000);m,n=divmod(n,60000);s,n=divmod(n,1000)
 return f'{h:02}:{m:02}:{s:02}'+(f',{n:03}' if ms else '')
def fix(t):
 for rule in G['fix']:
  for p in rule['patterns']:t=re.sub(p,lambda m:rule['term'],t,flags=re.I)
 for p,v in [(r'\bchat\s*g[pb]2\b','ChatGPT'),(r'\bproject\s+venn\b','Project Vend'),(r'\bSAS\b','SaaS'),(r'\bGrok ?bot\b','Grokbot'),(r'\bOpen ?Claw\b','OpenClaw'),(r'\bhard[- ](barreled|boiled)\b','hard-boiled')]:t=re.sub(p,v,t,flags=re.I)
 return t.strip()
def words():
 out=[];word=None
 for seg in T:
  for t in seg['tokens']:
   if t['id']>=50000:continue
   a=t['offsets']['from']/1000;b=t['offsets']['to']/1000;s=t['text']
   if s.startswith(' ') or word is None:
    if word:out.append(word)
    word=[a,b,s.strip()]
   else:word[1]=max(word[1],b);word[2]+=s
 if word:out.append(word)
 return out
W=words()
def captions(segs,path):
 cues=[]
 for s in segs:
  if s['kind']!='camera':continue
  chosen=[]
  for a,b,t in W:
   if a>=s['out'] or b<=s['in']:continue
   if a<s['in']-.2:continue
   if 2703<=a<2909:t=re.sub(r'\bdaddy\b','Dottie',t,flags=re.I)
   if 640<=a<765:t=re.sub(r'\bcontacts?\b','context',t,flags=re.I)
   a=max(a,s['in'])-s['in']+s['timeline_in'];b=min(b,s['out'])-s['in']+s['timeline_in']
   chosen.append([a,max(a+.035,b),t])
  group=[]
  def flush():
   if not group:return
   start,end=group[0][0],min(group[-1][1],s['timeline_out']);txt=fix(' '.join(w[2] for w in group))
   txt='\n'.join(textwrap.wrap(txt,width=42,break_long_words=False,break_on_hyphens=False))
   if txt and end>start:cues.append([start,end,txt])
  for w in chosen:
   text=' '.join(v[2] for v in group+[w])
   if group and (len(text)>67 or w[1]-group[0][0]>4.4 or w[0]-group[-1][1]>.8):flush();group=[]
   group.append(w)
  flush()
 for i,c in enumerate(cues[:-1]):c[1]=min(c[1],cues[i+1][0])
 cues=[c for c in cues if c[1]>c[0]]
 for i,c in enumerate(cues):assert c[1]>c[0] and (i==0 or c[0]>=cues[i-1][1]) and len(c[2].splitlines())<=2,(i,c)
 srt='\n\n'.join(f'{i+1}\n{tc(a,True)} --> {tc(b,True)}\n{t}' for i,(a,b,t) in enumerate(cues))+'\n'
 path.with_suffix('.srt').write_text(srt);path.with_suffix('.vtt').write_text('WEBVTT\n\n'+re.sub(r'(\d{2}:\d{2}:\d{2}),(\d{3})',r'\1.\2',srt))
 return {'cues':len(cues),'status':'ASR draft; glossary corrected; host listening and name proofing pending','nonoverlapping':True,'max_lines':2}
checks={'main':captions(M['segments'],R/'agents-proposed-cut-v4')}
for h in M['hooks']:checks[h['id']]=captions(h['segments'],R/h['file'])
(R/'qc/caption-structure.json').write_text(json.dumps(checks,indent=2)+'\n')
chapters='\n'.join(f'{tc(c["time"])[3:]} {c["title"]}' for c in M['chapters'])+'\n'
assert M['chapters'][0]['time']==0 and all(b['time']-a['time']>=30 for a,b in zip(M['chapters'],M['chapters'][1:])) and M['duration']-M['chapters'][-1]['time']>=30
(R/'chapters.txt').write_text(chapters)
retained=sorted((s['in'],s['out']) for s in M['body']+[s for s in M['segments'] if s['kind']=='covered-transition']);merged=[]
for a,b in retained:
 if merged and a<=merged[-1][1]+.001:merged[-1][1]=max(b,merged[-1][1])
 else:merged.append([a,b])
removed=[];pos=0
for a,b in merged:
 if a>pos:removed.append([pos,a])
 pos=b
if pos<4224.566667:removed.append([pos,4224.566667])
def reason(a,b):
 if b<=64:return 'Setup, retakes and production chatter.'
 if a<123.2:return 'Historical Operator retelling: wrong product name, amount and request. Replaced with already-recorded hypothetical.'
 if a<641.9:return 'Long first attempt at components, interruptions and retakes; clearer later take retained.'
 if a<794:return 'Duplicated explanation and transition.'
 if a<986:return 'Restart or repeated transition.'
 if a<1199:return 'Unverified Gartner quantity / Duplex detail, repeated wording, or transition.'
 if a<1351:return 'Parallel-only subagent definition; the recorded correction is retained.'
 if a<1549:return 'Repetition or diffuse setup; stronger personal-agent explanation retained.'
 if a<1742:return 'Workplace and wellbeing generalizations, production interruptions and less useful detour.'
 if a<1883:return 'Unsupported numerical hallucination analogy and speculative mechanism; accurate basic definition retained.'
 if a<1973:return 'Uncertain dates or unmeasured generalized model-improvement claim.'
 if a<2194:return 'Repetitive guardrail discussion and explanatory detour.'
 if a<2408:return 'Production aside, incomplete product critique, or unverified funding/team/privacy assertions.'
 if a<2579.4:return 'Detour, or unverified current monetization/tier/cap assertions.'
 if a<3011.5:return 'Repetition, incorrect/current-eligibility and future rollout claims, rumors or unsupported legal-letter account.'
 if a<3029.6:return 'Unverified first-ever agent-superlative.'
 if a<3378:return 'Speculative vendor motives; medical and legal generalizations without suitable evidence; diffuse pricing setup.'
 if a<3814:return 'Unverified precise unit price / medical pricing; long SaaS-margin detour with weak causal claims.'
 if a<3907.6:return 'Gym analogy repetition; setup and useful payoff retained.'
 if a<4178.1:return 'Undercooked-egg safety reassurance removed; personal taste discussion retained.'
 return 'After-signoff production talk.'
with (R/'removed-ranges.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['source_start','source_end','duration_seconds','reason'])
 for a,b in removed:w.writerow([tc(a,True),tc(b,True),round(b-a,3),reason(a,b)])
log=['# Proposed cut — editorial record','',f'Source: `{M["source"]}`. Source recording: 70:24.567. Proposed export: {tc(M["duration"],True)}; {M["total_frames"]:,} frames. Eight previews: 900 frames / 30 seconds each.','',
 'Status: proposed, exact-version host approval pending. Big Egg is the provisional assembled opening, not a host selection. All raw material stays intact. Every boundary can be recovered through the manifest and source timestamps.','',
 'The cut uses the cleaner components retake, preserves the workflow/agent distinction, subagent correction, Project Vend, limited personal-product trials, trust/permissions, outcome pricing, and the closing egg argument. It retains laughs, tangents and meaningful contributions from both hosts.','',
 'The Operator retelling was removed because it misstates the product, request and amount. The recording already contains a generic egg-shopping example; that plays first, followed by the hosts’ egg-buying reaction moved from earlier in the source. No new host speech or synthetic correction was added. The cold-open excerpts recur in their longer context later.','',
 'Evidence boundaries: product trials and refunds are host-reported experiences, not independently verified transactions or comparative benchmarks. Hypothetical examples and predictions remain clearly conversational. Project Vend is a vendor-reported office experiment; the host’s “a little better” is an assessment, not a quantified phase-two comparison.','',
 'Verification: complete source transcript reviewed; source and export frames sampled; automated audio/export/caption-structure checks recorded in qc/. Continuous listening, exact-version lip sync, conversational joins and caption names still require host review. This environment does not establish a continuous audiovisual listening pass.','',
 '## Retained sequence','']
for s in M['segments']:
 log.append(f'- Output {tc(s["timeline_in"],True)}–{tc(s["timeline_out"],True)} ← '+(f'source {tc(s["in"],True)}–{tc(s["out"],True)}' if s['kind'] in ('camera','covered-transition') else 'recurring brand card and music')+f': {s["reason"]}')
log+=['','## Removed source ranges','']
for a,b in removed:log.append(f'- {tc(a,True)}–{tc(b,True)} ({b-a:.1f}s): {reason(a,b)}')
(R/'edit-notes.md').write_text('\n'.join(log)+'\n')
review=['# Proposed cut — mapped transcript (ASR draft)','']
for s in M['segments']:
 review+=['',f'## Output {tc(s["timeline_in"],True)} — '+(f'Source {tc(s["in"],True)}–{tc(s["out"],True)}' if s['kind']=='camera' else ('Covered camera / outro music' if s['kind']=='covered-transition' else 'Brand card')),s['reason'],'']
 if s['kind']=='camera':
  txt=fix(' '.join(w[2] for w in W if w[0]>=s['in']-.2 and w[0]<s['out'] and w[1]>s['in']))
  if 2703<=s['in']<2909:txt=re.sub(r'\bdaddy\b','Dottie',txt,flags=re.I)
  if 640<=s['in']<765:txt=re.sub(r'\bcontacts?\b','context',txt,flags=re.I)
  review.append(txt)
(R/'proposed-cut-transcript.md').write_text('\n'.join(review)+'\n')
omitted=['REMOVED SOURCE MATERIAL — ASR DRAFT; all original footage remains intact.','']
for a,b in removed:
 omitted+=[f'SOURCE {tc(a,True)}–{tc(b,True)} | {reason(a,b)}',fix(' '.join(w[2] for w in W if a<=w[0]<b)),'']
(R/'removed-material-transcript.txt').write_text('\n'.join(omitted)+'\n')
review_flags=[]
for s in M['segments']:
 if s['kind']=='camera':
  text=' '.join(w[2] for w in W if s['in']<=w[0]<s['out'])
  for pattern in [r'Joshua Hunter Island',r'\bKaysha\b',r'\bKeshav\b',r'\bclaw ?bot\b',r'\bcontext\b',r'\bguard\b']:
   if re.search(pattern,text,re.I):review_flags.append({'output_time':tc(s['timeline_in'],True),'source_in':tc(s['in'],True),'term':pattern,'action':'Listen and proof exact word/name; no synthetic rewriting.'})
(R/'qc/caption-proof-flags.json').write_text(json.dumps(review_flags,indent=2)+'\n')
readme='''# Agents — proposed final cut v4

Current version: `agents-proposed-cut-v4.mp4` — **37:13.667**. Eight hook-only previews are **30.000 seconds each**, including their recurring card/music tail. Big Egg is the provisional cold open; choose another preview before final lock if preferred. The superseded v1 and v3 work renders are preserved; v2 was interrupted and is incomplete. v4 carries the completed hand-cover gesture into the outro and masks the message-list screen. Dialogue and its audio are the same as v3.

Open `review.html` through `serve-review.py` for the episode, hook comparison, chapter jumps and removed-source review. The MP4s also play independently. Adjacent SRT/VTT files are editable caption drafts. `chapters.txt` is the draft shared chapter list.

Recommended hooks: **1 Big Egg** for the absurd premise and both hosts; **2 Five-minute audition** for Mary's sharp personal verdict; **3 Baby** for the unexpected punchline. Options 4–8 offer other funny exchanges. Each preview ends after the card; it does not append the full episode.

Source: `/Users/je/Movies/Agents episode.mp4` (70:24.567), unchanged. `edit-manifest-v4.json`, `edit-decision-list-v4.csv`, `removed-ranges.csv` and `edit-notes.md` make all choices reversible. `proposed-cut-transcript.md` maps the actual output; `source-review/transcript-full.txt` retains the full ASR source.

The claim register is `../../../../02_RESEARCH/codex-agents-recording-fact-check-2026-10-03.md`. Export and audio results are recorded in `qc/`; source/mix/encoder evidence is retained in `source-review/` and `work/`.

Status: **proposed for host review; not approved or published**. Automated checks and sampled pictures do not establish continuous listening or host approval. Hosts should check pacing, laughter, lip sync and conversational joins; proof captions, especially Dottie, Clawdbot and personal names; select the hook. No external delivery or publication was performed.
'''
(R/'README.md').write_text(readme)
print(json.dumps({'captions':checks,'removed_ranges':len(removed),'unique_source_retained_seconds':sum(b-a for a,b in merged)},indent=2))
