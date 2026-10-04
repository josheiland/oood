from pathlib import Path
import subprocess,json
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent; m=json.loads((R/'edit-manifest-v3.json').read_text());d=R/'qc/final-picture-review-v3';d.mkdir(exist_ok=True)
items=[]
for s in m['segments']:
 for label,t in [('start',s['timeline_in']+.12),('end',s['timeline_out']-.12)]:items.append((f'{s["id"]}-{label}',t))
for i,s in enumerate([s for s in m['segments'] if s.get('screen')]):items.append((f'demo-{s["id"]}',(s['timeline_in']+s['timeline_out'])/2))
for name,t in items:
 p=d/(name+'.jpg');subprocess.run(['ffmpeg','-v','error','-nostdin','-ss',str(t),'-i',str(R/'el-cruce-proposed-cut-v3.mp4'),'-frames:v','1','-vf','scale=640:360','-y',str(p)],check=True)
for start in range(0,len(items),12):
 group=items[start:start+12];im=Image.new('RGB',(1920,4*386),'#0b2a45');draw=ImageDraw.Draw(im)
 for i,(name,t) in enumerate(group):
  x=(i%3)*640;y=(i//3)*386;im.paste(Image.open(d/(name+'.jpg')),(x,y));draw.text((x+8,y+362),f'{name} | final {t:.2f}s',fill='white')
 im.save(d/f'board-{start//12+1:02}.jpg')
print('Sampled',len(items),'frames into',len(range(0,len(items),12)),'boards')
