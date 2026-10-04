from pathlib import Path
import os,json,subprocess,re,textwrap
from PIL import Image,ImageDraw,ImageFont
os.environ['PATH']='/opt/homebrew/bin:'+os.environ.get('PATH','')
L=Path(__file__).resolve().parent;ROOT=Path('/Users/je/oood');R=L.parents[1]/'codex-review-2026-10-02'
CAM=Path('/Users/je/Movies/2026-10-02 14-21-33.mp4');SCREEN=next(Path(s['path']) for s in json.loads((R/'source-review/screens-inventory.json').read_text()) if '2.21.28' in s['path'])
FONT=ROOT/'03_ASSETS/brand-fonts/teachers.ttf';START=280.6;END=319.9333333333;DUR=END-START;OFFSET=4.3703
P={'foam':'#FDF8F2','cream':'#FBF1E5','navy':'#0B2A45','blue':'#38B6FF','tint':'#A9DCFF'}
options=[
 {'id':'a-balanced','name':'A. Balanced split','description':'Larger host reactions, a focused screen crop, and a readable teaching card in the side column.','screen_box':[40,118,1160,854],'screen_crop':[460,125,1140,850],'camera_box':[1240,118,640,360],'card_box':[1240,514,640,458],'heading_size':51,'body_size':41},
 {'id':'b-screen-first','name':'B. Screen first','description':'More room for the demo, smaller hosts, and a compact teaching note in the side rail.','screen_box':[40,118,1424,922],'screen_crop':[460,125,1140,850],'camera_box':[1512,118,368,207],'card_box':[1512,361,368,679],'heading_size':36,'body_size':32},
 {'id':'c-wide-demo','name':'C. Wide demo + bottom strip','description':'A wider view of the app above, with hosts and the teaching note together in a separate bottom strip.','screen_box':[40,96,1840,720],'screen_crop':[240,150,1640,850],'camera_box':[40,840,384,216],'card_box':[472,840,1408,216],'heading_size':45,'body_size':37}
]
copy={'label':'ONE THING TO TRY','heading':'CHECK THE\nBORING BITS','body':'An impressive first draft can still get the basics wrong.','action':'Check dates, ordering, and whose plan you are seeing.'}
config={'status':'Three proposals; no standard selected','fps':30,'width':1920,'height':1080,'camera':str(CAM),'screen':str(SCREEN),'camera_in':START,'camera_out':END,'screen_offset':OFFSET,'copy':copy,'options':options,'font':str(FONT),'colors':P,'notes':'No text overlays the hosts or screen evidence. No intro/outro in these format-only comparisons.'}
(L/'layout-options.json').write_text(json.dumps(config,indent=2)+'\n')
def font(sz,weight=600):
 f=ImageFont.truetype(str(FONT),sz);f.set_variation_by_axes([weight]);return f
def wrapped(draw,txt,f,maxwidth):
 lines=[]
 for paragraph in txt.split('\n'):
  line=''
  for word in paragraph.split():
   nxt=(line+' '+word).strip()
   if draw.textlength(nxt,font=f)>maxwidth and line:lines.append(line);line=word
   else:line=nxt
  lines.append(line)
 return lines
def write(draw,x,y,txt,sz,w,width,col,spacing=1.14):
 f=font(sz,w)
 for line in wrapped(draw,txt,f,width):draw.text((x,y),line,font=f,fill=col);y+=sz*spacing
 return y
for o in options:
 im=Image.new('RGB',(1920,1080),P['foam']);d=ImageDraw.Draw(im)
 # Native two-line lockup; clear space around the small tile.
 d.rectangle((40,20,104,84),fill=P['blue']);d.text((47,32),'OUT OF OUR',font=font(9,800),fill=P['cream']);d.text((47,43),'DEPTH',font=font(19,800),fill=P['cream'])
 d.text((128,30),'CHECK THE FIRST DRAFT',font=font(41,800),fill=P['navy'])
 x,y,w,h=o['card_box'];d.rectangle((x,y,x+w,y+h),fill=P['cream']);d.rectangle((x,y+round(h*.59),x+w,y+h),fill=P['foam']);d.rectangle((x,y,x+6,y+h),fill=P['blue'])
 pad=28 if o['id']!='b-screen-first' else 23;tx=x+pad;ty=y+23
 if o['id']=='c-wide-demo':
  write(d,tx,ty,copy['label'],23,600,350,P['small_blue'] if 'small_blue' in P else '#0E6FC0')
  write(d,tx,ty+37,'CHECK THE BORING BITS',45,800,530,P['navy'])
  write(d,x+610,ty,copy['body'],37,600,w-650,P['navy'])
  write(d,x+610,ty+91,copy['action'],35,600,w-650,P['navy'])
 else:
  ty=write(d,tx,ty,copy['label'],23 if w>400 else 21,600,w-pad*2,'#0E6FC0')+23
  ty=write(d,tx,ty,copy['heading'],o['heading_size'],800,w-pad*2,P['navy'],.98)+29
  ty=write(d,tx,ty,copy['body'],o['body_size'],600,w-pad*2,P['navy'])+25
  write(d,tx,ty,copy['action'],o['body_size'],600,w-pad*2,P['navy'])
 bg=L/f'{o["id"]}-background.png';im.save(bg)
 # Still mockup from the exact same recorded moment, before expensive preview rendering.
 still=im.copy();scr=Image.open(L/'screen-fast.png').resize((1920,1080));cam=Image.open(L/'camera-fast.png')
 for typ,src in [('screen',scr),('camera',cam)]:
  if typ=='screen':cx,cy,cw,ch=o['screen_crop'];src=src.crop((cx,cy,cx+cw,cy+ch))
  bx,by,bw,bh=o[f'{typ}_box'];ratio=min(bw/src.width,bh/src.height);src=src.resize((round(src.width*ratio),round(src.height*ratio)),Image.Resampling.LANCZOS);still.paste(src,(bx+(bw-src.width)//2,by+(bh-src.height)//2))
 still.save(L/f'{o["id"]}-still.png')
# Prepare one identical pitch/timing-preserved dialogue mix for all variants.
audio=L/'comparison-dialogue.wav'
cmd=['ffmpeg','-nostdin','-n','-hide_banner','-threads','2','-ss',str(START),'-i',str(CAM),'-t',str(DUR),'-map','0:a:0','-af','loudnorm=I=-16:TP=-2:LRA=11:print_format=json','-f','null','-']
p=subprocess.run(cmd,capture_output=True,text=True,check=True);(L/'audio-level-pass1.log').write_text(p.stderr);st=json.loads(re.findall(r'\{[^{}]+\}',p.stderr)[-1])
af=f"loudnorm=I=-16:TP=-2:LRA=11:measured_I={st['input_i']}:measured_TP={st['input_tp']}:measured_LRA={st['input_lra']}:measured_thresh={st['input_thresh']}:offset={st['target_offset']}:linear=true,aresample=48000,apad=whole_dur={DUR},atrim=duration={DUR},asetpts=N/SR/TB,afade=t=in:d=0.005,afade=t=out:st={DUR-.01}:d=0.01"
subprocess.run(['ffmpeg','-v','error','-nostdin','-n','-threads','2','-ss',str(START),'-i',str(CAM),'-t',str(DUR),'-map','0:a:0','-af',af,'-ac','2','-ar','48000','-c:a','pcm_s16le',str(audio)],check=True)
for o in options:
 dst=L/f'{o["id"]}.mp4';x,y,w,h=o['screen_crop'];sx,sy,sw,sh=o['screen_box'];cx,cy,cw,ch=o['camera_box']
 filters=f'[0:v]fps=30,format=yuv420p[bg];[1:v]setpts=PTS-STARTPTS,fps=30,crop={w}:{h}:{x}:{y},scale={sw}:{sh}:force_original_aspect_ratio=decrease,pad={sw}:{sh}:(ow-iw)/2:(oh-ih)/2:color=0xFDF8F2,setsar=1[screen];[2:v]setpts=PTS-STARTPTS,fps=30,scale={cw}:{ch},setsar=1[hosts];[bg][screen]overlay={sx}:{sy}[demo];[demo][hosts]overlay={cx}:{cy},trim=duration={DUR},setpts=N/(30*TB),setsar=1,setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709[v]'
 cmd=['ffmpeg','-nostdin','-n','-hide_banner','-threads','2','-loop','1','-framerate','30','-i',str(L/f'{o["id"]}-background.png'),'-threads','2','-ss',str(START+OFFSET),'-i',str(SCREEN),'-threads','2','-ss',str(START),'-i',str(CAM),'-i',str(audio),'-filter_complex_threads','2','-filter_complex',filters,'-map','[v]','-map','3:a:0','-t',str(DUR),'-c:v','libx264','-preset','veryfast','-crf','19','-threads','4','-pix_fmt','yuv420p','-bf','0','-g','30','-sc_threshold','0','-color_range','tv','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-c:a','aac','-b:a','256k','-ar','48000','-bsf:a','noise=drop=lt(pts\\,0)','-use_editlist','0','-movflags','+faststart',str(dst)]
 print('RENDER',o['name'],flush=True)
 with (L/f'{o["id"]}-render.log').open('w') as log:subprocess.run(cmd,stdout=log,stderr=log,check=True)
 print('FINISHED',dst.name,flush=True)
