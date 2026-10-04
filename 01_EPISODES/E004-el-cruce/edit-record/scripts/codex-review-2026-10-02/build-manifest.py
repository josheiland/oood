from pathlib import Path
import json,copy
R=Path(__file__).resolve().parent
repo=Path('/Users/je/oood')
paths={k:f'/Users/je/Movies/2026-10-02 {v}.mp4' for k,v in [('A','09-36-14'),('B','14-21-33'),('C','14-52-11')]}
screens=json.loads((R/'source-review/screens-inventory.json').read_text())
sc={k:next(s['path'] for s in screens if name in s['path']) for k,name in [('A','9.36'),('B','2.21'),('C','2.51')]}
off={'A':1.0725,'B':4.3703,'C':10.7038}
body=[]
def f(t):return round(t*30)/30
def add(k,a,b,reason,chapter=None,popup=None,demos=()):
 boundaries=sorted(set([a,b]+[t for u,v,*_ in demos for t in [u,v] if a<t<b]))
 for j,(u,v) in enumerate(zip(boundaries,boundaries[1:])):
  s={'source':paths[k],'source_id':k,'in':f(u),'out':f(v),'reason':reason}
  if chapter and j==0:s['chapter']=chapter
  if popup and j==0:s.update(popup=f'graphics/{popup}-popup.png',popup_in=1,popup_out=min(8,v-u-.1))
  for ds,de,label,crop in demos:
   if ds<=u<de:s.update(screen=sc[k],screen_offset=off[k],layout=f'graphics/{label}-layout.png',crop=crop)
  body.append(s)
add('A',65.88,84.84,'Open on genuine energy and the race premise.','A real project: 100 km, two different goals')
add('A',125.30,163.58,'Brief race stakes, friends and the run/walk contrast; approximate distance stays qualified.')
add('A',185.45,203.00,'Name the coaching job without extended race questions.')
add('A',244.02,269.08,'Name the logistics job; preserve Mary\'s taste and purchase-approval constraint.')
add('A',305.53,352.85,'Record the brainstorm, create a project and ask what information is missing.','Give AI context before asking it to build',popup='context')
add('A',376.03,404.20,'Mary supplies real running background and bone-health constraints; omit unsupported rucking claims.')
add('A',426.48,442.65,'Mary explains her competitive motivation.')
add('A',457.43,524.92,'Personalized goals, age correction, shared training and day-three support.')
add('A',553.80,601.72,'Compare ways to turn spoken notes into project instructions.',demos=[(553.8,582,'context',[110,95,850,930])])
add('A',660.30,689.65,'Dictate the instruction-building request.',demos=[(660.30,689.65,'context',[110,95,850,930])])
add('A',876.38,928.84,'After removing production reset, retain chosen instructions and saving them.',demos=[(896.0,928.84,'context',[110,95,850,930])])
add('A',994.90,1004.35,'Explain that new project chats start with saved instructions.')
add('A',2205.58,2261.60,'Ask for an actual usable output and describe checking off or moving workouts.','Specify the output and ask for a plan')
add('A',2307.05,2338.90,'Ask it to outline the plan and missing inputs before executing.',popup='plan')
add('A',2621.42,2644.48,'Retain AI response framing the gap between current baseline and race demands.',demos=[(2621.42,2644.48,'plan',[480,125,1080,900])])
add('A',2688.28,2701.20,'Keep baseline questions and explicit clinician boundary; omit lengthy generic training lecture.',demos=[(2688.28,2701.20,'plan',[480,125,1080,900])])
add('A',2877.20,2889.88,'Explain using already connected email as source context.')
add('A',3357.42,3373.90,'Explicitly label who is speaking when providing joint context.')
add('A',3626.40,3657.44,'Explain that a useful plan needs to be revisable.')
add('A',4003.74,4031.60,'Start a separate gear chat inside the same project.')
add('B',26.88,47.32,'Time jump to the shopping update; preserve credit-card joke.','Choose options that fit your taste')
add('B',87.14,115.88,'Mary gives concrete screenshot-shortlist technique instead of generic recommendations.',popup='preferences')
add('B',173.37,195.20,'Reveal the first generated training-plan layout.',demos=[(173.37,195.2,'check',[970,155,950,880])])
add('B',224.22,254.88,'Ask to remove clutter and focus on the actual plan.')
add('B',280.64,333.36,'Keep the out-of-order calendar failure and targeted feedback.','Check the first attempt',demos=[(287.68,319.92,'check',[460,125,1140,850])])
add('B',477.30,516.64,'Preserve both views: brain dump for mental load, then align and tackle one task at a time.')
add('C',183.52,215.44,'Reveal prioritized logistics list and the massage exchange.','Turn logistics into a checklist',demos=[(183.52,200.0,'logistics',[460,125,1140,850])])
add('C',219.56,239.56,'Request a sheet with deadlines and flight comparisons.',popup='logistics')
add('C',322.08,380.20,'Specific design feedback, honest frustration and Claude/Chat joke.','Coach the output',demos=[(322.08,345.0,'feedback',[750,155,1170,880])])
add('C',844.84,875.16,'Flight alternative as observed recommendation, preserving need to check it; no booking implied.')
add('C',1272.24,1328.96,'Reveal improved website and check-off/move-day controls; genuine reactions.','A result you can actually use',demos=[(1298.04,1328.96,'result',[260,145,1640,870])])
add('C',1342.56,1364.92,'Show compact overview and ask to publish/share the usable version.',demos=[(1342.56,1355.84,'result',[260,145,1640,870])])
add('C',1545.05,1575.70,'Plain-language introduction to GitHub as project file storage.')
add('C',1577.74,1602.70,'Explain hosting and sending a link, based on the observed workflow.')
add('C',1681.54,1703.45,'Keep wrong-workspace delivery as a real lesson about specifying the destination.')
add('C',1797.76,1815.92,'Mary opens the received link and reacts to the actual result.')
add('C',1831.94,1847.45,'Keep accurate responsive-code/shared-link explanation; remove false claim hosting itself fixes spacing.')
add('C',675.64,775.92,'Move recorded reflection after the outcome: prioritize essentials and specify what to build.','What we would do differently',popup='result')
add('C',794.90,843.04,'Ask for alternative output formats before building.')
add('C',1485.27,1507.80,'Keep why learning together matters and laughing at the process.')
add('C',1851.24,1887.40,'Stop at good enough; honest end-of-experiment joke.')
add('C',1510.48,1517.90,'Use the complete flippity-flop signoff rather than the interrupted final signoff.')
intro={'source':str(repo/'03_ASSETS/music/oood-sting-5s.wav'),'in':0,'out':158/30,'still':str(repo/'03_ASSETS/codex-mono-mirrored-3digit/intro-card.png'),'reason':'Approved recurring intro and sting','gain_db':-3}
outro={'source':str(repo/'03_ASSETS/music/oood-outro-11s.wav'),'in':0,'out':323/30,'still':str(repo/'03_ASSETS/codex-mono-mirrored-3digit/outro-card.png'),'reason':'Approved recurring three-prompt outro and music','gain_db':-3}
choices=[
 ('01','we-dont-like-that','C',752.36,764.70,'The brief was the problem','Strongest teaching hook: a vague request creates work you never wanted.'),
 ('02','how-inspiring','C',1283.72,1296.10,'How inspiring, my love','The couple dynamic, with the actual plan as the payoff.'),
 ('03','claude-slop','C',357.32,370.95,'The ultimate insult','Funny and AI-specific; keep the joke as opinion, not prompting advice.'),
 ('04','credit-cards','B',26.96,34.32,'I drained our credit cards','Fast, clear relationship hook; less teaching promise than option 1.'),
 ('05','know-ourselves','A',457.43,469.74,'Context starts with your age','The need for personalization lands with a real correction.'),
 ('06','dusts-me','A',474.75,483.53,'She leaves me behind','Different goals, genuine chemistry; race-led opening.'),
 ('07','calendar','B',293.04,303.48,'It cannot order the weekdays','Concrete AI failure; main episode shows the actual calendar.'),
 ('08','time-is-money','C',648.92,662.38,'Time is money, my friend','Cost versus speed, framed as the hosts\' experience.'),
 ('09','perfect-trap','C',34.44,45.65,'The perfection trap','Useful and warm; introduces the episode\'s central tension.'),
 ('10','race-was-shorter','C',1879.0,1887.4,'The race might be shorter','Self-deprecating payoff; strongest for returning viewers.')]
hooks=[]
for num,slug,k,a,b,title,why in choices:
 h={'source':paths[k],'source_id':k,'in':f(a),'out':f(b),'reason':'Intentional cold-open repeat; '+why}
 remain_frames=900-round((h['out']-h['in'])*30)-158
 opening=copy.deepcopy(body[0]);opening['out']=body[0]['out'];opening.pop('chapter',None)
 hooks.append({'file':f'{num}-{slug}.mp4','title':title,'reason':why,'segments':[h,intro,opening]})
segments=[copy.deepcopy(hooks[0]['segments'][0]),intro]+body+[outro]
chapters=[{'time':0,'title':'The brief was the problem'}];cur=0
for i,s in enumerate(segments):
 s['timeline_in']=cur;s['timeline_out']=cur+(s['out']-s['in']);s['id']=f's{i:03d}'
 if s.get('chapter'):
  if cur-chapters[-1]['time']>=30:chapters.append({'time':cur,'title':s['chapter']})
  else:chapters[-1]['title']=s['chapter']
 cur=s['timeline_out']
m={'title':'We had to coach our AI coach','status':'Proposed review v1, host approval pending','fps':30,'screen_sync_note':'Screen time = camera time + offset. Audio correlation at start/middle/end is stable within 3 ms; original camera lip sync still needs human review.','segments':segments,'hooks':hooks,'chapters':chapters,'duration':cur}
(R/'edit-manifest-v1.json').write_text(json.dumps(m,indent=2))
print(f'{len(segments)} segments, {cur/60:.2f} minutes; 10 hooks with a complete shared opening')
