#!/usr/bin/env python3
"""Reproducible review renderer. Originals read only; refuses to replace exports."""
import argparse, hashlib, json, pathlib, re, subprocess
ROOT=pathlib.Path(__file__).resolve().parent
REPO=pathlib.Path('/Users/je/oood')
FPS=30
COLOR=['-color_range','tv','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709']
VENC=['-c:v','libx264','-preset','veryfast','-crf','19','-threads','4','-pix_fmt','yuv420p','-bf','0','-g','30','-sc_threshold','0',*COLOR]

def run(args,log):
 with open(log,'w') as f:
  p=subprocess.run(['ffmpeg','-nostdin','-n','-hide_banner',*map(str,args)],stdout=f,stderr=f)
 if p.returncode: raise RuntimeError(f'ffmpeg failed: {log}')

def render_segment(s,folder):
 key=hashlib.sha256(json.dumps(s,sort_keys=True).encode()).hexdigest()[:16]
 dst=folder/f'{key}.mov'
 done=folder/f'{key}.done'
 if dst.exists():
  if done.exists():return dst
  raise RuntimeError(f'Incomplete cached segment: {dst}')
 dur=round((s['out']-s['in'])*FPS)/FPS
 args=['-ss',s['in'],'-i',s['source']]
 filters=[]
 if s.get('still'):
  args=['-loop','1','-framerate','30','-i',s['still'],'-i',s['source']]
  filters += ['[0:v]scale=1920:1080,setsar=1,format=yuv420p[v0]']
  aud='1:a:0'
 elif s.get('screen'):
  args += ['-ss',s['in']+s['screen_offset'],'-i',s['screen'],'-loop','1','-framerate','30','-i',str(ROOT/s['layout'])]
  x,y,w,h=s['crop']
  filters += [f'[1:v]setpts=PTS-STARTPTS,fps=30,crop={w}:{h}:{x}:{y},scale=1184:1000:force_original_aspect_ratio=decrease,pad=1184:1000:(ow-iw)/2:(oh-ih)/2:color=0x0B2A45[screen]', '[0:v]setpts=PTS-STARTPTS,fps=30,scale=640:360[hosts]', '[2:v]format=yuv420p[bg]', '[bg][screen]overlay=24:40[bgs]', '[bgs][hosts]overlay=1256:40:shortest=1[v0]']
  aud='0:a:0'
 else:
  filters += ['[0:v]setpts=PTS-STARTPTS,fps=30,scale=1920:1080,setsar=1,format=yuv420p[v0]']
  aud='0:a:0'
 if s.get('popup'):
  idx=1 if not s.get('screen') else 3
  args += ['-loop','1','-framerate','30','-i',str(ROOT/s['popup'])]
  filters += [f'[v0][{idx}:v]overlay=0:0:enable=\'between(t,{s.get("popup_in",1)},{s.get("popup_out",8)})\'[vp]']
  vin='vp'
 else: vin='v0'
 filters += [f'[{vin}]trim=duration={dur},setpts=N/(30*TB),setsar=1,setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709[v]',f'[{aud}]atrim=duration={dur},asetpts=PTS-STARTPTS,aresample=48000,apad=whole_dur={dur},atrim=duration={dur},afade=t=in:d=0.005,afade=t=out:st={max(0,dur-.01)}:d=0.01,volume={s.get("gain_db",0)}dB[a]']
 args += ['-filter_complex_threads','2','-filter_complex',';'.join(filters),'-map','[v]','-map','[a]',*VENC,'-c:a','pcm_s16le','-ac','2','-ar','48000','-t',dur,dst]
 run(args,folder/f'{key}.log');done.write_text(json.dumps(s,indent=2));return dst

def stats(path):
 return json.loads(re.findall(r'\{[^{}]+\}',path.read_text())[-1])

def render(segments,dst,work,chapters=None):
 if dst.exists():raise FileExistsError(dst)
 work.mkdir(parents=True,exist_ok=True)
 cache=ROOT/'intermediate';cache.mkdir(exist_ok=True)
 clips=[];total=0
 for i,s in enumerate(segments):
  print(f'{dst.name}: segment {i+1}/{len(segments)}',flush=True)
  clips.append(render_segment(s,cache));total+=round((s['out']-s['in'])*FPS)
 concat=work/'concat.txt';concat.write_text(''.join(f"file '{p}'\n" for p in clips))
 ci=['-f','concat','-safe','0','-i',concat]
 duration=total/FPS
 run([*ci,'-vn','-af','loudnorm=I=-15.5:TP=-3:LRA=11:print_format=json','-f','null','-'],work/'loudness-pass1.log')
 st=stats(work/'loudness-pass1.log');(work/'loudness-pass1.json').write_text(json.dumps(st,indent=2))
 af=f"loudnorm=I=-15.5:TP=-3:LRA=11:measured_I={st['input_i']}:measured_TP={st['input_tp']}:measured_LRA={st['input_lra']}:measured_thresh={st['input_thresh']}:offset={st['target_offset']}:linear=true,aresample=48000,apad=whole_dur={duration},atrim=duration={duration},asetpts=N/SR/TB"
 meta=work/'chapters.ffmeta'
 lines=[';FFMETADATA1','title=Out of Our Depth | El Cruce | Proposed review','comment=Proposed edit; host approval pending']
 for i,c in enumerate(chapters or []):
  end=chapters[i+1]['time'] if i+1<len(chapters) else duration
  lines+=['[CHAPTER]','TIMEBASE=1/1000',f'START={round(c["time"]*1000)}',f'END={round(end*1000)}',f'title={c["title"]}']
 meta.write_text('\n'.join(lines)+'\n')
 run([*ci,'-i',meta,'-map','0:v:0','-map','0:a:0','-map_metadata','1','-map_chapters','1','-vf','setpts=N/(30*TB),setsar=1,format=yuv420p,setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709','-af',af,*VENC,'-r','30','-fps_mode','cfr','-c:a','aac','-b:a','256k','-ar','48000','-bsf:a','noise=drop=lt(pts\,0)','-use_editlist','0','-movflags','+faststart',dst],work/'final-render.log')
 (work/'render-manifest.json').write_text(json.dumps({'file':str(dst),'expected_frames':total,'expected_duration':duration,'segments':segments},indent=2))
 print(f'FINISHED {dst}',flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('manifest');p.add_argument('--hooks',action='store_true');p.add_argument('--full',action='store_true');a=p.parse_args()
 m=json.loads(pathlib.Path(a.manifest).read_text())
 if a.full:render(m['segments'],ROOT/m.get('output_file','el-cruce-proposed-cut-v1.mp4'),ROOT/'qc-work'/m.get('work_folder','full'),m['chapters'])
 if a.hooks:
  (ROOT/'hooks').mkdir(exist_ok=True)
  for h in m['hooks']:render(h['segments'],ROOT/'hooks'/h['file'],ROOT/'qc-work'/h['file'].removesuffix('.mp4'))
