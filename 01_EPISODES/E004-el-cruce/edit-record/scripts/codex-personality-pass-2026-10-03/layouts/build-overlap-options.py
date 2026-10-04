from pathlib import Path
import os,json,subprocess
from PIL import Image
os.environ['PATH']='/opt/homebrew/bin:'+os.environ.get('PATH','')
L=Path(__file__).resolve().parent;N=L/'overlap-window-options';N.mkdir(exist_ok=False);(N/'qc').mkdir();old=json.loads((L/'no-cards-5-options/layout-manifest.json').read_text());dur=old['duration']
opts=[
 {'id':'a-light-overlap','name':'A. Light overlap','description':'Large inset screen with a 640-pixel host window; about 6% screen overlap.','screen_box':[40,40,1600,829],'screen_crop':[240,150,1640,850],'camera_box':[1240,670,640,360]},
 {'id':'b-balanced-overlap','name':'B. Balanced overlap','description':'Inset screen and a larger 720-pixel host window; about 8% screen overlap.','screen_box':[40,40,1544,800],'screen_crop':[240,150,1640,850],'camera_box':[1160,610,720,405]},
 {'id':'c-larger-hosts','name':'C. Largest host window','description':'More room for your reactions, with an 800-pixel host window; about 8% screen overlap.','screen_box':[40,40,1440,746],'screen_crop':[240,150,1640,850],'camera_box':[1080,590,800,450]}
]
for o in opts:
 s=o['screen_box'];c=o['camera_box'];outer=[c[0]-6,c[1]-6,c[2]+12,c[3]+12];ow=max(0,min(s[0]+s[2],outer[0]+outer[2])-max(s[0],outer[0]));oh=max(0,min(s[1]+s[3],outer[1]+outer[3])-max(s[1],outer[1]));o['covered_screen_fraction_including_border']=ow*oh/(s[2]*s[3]);o['host_width_vs_old_option_4']=c[2]/472
m={k:old[k] for k in ['fps','width','height','camera','screen','camera_in','camera_out','screen_offset','audio_source']};m.update(status='Three inset-screen/larger-host overlap proposals; exact standard not selected',duration=dur,options=opts,background_color='#FDF8F2',host_border_px=6,no_added_text_or_logo=True)
(N/'layout-manifest.json').write_text(json.dumps(m,indent=2)+'\n');bg=N/'plain-background.png';Image.new('RGB',(1920,1080),'#FDF8F2').save(bg)
for o in opts:
 sx,sy,sw,sh=o['screen_box'];cx,cy,cw,ch=o['camera_box'];x,y,w,h=o['screen_crop'];dst=N/f'{o["id"]}.mp4'
 vf=f'[0:v]fps=30,format=yuv420p[bg];[1:v]setpts=PTS-STARTPTS,fps=30,crop={w}:{h}:{x}:{y},scale={sw}:{sh}:force_original_aspect_ratio=decrease,pad={sw}:{sh}:(ow-iw)/2:(oh-ih)/2:color=0xFDF8F2,setsar=1[screen];[2:v]setpts=PTS-STARTPTS,fps=30,scale={cw}:{ch},pad=iw+12:ih+12:6:6:color=0xFDF8F2,setsar=1[hosts];[bg][screen]overlay={sx}:{sy}[demo];[demo][hosts]overlay={cx-6}:{cy-6},trim=duration={dur},setpts=N/(30*TB),setsar=1,setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709[v]'
 cmd=['ffmpeg','-nostdin','-n','-hide_banner','-threads','2','-loop','1','-framerate','30','-i',str(bg),'-threads','2','-ss',str(m['camera_in']+m['screen_offset']),'-i',m['screen'],'-threads','2','-ss',str(m['camera_in']),'-i',m['camera'],'-i',m['audio_source'],'-filter_complex_threads','2','-filter_complex',vf,'-map','[v]','-map','3:a:0','-t',str(dur),'-c:v','libx264','-preset','veryfast','-crf','19','-threads','4','-pix_fmt','yuv420p','-bf','0','-g','30','-sc_threshold','0','-color_range','tv','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-c:a','copy','-use_editlist','0','-movflags','+faststart',str(dst)]
 print('RENDER',o['name'],flush=True)
 with (N/f'{o["id"]}-render.log').open('w') as log:subprocess.run(cmd,stdout=log,stderr=log,check=True)
 for t,suf in [(0,'start'),(6.4,'still'),(38.9,'end')]:subprocess.run(['ffmpeg','-v','error','-nostdin','-n','-threads','2','-ss',str(t),'-i',str(dst),'-frames:v','1','-threads','2',str(N/f'{o["id"]}-{suf}.png')],check=True)
 print('FINISHED',dst.name,flush=True)
