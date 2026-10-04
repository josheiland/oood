from pathlib import Path
import json, html, re, subprocess, concurrent.futures
from PIL import Image, ImageDraw

R=Path(__file__).resolve().parent;D=R/'hook-transition-previews-v2'
P=json.loads((D/'preview-manifest.json').read_text())

def pictures():
    out=D/'qc/pictures';out.mkdir(exist_ok=False)
    items=[]
    for h in P['hooks']:
        for i,s in enumerate(h['segments']):
            for label,t in [('start',s['timeline_in']+.1),('end',s['timeline_out']-.1)]:
                items.append((h['id']+f'-{i}-{label}',D/h['file'],t))
    def snap(item):
        name,path,t=item
        subprocess.run(['ffmpeg','-nostdin','-v','error','-ss',str(t),'-threads','1','-i',str(path),
            '-frames:v','1','-vf','scale=480:270','-n',str(out/(name+'.jpg'))],check=True,capture_output=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(snap,items))
    for start in range(0,len(items),16):
        im=Image.new('RGB',(1920,1184),'#0b2842');draw=ImageDraw.Draw(im)
        for i,(name,path,t) in enumerate(items[start:start+16]):
            x=i%4*480;y=i//4*296;im.paste(Image.open(out/(name+'.jpg')),(x,y))
            draw.text((x+7,y+274),f'{name} | {t:.3f}s',fill='white')
        im.save(out/f'board-{start//16+1:02}.jpg')
    (out/'sample-map.json').write_text(json.dumps([dict(name=a,file=str(b),time=c) for a,b,c in items],indent=2)+'\n')
    print('Sampled',len(items),'pictures',flush=True)

def pages():
    assert json.loads((D/'qc/summary.json').read_text())['passed']
    for ext in ['srt','vtt']:
        path=D/('06-agent-gender-transition-v2.'+ext)
        text=path.read_text().replace('muses a he for sure.','Muse is a he for sure.').replace('how instinct works','how Instinct works')
        path.write_text(text)
    tiles=[]
    for h in P['hooks']:
        f=h['file'];v=Path(f).with_suffix('.vtt').name;t=html.escape(h['title']);ident=h['id']
        tiles.append(f'''<article><h2>{t}</h2><p>{h['hook_duration']:.1f}s hook → 5.3s intro/song → {h['opening_duration']:.1f}s episode opening</p>
<video id="{ident}" controls preload="metadata" src="{f}"><track kind="captions" src="{v}" srclang="en" label="English draft"></video>
<div class="links"><button onclick="jump('{ident}',{h['hook_duration']})">Intro transition</button><button onclick="jump('{ident}',{h['hook_duration']+h['card_duration']})">Episode transition</button><a href="{f}" download>Download preview</a></div></article>''')
    text='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>OOOD · Agents opening options</title>
<style>@font-face{font-family:Teachers;src:url('../teachers.ttf')}*{box-sizing:border-box}body{margin:0;background:#f3e8dd;color:#0b2842;font:18px/1.5 Teachers,system-ui,sans-serif}header{background:#3daff4;padding:28px max(20px,calc((100vw - 1200px)/2))}h1{line-height:1.15;font-size:42px;margin:8px 0}main{max-width:1200px;margin:auto;padding:24px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:24px}article{background:#fff7ef;padding:20px;border-radius:10px}h2{font-size:24px;margin:0 0 10px}article p{font-size:16px}video{display:block;width:100%;background:#0b2842;border-radius:8px}.links{display:flex;gap:12px;align-items:center;flex-wrap:wrap;margin:12px 0}a{color:#0b2842;font-weight:bold}button{font:inherit;font-size:15px;border:1px solid #0b2842;color:#0b2842;background:transparent;padding:8px;border-radius:6px;cursor:pointer}footer{font-size:15px;margin:24px 0}@media(max-width:720px){.grid{grid-template-columns:1fr}main{padding:16px}h1{font-size:32px}}</style>
<header><div>OUT OF OUR DEPTH · AGENTS · OPENING OPTIONS v2</div><h1>Eight hooks, with the full transition</h1><p>About 10 seconds of hook, the intro card and song, then the same episode opening. Each preview is exactly 30 seconds.</p></header>
<main><p>Start with <b>Too many tools</b>, <b>Baby</b> and <b>Big Egg</b> for the strongest comic options. Play each to compare the handoff into the episode.</p><p><a href="../review.html">Full episode and edit review</a></p><div class="grid">'''+''.join(tiles)+'''</div><footer>All eight exports pass frame, color, timing, decode, loudness and sampled source-alignment checks. Captions remain editable drafts. The 37:13.667 full cut is unchanged and still contains its earlier provisional Big Egg cold open; the chosen compact hook can replace that at final lock. Earlier previews are preserved. Host choice and continuous listening remain pending.</footer></main>
<script>const vids=[...document.querySelectorAll('video')];vids.forEach(v=>v.addEventListener('play',()=>vids.forEach(o=>{if(o!==v)o.pause()})));function jump(id,t){const v=document.getElementById(id);v.currentTime=Math.max(0,t-1.5);v.play().catch(()=>{})}</script></html>'''
    assert not (D/'review.html').exists();(D/'review.html').write_text(text)
    old=R/'review.html';archive=R/'review-hook-only-v1.html';assert not archive.exists();archive.write_text(old.read_text())
    page=old.read_text()
    page=page.replace('Eight 30-second hook previews.','Eight 30-second opening previews: ~10-second hooks, intro/song, then the episode opening.')
    page=page.replace('<h2>Choose the hook</h2>','<h2>Choose the hook</h2><p><a href="hook-transition-previews-v2/review.html">Open the revised transition comparisons</a> — compact hook, intro/song, same episode opening; 30 seconds each.</p>')
    for h in P['hooks']:
        for ext in ['mp4','vtt','srt']:
            page=page.replace('hooks/'+h['id']+'.'+ext,'hook-transition-previews-v2/'+h['id']+'-transition-v2.'+ext)
    page=page.replace('Every preview is exactly 30 seconds and ends after its card/music tail.','Every preview is exactly 30 seconds: a compact hook, the intro card/song, and the same episode opening.')
    page=page.replace('Each file stops after its card/music tail; it does not continue into the full episode.','Each revised preview plays a compact hook, the recurring intro card/song, and the same beginning of the episode.')
    page=page.replace('1. Big Egg and the egg police','1. Big Egg / too many eggs')
    page=page.replace('the harsh-critic response and a real qualification','tool overload and a real qualification')
    old.write_text(page)
    rows=['# Agents — compact hook transition comparisons v2','',
        'Eight exactly 30-second previews: approximately 10 seconds of authentic hook, the full 5.267-second recurring intro card/song, and the same beginning of the episode body (source 01:04, v4 output 00:30).','',
        'Open `review.html` for side-by-side playback, transition jumps and downloads. Each MP4 has adjacent draft SRT/VTT captions. `preview-manifest.json` records every source and output frame.','',
        'The full 37:13.667 v4 episode is unchanged and retains its earlier provisional longer Big Egg hook pending selection. Earlier hook-only comparisons and all raw footage are preserved.','',
        'Each export is 900 frames, 1080p30; coded color/MP4, packet timing, full decode and loudness checks pass. Every retained camera excerpt has sampled waveform/picture correspondence. See `qc/summary.json` and `qc/source-comparison.json`. Sampled transition pictures are in `qc/pictures/`. Host listening, captions and final selection remain pending.','',
        '| Option | Hook | Intro/song | Episode opening |','|---|---:|---:|---:|']
    for h in P['hooks']:rows.append(f'| {h["title"]} | {h["hook_duration"]:.3f}s | {h["card_duration"]:.3f}s | {h["opening_duration"]:.3f}s |')
    (D/'README.md').write_text('\n'.join(rows)+'\n')
    for filename in ['README.md','HANDOFF.md']:
        p=R/filename;text=p.read_text()
        text=re.sub(r'Eight hook-only (?:previews|comparisons) are \*\*30\.000 seconds each\*\*, including their recurring card/music tail\.|Eight hook-only comparisons are exactly 30 seconds each, including their card/music tail\.',
            'Current comparisons: `hook-transition-previews-v2/review.html` — eight exactly 30-second previews, with 8–12-second hooks, the 5.267-second intro card/song, and the same episode opening. Earlier hook-only previews are preserved.',text)
        text=text.replace('Each preview ends after the card; it does not append the full episode.','Each revised preview continues through the card/song into the same episode opening. The full master retains its earlier provisional longer hook pending selection.')
        p.write_text(text)
    print('Review pages and handoff updated',flush=True)

if __name__=='__main__':
    import sys
    if '--pictures' in sys.argv:pictures()
    else:pages()
