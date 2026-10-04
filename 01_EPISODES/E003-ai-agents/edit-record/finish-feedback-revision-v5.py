from pathlib import Path
import json,html,csv,subprocess,concurrent.futures,re,sys
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent;D=R/'feedback-revision-v5';M=json.loads((D/'edit-manifest-v5.json').read_text())
CORE=Path(M['output_file']).stem

def pictures():
    dest=D/'qc/pictures';dest.mkdir(exist_ok=False);items=[]
    for s in M['segments']:
        for label,t in [('start',s['timeline_in']+.1),('end',s['timeline_out']-.1)]:
            items.append((s['id']+'-'+label,D/M['output_file'],t))
    for name,t in [('hook-end',4.733333),('card-start',4.933333),('card-end',10.0),('opening-start',10.2),('opening-end',29.9)]:
        items.append(('preview-'+name,D/'agents-selected-opening-v5.mp4',t))
    def snap(item):
        name,path,t=item
        subprocess.run(['ffmpeg','-nostdin','-v','error','-ss',str(t),'-threads','1','-i',str(path),
            '-frames:v','1','-vf','scale=480:270','-n',str(dest/(name+'.jpg'))],capture_output=True,check=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(snap,items))
    for k in range(0,len(items),16):
        im=Image.new('RGB',(1920,1184),'#0b2842');draw=ImageDraw.Draw(im)
        for i,(name,path,t) in enumerate(items[k:k+16]):
            x=i%4*480;y=i//4*296;im.paste(Image.open(dest/(name+'.jpg')),(x,y));draw.text((x+5,y+274),f'{name} | {t:.3f}s',fill='white')
        im.save(dest/f'board-{k//16+1:02}.jpg')
    (dest/'sample-map.json').write_text(json.dumps([dict(name=a,file=str(b),time=c) for a,b,c in items],indent=2)+'\n')
    print('Sampled',len(items),'pictures',flush=True)

def finish():
    Q=json.loads((D/'qc/summary.json').read_text());assert Q['passed']
    assert Q['current_master']==M['output_file']=='agents-feedback-cut-v5-audio-matched.mp4'
    assert not any((D/name).exists() for name in ['review.html','README.md','HANDOFF.md'])
    by={s['id']:s for s in M['segments']}
    timings=[
        ('Egg reaction: full sentence lead-in',104.933333,by['s005']['timeline_in'],30),
        ('Guardrails: complete exchange into personal agents',1159,by['s023']['timeline_in'],30),
        ('OpenClaw into pricing: spoken topic bridge',1832.233333,by['pricing-bridge']['timeline_in'],45),
        ('Gym equipment → models; gym → AI tool provider',1925.666667,by['s035']['timeline_in']+(3883.966667-by['s035']['in']),65),
    ]
    entries=[]
    for title,before,after,dur in timings:
        entries.append(f'<article><h3>{html.escape(title)}</h3><button onclick="range(\'old\',{before-8},{before+dur-8})">Before · v4</button> <button onclick="range(\'main\',{after-8},{after+dur-8})">After · v5</button></article>')
    chapters=''.join(f'<button onclick="range(\'main\',{c["time"]},null)">{int(c["time"]//60):02}:{int(c["time"]%60):02} {html.escape(c["title"])}</button>' for c in M['chapters'])
    rows=[]
    for x in csv.DictReader((D/'removed-ranges.csv').open()):
        def sec(t):
            h,m,s=t.replace(',','.').split(':');return int(h)*3600+int(m)*60+float(s)
        a,b=sec(x['source_start']),sec(x['source_end']);rows.append(f'<tr><td><button onclick="range(\'raw\',{a},{b})">{x["source_start"]}–{x["source_end"]}</button></td><td>{html.escape(x["reason"])}</td></tr>')
    css='''@font-face{font-family:Teachers;src:url('../teachers.ttf')}*{box-sizing:border-box}body{margin:0;background:#f3e8dd;color:#0b2842;font:18px/1.5 Teachers,system-ui,sans-serif}header{background:#3daff4;padding:28px max(20px,calc((100vw - 1100px)/2))}main{max-width:1100px;margin:auto;padding:24px}h1{font-size:40px;line-height:1.15}video{display:block;width:100%;background:#0b2842;border-radius:8px}a{color:inherit;font-weight:bold}button{font:inherit;border:1px solid #0b2842;color:inherit;background:transparent;padding:9px 12px;border-radius:6px;cursor:pointer}.grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}article{background:#fff7ef;padding:16px;border-radius:8px}.chapters{display:flex;flex-wrap:wrap;gap:8px;margin:16px 0}.chapters button{font-size:15px}.status{background:#fff7ef;padding:18px;border-radius:8px}details{padding:15px;border:1px solid #b6ada4;border-radius:8px;margin:20px 0}summary{font-weight:bold;cursor:pointer}td{padding:12px 8px;border-bottom:1px solid #c9beb3;vertical-align:top;font-size:15px}td:first-child{min-width:220px}footer{font-size:15px;padding:20px 0}@media(max-width:700px){.grid{grid-template-columns:1fr}h1{font-size:30px}main{padding:16px}}'''
    page=f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>OOOD · Agents feedback cut v5</title><style>{css}</style>
<header><div>OUT OF OUR DEPTH · AGENTS · FEEDBACK CUT v5</div><h1>Your chosen hook, smoother joins, clearer pricing</h1><p>37:36.933 · Selected shortened 400-agents hook · Host review pending</p></header><main>
<div class="status">Your saved 4.833-second hook is incorporated. Restored the complete egg-reaction lead-in, the guardrails exchange before “Anyways,” Mary's request to explore outcome pricing, and the explicit gym-to-AI-provider comparison. Original files and earlier versions remain preserved.</div>
<h2>Updated episode</h2><video id="main" controls preload="metadata" src="{M['output_file']}"><track kind="captions" src="agents-feedback-cut-v5.vtt" srclang="en" label="English draft"></video>
<p><a href="{M['output_file']}" download>Download episode</a> · <a href="agents-feedback-cut-v5.srt" download>Caption draft</a> · <a href="chapters.txt">Chapters</a> · <a href="README.md">Changes and checks</a></p>
<details><summary>Jump to a chapter</summary><div class="chapters">{chapters}</div></details>
<h2>The selected 30-second opening</h2><video id="opening" controls preload="metadata" src="agents-selected-opening-v5.mp4"><track kind="captions" src="agents-selected-opening-v5.vtt" srclang="en" label="English draft"></video><p>4.833s saved hook → 5.267s recurring intro card/song → 19.9s episode opening. <a href="agents-selected-opening-v5.mp4" download>Download preview</a></p>
<h2>Compare the changes</h2><p>The shorter hook changes timestamps. These buttons seek to the corresponding moments in each version and stop after the comparison.</p><div class="grid">{''.join(entries)}</div>
<details id="old-wrap"><summary>Previous v4 for comparison</summary><video id="old" controls preload="metadata" src="../agents-proposed-cut-v4.mp4"></video></details>
<details><summary>Remaining omitted source · 32 intervals</summary><p>All original footage remains intact. <a href="removed-material-transcript.txt">Full omitted transcript</a> · <a href="removed-ranges.csv">Source ranges and reasons</a></p><video id="raw" controls preload="metadata" src="../source.mp4"></video><table>{''.join(rows)}</table></details>
<p><a href="proposed-cut-transcript.md">Mapped output transcript</a> · <a href="edit-decision-list-v5.csv">Reversible edit list</a> · <a href="qc/summary.json">Exact export checks</a> · <a href="../../../../../02_RESEARCH/codex-agents-feedback-fact-check-v5-2026-10-03.md">Restored-claim checks</a></p>
<footer>Full decode, coded H.264/color/MP4 structure, timestamps and loudness pass. Each retained camera range has sampled picture/waveform correspondence. Every boundary and the selected preview have sampled pictures. Continuous listening, original camera lip sync and caption-word proofing remain pending for this version. Your hook choice is recorded; full-episode approval and publication are separate. Nothing was uploaded, sent or published.</footer></main>
<script>const vids=[...document.querySelectorAll('video')],stops=new Map();vids.forEach(v=>{{v.addEventListener('play',()=>vids.forEach(o=>{{if(o!==v)o.pause()}}));v.addEventListener('timeupdate',()=>{{const t=stops.get(v);if(t!=null&&v.currentTime>=t){{v.pause();stops.delete(v)}}}})}});function range(id,a,b){{const v=document.getElementById(id);v.closest('details')?.setAttribute('open','');stops.set(v,b);v.currentTime=a;v.play().catch(()=>{{}});v.scrollIntoView({{behavior:'smooth',block:'center'}})}}</script></html>'''
    page=page.replace('agents-feedback-cut-v5.srt',CORE+'.srt').replace('agents-feedback-cut-v5.vtt',CORE+'.vtt')
    page=page.replace('agents-selected-opening-v5.mp4','agents-selected-opening-v5-audio-matched.mp4').replace('agents-selected-opening-v5.vtt','agents-selected-opening-v5-audio-matched.vtt')
    assert not (D/'review.html').exists();(D/'review.html').write_text(page)
    # The main local server serves this workspace subtree; its special claim-file
    # route does not expose files above the subtree. Keep an exact local copy.
    claims=R.parents[3]/'02_RESEARCH/codex-agents-feedback-fact-check-v5-2026-10-03.md'
    local=D/'restored-claim-check.md';local.write_text(claims.read_text())
    p=D/'review.html';p.write_text(p.read_text().replace('../../../../../02_RESEARCH/codex-agents-feedback-fact-check-v5-2026-10-03.md','restored-claim-check.md'))
    readme=f'''# Agents — feedback revision v5

Current master: `agents-feedback-cut-v5.mp4`, **37:36.933**, 67,708 frames, 1080p30. Your saved shortened 400-agents hook is incorporated exactly as supplied (145 frames / 4.833s). The source file remains in its original E004 folder; a byte-identical copy is in `source-review/`. Picture matching identifies it as this agents recording, not El Cruce.

Changes from v4:

- Restore the complete “It's important that you're telling a story…” lead-in before the egg-purchase reaction. New location: **01:25**; previously around 01:45.
- Restore the checker/guardrails exchange and its natural lead-out before “Anyways, let's get into personal agents.” New transition: **19:10.667**; previously around 19:18/19:19.
- Add Mary's already-recorded request to explore outcome pricing as the spoken bridge from personal agents. Starts **30:23.900**.
- Restore the explicit gym equipment → models / gym experience → AI tool provider mapping, plus the per-minute setup. Starts **32:05.367**. The gym efficiency/outcome payoff follows continuously.

The phone-message mask, completed covered-lens outro, recurring graphics/music, and all other retained conversation remain in place. Existing unsupported historical/product/medical/liability/price assertions remain excluded. No new speech or reactions were invented. `restored-claim-check.md` records the refreshed Harvey/Sierra source support and limits.

`review.html` includes the full episode, the exact 30-second selected opening, chapter jumps, before/after playback at all four changes, and 32 remaining omitted source intervals. `edit-manifest-v5.json` and the CSV record both original-source mapping and actual assembly references. Captions and chapters are retimed; the sub-30-second opening chapter is merged for platform compatibility.

Exact current-master checks: **{Q['loudness']['input_i']} LUFS / {Q['loudness']['input_tp']} dBTP**; coded H.264/MP4/color, all decoded frames, timestamps, full A/V decode and loudness pass. Source/picture waveform samples pass. SHA-256: `{Q['sha256']}`. Details: `qc/summary.json`, `qc/main-v5-report.json`, `qc/source-comparison.json` and `qc/pictures/`.

Status: **complete proposed feedback revision; chosen hook incorporated; exact-version host listening and full-episode approval pending**. Caption wording/names remain drafts requiring auditory proof. Original camera lip sync and continuous perceived pacing/balance are not established by sampled source alignment. Earlier full cuts, comparisons and all raw/saved source files are preserved. No external delivery, publication or deletion occurred.
'''
    readme=readme.replace('`agents-feedback-cut-v5.mp4`','`'+M['output_file']+'`').replace('`qc/main-v5-report.json`','`qc/main-v5-audio-matched-report.json`').replace('`qc/source-comparison.json`','`qc/audio-matched-source-comparison.json`')
    readme+='\nThe restored raw passages are gain-matched to the surrounding finished dialogue, with a latency-compensated peak limiter. `qc/matched-dialogue-levels.json` verifies restored speech against matching v4 windows (within 2dB). The final audio-matched export reuses byte-identical H.264 video; the 87-picture review is preserved and verified by the elementary-stream hash in `qc/video-identity-audio-match.json`. The initial v5 working export remains preserved. The current 30-second selected preview is extracted directly from the final master.\n'
    (D/'README.md').write_text(readme);(D/'HANDOFF.md').write_text(readme)
    print('Review and handoff ready',flush=True)

if __name__=='__main__':
    if '--pictures' in sys.argv:pictures()
    else:finish()
