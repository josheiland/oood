from pathlib import Path
import json,os,subprocess
from PIL import Image,ImageDraw,ImageFont
Q=Path(__file__).resolve().parent;M=json.loads((Q/'edit-manifest-v8-final.json').read_text());MASTER=Q/M['output_file'];W=Q/'picture-review-v8';W.mkdir(exist_ok=False)
font=ImageFont.truetype(str(Q/'teachers.ttf'),20)
def frame(t,name):
    out=W/f'{name}.jpg'
    subprocess.run(['/opt/homebrew/bin/ffmpeg','-nostdin','-v','error','-threads','2','-ss',str(max(0,t)),'-i',str(MASTER),'-frames:v','1','-vf','scale=640:360','-filter_threads','2','-q:v','3','-threads','2',str(out)],check=True)
    return out
def board(items,path):
    im=Image.new('RGB',(1280,414*len(items)//2),'#FDF8F2');d=ImageDraw.Draw(im)
    for i,(p,label) in enumerate(items):
        x=(i%2)*640;y=(i//2)*414;im.paste(Image.open(p),(x,y));d.text((x+8,y+366),label,font=font,fill='#0B2A45')
    im.save(path,quality=88)
allitems=[]
for i,s in enumerate(M['segments'][1:],1):
    t=s['timeline_in'];items=[]
    for name,at in [('before',t-1/30),('after',t)]:
        p=frame(at,f'join-{i:02}-{name}');items.append((p,f'{i:02} {name} · {at:.3f}s · {s["id"]}'))
    allitems+=items
    if len(allitems)==16:
        dest=W/f'joins-{(i-1)//8+1:02}.jpg';board(allitems,dest);print(dest,flush=True);allitems=[]
if allitems:board(allitems,W/'joins-final.jpg')
screens=[]
for s in M['segments']:
    if s.get('screen'):
        t=(s['timeline_in']+s['timeline_out'])/2;p=frame(t,f'{s["id"]}-mid');screens.append((p,f'{s["id"]} · {int(t)//60:02}:{int(t)%60:02} · screen C'))
for i in range(0,len(screens),8):
    items=screens[i:i+8]
    if len(items)%2:items.append((items[-1][0],'Same frame'))
    board(items,W/f'screens-{i//8+1:02}.jpg')
for name,t in [('hook',3),('intro',10),('covered-opening',M['segments'][2]['timeline_in']),('covered-ending',M['segments'][-2]['timeline_out']-1/30),('outro',M['duration']-5)]:
    frame(t,name)
print('Picture samples complete',flush=True)
