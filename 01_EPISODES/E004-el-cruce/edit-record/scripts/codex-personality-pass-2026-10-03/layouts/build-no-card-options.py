from pathlib import Path
import os,json,subprocess
from PIL import Image
os.environ['PATH']='/opt/homebrew/bin:'+os.environ.get('PATH','')
L=Path(__file__).resolve().parent;N=L/'no-cards-5-options';N.mkdir(exist_ok=False);(N/'qc').mkdir();m=json.loads((L/'layout-options-current.json').read_text());dur=round((m['camera_out']-m['camera_in'])*30)/30
opts=[
 {'id':'01-balanced','name':'1. Balanced side by side','description':'Focused screen on the left, medium-size hosts on the right.','screen_box':[24,24,1248,1032],'screen_crop':[460,125,1140,850],'camera_box':[1296,371,600,338]},
 {'id':'02-equal-split','name':'2. Equal split, hosts left','description':'Largest host view, with the demo on the right.','screen_box':[976,24,920,1032],'screen_crop':[460,125,1140,850],'camera_box':[24,279,928,522]},
 {'id':'03-screen-first','name':'3. Screen first','description':'Large focused demo and a small host view at the right.','screen_box':[24,24,1464,1032],'screen_crop':[460,125,1140,850],'camera_box':[1512,432,384,216]},
 {'id':'04-corner-hosts','name':'4. Full screen with corner hosts','description':'Wide demo with hosts floating at the lower right; may cover some interface content.','screen_box':[0,0,1920,1080],'screen_crop':[240,150,1640,850],'camera_box':[1424,790,472,266]},
 {'id':'05-stacked','name':'5. Screen above, hosts below','description':'Wide app view above the hosts; more browser context, smaller on-screen text.','screen_box':[24,24,1872,726],'screen_crop':[0,0,1920,1080],'camera_box':[688,774,544,306]}
]
m2={k:m[k] for k in ['fps','width','height','camera','screen','camera_in','camera_out','screen_offset']};m2.update(status='Five proposals with no text, teaching cards or logo overlays; no standard selected',duration=dur,options=opts,audio_source=str(L/'a-balanced-v2.mp4'),background_color='#FDF8F2')
(N/'layout-manifest.json').write_text(json.dumps(m2,indent=2)+'\n');bg=N/'plain-background.png';Image.new('RGB',(1920,1080),'#FDF8F2').save(bg)
for o in opts:
 sx,sy,sw,sh=o['screen_box'];cx,cy,cw,ch=o['camera_box'];x,y,w,h=o['screen_crop'];dst=N/f'{o["id"]}.mp4'
 vf=f'[0:v]fps=30,format=yuv420p[bg];[1:v]setpts=PTS-STARTPTS,fps=30,crop={w}:{h}:{x}:{y},scale={sw}:{sh}:force_original_aspect_ratio=decrease,pad={sw}:{sh}:(ow-iw)/2:(oh-ih)/2:color=0xFDF8F2,setsar=1[screen];[2:v]setpts=PTS-STARTPTS,fps=30,scale={cw}:{ch},setsar=1[hosts];[bg][screen]overlay={sx}:{sy}[demo];[demo][hosts]overlay={cx}:{cy},trim=duration={dur},setpts=N/(30*TB),setsar=1,setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709[v]'
 cmd=['ffmpeg','-nostdin','-n','-hide_banner','-threads','2','-loop','1','-framerate','30','-i',str(bg),'-threads','2','-ss',str(m['camera_in']+m['screen_offset']),'-i',m['screen'],'-threads','2','-ss',str(m['camera_in']),'-i',m['camera'],'-i',str(L/'a-balanced-v2.mp4'),'-filter_complex_threads','2','-filter_complex',vf,'-map','[v]','-map','3:a:0','-t',str(dur),'-c:v','libx264','-preset','veryfast','-crf','19','-threads','4','-pix_fmt','yuv420p','-bf','0','-g','30','-sc_threshold','0','-color_range','tv','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-c:a','copy','-use_editlist','0','-movflags','+faststart',str(dst)]
 print('RENDER',o['name'],flush=True)
 with (N/f'{o["id"]}-render.log').open('w') as log:subprocess.run(cmd,stdout=log,stderr=log,check=True)
 for t,suf in [(0,'start'),(6.4,'still'),(38.9,'end')]:
  subprocess.run(['ffmpeg','-v','error','-nostdin','-n','-threads','2','-ss',str(t),'-i',str(dst),'-frames:v','1','-threads','2',str(N/f'{o["id"]}-{suf}.png')],check=True)
 print('FINISHED',dst.name,flush=True)
