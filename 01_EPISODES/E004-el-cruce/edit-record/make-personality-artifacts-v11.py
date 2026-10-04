from pathlib import Path
import copy, csv, html, json, re, textwrap

Q = Path(__file__).resolve().parent
E = Q.parents[2]
R = E / 'edit/codex-review-2026-10-02'
m = json.loads((Q/'edit-manifest-v11-final.json').read_text())
src = (R/'make-sidecars-v3.py').read_text().split('for file,segments in ')[0]
src = src.replace("R=Path(__file__).resolve().parent;m=json.loads((R/'edit-manifest-v3.json').read_text());names=", 'names=')
src = src.replace("s['in']-.025<=a<s['out']", "s.get('audio_in',s['in'])-.025<=a<s.get('audio_out',s['out'])")
ns = {'__file__':str(R/'make-sidecars-v3.py'), 'R':R, 'm':m}
exec(src,ns)

def patch_transcript(sid, start, end, path):
    rows = copy.deepcopy(json.loads(path.read_text())['transcription'])
    for row in rows:
        for t in row['tokens']:
            t['offsets'] = {k:v+round(start*1000) for k,v in t['offsets'].items()}
    tokens = [t for row in ns['db'][sid] for t in row['tokens'] if not start<=t['offsets']['from']/1000<end]
    tokens += [t for row in rows for t in row['tokens'] if t['offsets']['to']>=t['offsets']['from'] and start<=t['offsets']['from']/1000<end]
    ns['db'][sid] = [{'tokens':sorted(tokens,key=lambda t:t['offsets']['from'])}]

oldfocus = R/'refinement-v4/source-review'
for c in json.loads((oldfocus/'focused-clips-map.json').read_text()):
    patch_transcript(c['source_id'],c['in'],c['out'],oldfocus/'focused'/f"{c['name']}.json")
for name,start,end in [('voice',1380,1455),('effort',2520,2559),('baseline',2620,2705),('intro',38,56)]:
    patch_transcript('A',start,end,Q/'focused'/f'{name}.json')
ns['corrections'] += [(r'\bChad\b','Chat'),(r'\bRunYourCity\b','Run Your City'),(r'\b[Ss]peech ?ify\b','Speechify'),(r'\bget hub\b','GitHub')]
segs = copy.deepcopy(m['segments'])
for s in segs:
    if s.get('source_id') not in 'ABC':
        s.pop('source_id',None)
cc = [(0,2.433,'♪ We are so chaotic ♪'),(2.8,5.8,'Do you think I should become a singer?'),(5.82,6.5,'Probably…'),(6.5,8.3,'NOT.')]+ns['cues'](segs)
ts = ns['ts']
assert all(0<=a<b<=m['duration']+.001 for a,b,t in cc)
assert all(cc[i][0]>=cc[i-1][1] for i in range(1,len(cc)))
stem=Q/'el-cruce-personality-v11'
stem.with_suffix('.srt').write_text('\n\n'.join(f'{i+1}\n{ts(a)} --> {ts(b)}\n'+'\n'.join(textwrap.wrap(t,42)) for i,(a,b,t) in enumerate(cc))+'\n')
stem.with_suffix('.vtt').write_text('WEBVTT\n\n'+'\n\n'.join(f'{ts(a,".")} --> {ts(b,".")}\n'+'\n'.join(textwrap.wrap(t,42)) for a,b,t in cc)+'\n')
profanity = [{'time':a,'text':t} for a,b,t in cc if re.search(r'\b(?:shit|fuck\w*|bitch\w*|asshole\w*)\b',t,re.I)]
(Q/'caption-review-status-v11.json').write_text(json.dumps({'status':'Draft English sidecars; terminology corrected and focused source transcripts patched. Continuous auditory wording proof remains pending.','cue_count':len(cc),'checks':{'all_nonoverlapping':True,'all_within_exact_timeline':True},'explicit_profanity_matches':profanity},indent=2)+'\n')
with (Q/'edit-decision-list-v11.csv').open('w') as f:
    w=csv.writer(f);w.writerow(['clip','source_id','source_path','source_in','source_out','final_in','final_out','picture','reason'])
    for s in m['segments']:
        w.writerow([s['id'],s.get('source_id'),s['source'],ts(s['in']),ts(s['out']),ts(s['timeline_in']),ts(s['timeline_out']),s.get('picture'),s['reason']])

lengths={'A':4409.966667,'B':1011.733333,'C':1898.4}
def cut_reason(sid,a,b):
    if a<47 and b<90:return 'Pre-roll, recording setup or abandoned opening; the covered-camera start and clean opening are retained.'
    if (sid=='A' and a<877 and b>748) or (sid=='B' and a<959 and b>516):return 'Remove the brushing-off/arguing stretch, repetition and idle iteration; preserve the constructive discussion before and after.'
    if sid=='A' and a<2206 and b>1575:return 'Repeated troubleshooting and model/voice speculation; retain the actual voice test, written-versus-spoken observation and clear request for a useful plan.'
    if sid=='A' and a<2584 and b>2338:return 'Build waiting, repeated setup, profanity and unsupported tier/pricing explanation; retain the reasoning-effort lesson.'
    if sid=='A' and a<3432 and b>2889:return 'Long draft/prescription reading, duplicated requests and unsupported running baseline; keep the email connection and speaker-context lesson.'
    if sid=='A' and a<3904 and b>3657:return 'Repeated website requests, build waiting and speculation; keep the concrete next-step observation and gear task.'
    if sid=='C' and a<943 and b>843:return 'Unverified flight/separate-ticket guidance and intervening repetition; retain the comparison request and workflow alternatives.'
    if sid=='C' and a<1273 and b>1030:return 'Build waiting and repeat troubleshooting; go from the reflection to the actual result.'
    if sid=='C' and a<1832 and b>1815:return 'Remove the incorrect suggestion that hosting itself fixes responsive layout; retain the code-versus-link explanation.'
    if sid=='C' and a<1546 and b>1385:return 'Repeated setup and interim discussion. Selected reflection and final signoff are reordered after the result for a complete ending.'
    if b-a<12:return 'Tighten an abandoned start, pause, filler or partial sentence; join at a complete phrase.'
    return 'Repeated or lower-value troubleshooting, waiting, tangents or less useful detail; retain the clearer demonstration and real reactions.'
omitted=[]
for sid,total in lengths.items():
    ranges=sorted((s['in'],s['out']) for s in m['segments'] if s.get('source_id')==sid)
    merged=[]
    for a,b in ranges:
        if merged and a<=merged[-1][1]+.001:merged[-1][1]=max(b,merged[-1][1])
        else:merged.append([a,b])
    last=0
    for a,b in merged+[[total,total]]:
        if a-last>.001:omitted.append({'source_id':sid,'in':last,'out':a,'reason':cut_reason(sid,last,a)})
        last=b
(Q/'omitted-source-ranges-v11.json').write_text(json.dumps(omitted,indent=2)+'\n')
with (Q/'omitted-source-ranges-v11.csv').open('w') as f:
    w=csv.writer(f);w.writerow(['source_id','source_in','source_out','seconds','reason'])
    for x in omitted:w.writerow([x['source_id'],ts(x['in']),ts(x['out']),round(x['out']-x['in'],3),x['reason']])

assert m['chapters'][0]['time']==0
assert all(m['chapters'][i]['time']-m['chapters'][i-1]['time']>=30 for i in range(1,len(m['chapters'])))
assert m['duration']-m['chapters'][-1]['time']>=30
chapters=[f'{int(c["time"])//60:02}:{int(c["time"])%60:02} {c["title"]}' for c in m['chapters']]
(Q/'chapters-v11.txt').write_text('\n'.join(chapters)+'\n')
(Q/'description-and-chapters-draft-v11.txt').write_text('EL CRUCE | DESCRIPTION DRAFT — HOST APPROVAL PENDING\n\nJosh and Mary try turning an ambitious race into an AI planning experiment: shared context, a coach-and-logistics brief, gear preferences, a calendar and a website they actually want to use. The laughs, corrections and different working styles show what makes an AI request useful—and why thinking before you hit Enter matters.\n\n'+ '\n'.join(chapters)+'\n\nRecorded October 2, 2026. Tool interfaces and account access reflect this recording. Training plans remain unverified experiment outputs; medical decisions stay with qualified clinicians. Proposed calendar, check-in and purchasing workflows are not established as completed automations.\n')
outline=['# El Cruce — what stays and what goes','', '**Current review cut: 44:49.833. Host approval pending.**','', '## What is restored and retained','', '- **Opening personality and the real brief:** continuous opening banter, the geography story, the race stakes, Mary’s full coach/logistics goals, medical context and approval before purchases. The brief gives the experiment a purpose beyond one race.','- **A visible AI process:** brainstorm → context → instructions → ask what is missing → propose a plan → review the result. Keep substantive input from both hosts, including Mary’s request to read the screen aloud.','- **Voice, with the interesting discovery:** the actual test, running/music/tree joke, Mary asking for more depth, and the difference between the spoken summary and the written response. Remove the slow repeated troubleshooting.','- **Judgment and constraints:** different athletic goals, the clinician boundary, shared training anchors, flexible weekly feedback, preferences and budget. These are demonstration inputs, not verified coaching advice.','- **Your chemistry through the middle:** the slow-reading reaction, cute shared-anchors response, shopping story, AIs-in-cahoots joke, ten-minute constraint and affectionate design-versus-words contrast.','- **Mary’s practical insights:** finish the last 20%, reduce mental load, define the smallest useful result and ask for format options before building. Josh’s milestone approach and corrections stay alongside these.','- **Real output inspection:** AI-slop reactions, out-of-order calendar days, specific design feedback, sycophancy, account permissions, the improved website, checkboxes and moving a workout.','- **A complete payoff:** repository/deployment explanation, explicit sharing destination, Mary receiving the link, wedding/anniversary and varnish analogies, good-enough judgment, learning out loud and the covered-camera signoff.','', '## What is removed','', '- The requested arguing/brushing-off stretches; retain the constructive alternatives and affectionate disagreement.','- Extended build waits, resets, repeated prompts, abandoned starts and repeated inspections with no new insight.','- Unsupported historical climbing numbers, pricing/model-tier ratios, news attribution, browser-capability rankings and the claim that hosting fixes responsive design.','- The inaccurate running-baseline request and casual ramp-up reassurance; keep the clinical boundary.','- An unverified “today is the last day” claim and separate-ticket flight guidance.','- Profanity-bearing source passages; no detected explicit profanity remains in the draft captions. Captions still need an auditory wording proof.','- The last hand withdrawal. The signoff cuts to the recurring outro with the lens covered.','', '## Presentation and review limits','', '- **Chosen C layout throughout screen scenes:** inset shared screen, larger overlapping hosts, foam background. No added teaching cards, headings or screen-scene logos. Camera-only scenes stay full-screen.','- Show captured screen activity whenever it is actually available. Mary’s shoe screenshots were on her separate device, which was not captured; that story uses the real hosts/phone footage rather than an unrelated desktop screen.','- The selected singing hook includes the extra half-second laugh before the recurring intro card/music. The original outro/music is retained.','- Quiet AI readings are boosted with timing preserved and human interruptions protected, then mastered with the whole episode. Subjective balance and lip sync remain host-review items.','- The edit is deliberately longer than the prior 29:18 version. The additional time preserves context, relationship moments and complete reflections, rather than more waiting.','', '## Reversible source trail','', 'Every included interval and its reason is in [the edit list](edit-decision-list-v11.csv). All omitted source intervals are in [the cut list](omitted-source-ranges-v11.csv); no original is removed. A/B/C refer to the 09:36, 14:21 and 14:52 camera recordings.','', 'The minute-by-minute choices are editorial proposals. Continuous host viewing, subjective rhythm, final caption wording, title/thumbnail selection and exact-version approval remain open.']
(Q/'include-and-cut-notes-v11.md').write_text('\n'.join(outline)+'\n')
buttons=''.join(f'<button data-time="{c["time"]}"><span>{int(c["time"])//60:02}:{int(c["time"])%60:02}</span> {html.escape(c["title"])}</button>' for c in m['chapters'])
cuts=''.join(f'<button data-source="{x["source_id"]}" data-start="{x["in"]}" data-end="{x["out"]}">{x["source_id"]} {ts(x["in"],".")[:-4]}–{ts(x["out"],".")[:-4]} · {html.escape(x["reason"])}</button>' for x in omitted if x['out']-x['in']>=5)
page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>El Cruce · New episode</title><style>@font-face{font-family:Teachers;src:url('teachers.ttf')}*{box-sizing:border-box}body{margin:0;background:#FDF8F2;color:#0b2a45;font:18px Teachers,system-ui}main{max-width:1180px;margin:auto;padding:28px 22px}h1{font-size:clamp(32px,5vw,56px);line-height:1.05;margin:18px 0}p,li{line-height:1.5}video{width:100%;background:#0b2a45;border-radius:10px}a{color:#0e6fc0}section{display:grid;grid-template-columns:1fr 1fr;gap:26px;margin-top:24px}button{display:block;width:100%;text-align:left;border:1px solid #a9dcff;background:#fff;color:#0b2a45;border-radius:7px;font:inherit;padding:12px;margin:7px 0;cursor:pointer}button:hover{background:#a9dcff}.tag{display:inline-block;padding:8px 14px;border-radius:20px;background:#a9dcff;font-size:15px}summary{cursor:pointer;font-size:24px;font-weight:bold;margin:24px 0 12px}#raw{display:none}.note{font-size:15px}button span{font-variant-numeric:tabular-nums;margin-right:8px}@media(max-width:700px){section{grid-template-columns:1fr}}</style><main><span class="tag">New full episode · host review pending</span><h1>More of you. A clearer AI journey.</h1><p><b>44:50</b> · Your chosen C layout, singing hook, full opening context and a covered-camera ending.</p><video id="episode" controls preload="metadata"><source src="el-cruce-personality-v11.mp4" type="video/mp4"><track kind="captions" label="English draft" srclang="en" src="el-cruce-personality-v11.vtt"></video><section><div><h2>Jump into the episode</h2>BUTTONS</div><div><h2>What changed</h2><ul><li>Restored the opening banter and Mary’s complete AI brief.</li><li>Kept real reactions, different working styles and useful judgment from both of you.</li><li>Made the experiment easier to follow: context, plan, feedback and a real result.</li><li>Removed the requested arguments, repeated waiting and unsupported claims.</li><li>Used the selected screen/hosts layout, without added text cards.</li><li>Boosted quiet AI readings and tightened incomplete phrases.</li></ul><p><a href="include-and-cut-notes-v11.md">Full include/cut guide</a> · <a href="chapters-v11.txt">Chapters</a> · <a href="title-and-thumbnail-options.txt">Title and thumbnail options</a> · <a href="el-cruce-personality-v11.mp4" download>Download episode</a></p><p class="note">Draft captions are included. Final wording, subjective sound/rhythm and your approval of this exact cut remain open. No publication or new external sharing has happened.</p></div></section><details><summary>Review material left out</summary><p>These buttons play the original camera ranges omitted from this proposal. A is the morning recording; B and C are the two afternoon recordings. Originals are preserved.</p><video id="raw" controls preload="none"></video><p id="rawlabel"></p>CUTS</details></main><script>const p=document.querySelector('#episode'),r=document.querySelector('#raw'),label=document.querySelector('#rawlabel');let stop=Infinity;document.querySelectorAll('[data-time]').forEach(b=>b.onclick=()=>{r.pause();p.currentTime=+b.dataset.time;p.play()});document.querySelectorAll('[data-source]').forEach(b=>b.onclick=()=>{p.pause();r.style.display='block';const url='/sources/'+b.dataset.source+'.mp4';stop=+b.dataset.end;label.textContent=b.textContent;r.src=url;r.onloadedmetadata=()=>{r.currentTime=+b.dataset.start;r.play()};r.scrollIntoView({behavior:'smooth',block:'center'})});r.ontimeupdate=()=>{if(r.currentTime>=stop)r.pause()};</script></html>'''.replace('BUTTONS',buttons).replace('CUTS',cuts)
(Q/'review-v11.html').write_text(page)
print(json.dumps({'cues':len(cc),'omitted_intervals':len(omitted),'profanity':profanity,'duration':m['duration']}))
