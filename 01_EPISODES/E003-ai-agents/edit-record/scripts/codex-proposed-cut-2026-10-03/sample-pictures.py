from pathlib import Path
import json,subprocess,sys,concurrent.futures
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent;M=json.loads((R/'edit-manifest-v4.json').read_text());mode='hooks' if '--hooks' in sys.argv else 'main-v4'
D=R/'qc'/f'picture-review-{mode}';D.mkdir(exist_ok=False)
items=[]
if mode=='hooks':
 for h in M['hooks']:
  for i,s in enumerate(h['segments']):
   for label,t in [('start',s['timeline_in']+.15),('end',s['timeline_out']-.15)]:items.append((h['id']+f'-{i}-{label}',R/h['file'],t))
else:
 for s in M['segments']:
  for label,t in [('start',s['timeline_in']+.1),('end',s['timeline_out']-.1)]:items.append((s['id']+'-'+label,R/M['output_file'],t))
def snap(item):
 name,path,t=item;dst=D/(name+'.jpg')
 subprocess.run(['ffmpeg','-nostdin','-v','error','-ss',str(t),'-threads','1','-i',str(path),'-frames:v','1','-vf','scale=480:270','-n',str(dst)],check=True,capture_output=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(snap,items))
for start in range(0,len(items),16):
 group=items[start:start+16];im=Image.new('RGB',(1920,4*296),'#0b2842');draw=ImageDraw.Draw(im)
 for i,(name,path,t) in enumerate(group):
  x=i%4*480;y=i//4*296;im.paste(Image.open(D/(name+'.jpg')),(x,y));draw.text((x+7,y+274),f'{name} | {t:.3f}s',fill='white')
 im.save(D/f'board-{start//16+1:02}.jpg')
(D/'sample-map.json').write_text(json.dumps([{'name':a,'file':str(b),'time':c} for a,b,c in items],indent=2))
print(mode,'sampled',len(items),'frames')
