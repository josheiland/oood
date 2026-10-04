#!/usr/bin/env python3
"""Own-lane deterministic C-layout render; read-only sources, no replacement outputs."""
from pathlib import Path
import os,json,subprocess,hashlib,re,sys
os.environ['PATH']='/opt/homebrew/bin:'+os.environ.get('PATH','')
Q=Path(__file__).resolve().parent;CACHE=Q/'intermediate';CACHE.mkdir(exist_ok=True)
ENC=['-c:v','libx264','-preset','veryfast','-crf','19','-threads','4','-pix_fmt','yuv420p','-bf','0','-g','30','-sc_threshold','0','-color_range','tv','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709']
def run(args,log):
 with Path(log).open('w') as f:
  r=subprocess.run(['ffmpeg','-nostdin','-n','-hide_banner',*map(str,args)],stdout=f,stderr=f)
 if r.returncode:raise RuntimeError(f'FFmpeg failed: {log}')
def key(s):
 fields=['source','in','out','still','gain_db','screen','screen_offset','crop','host_position','redactions','processed_audio','audio_in','audio_out','mutes']
 return hashlib.sha256(json.dumps({k:s[k] for k in fields if k in s},sort_keys=True).encode()).hexdigest()[:16]
def segment(s):
 K=key(s);dst=CACHE/f'{K}.mov';done=CACHE/f'{K}.done'
 if done.exists() and dst.exists():return dst
 if dst.exists():raise FileExistsError(f'Incomplete cache preserved: {dst}')
 dur=round((s['out']-s['in'])*30)/30;filters=[];next_idx=1
 if s.get('still'):
  args=['-threads','2','-loop','1','-framerate','30','-i',s['still'],'-threads','2','-i',s['source']];aud='1:a:0';next_idx=2
  filters.append('[0:v]scale=1920:1080,format=yuv420p,setsar=1[v0]')
 else:
  args=['-threads','2','-ss',s['in'],'-i',s['source']];aud='0:a:0'
  if s.get('screen'):
   args+=['-threads','2','-ss',s['in']+s['screen_offset'],'-i',s['screen'],'-f','lavfi','-i','color=c=0xFDF8F2:s=1920x1080:r=30'];next_idx=3
   x,y,w,h=s['crop'];cx,cy=s.get('host_position',[1080,590]);redact=''
   for bx,by,bw,bh in s.get('redactions',[]):redact+=f'drawbox=x={bx}:y={by}:w={bw}:h={bh}:color=black:t=fill,'
   filters.extend([f'[1:v]setpts=PTS-STARTPTS,fps=30,{redact}crop={w}:{h}:{x}:{y},scale=1440:746:force_original_aspect_ratio=decrease:force_divisible_by=2,pad=1440:746:(ow-iw)/2:(oh-ih)/2:color=0xFDF8F2,setsar=1[screen]', '[0:v]setpts=PTS-STARTPTS,fps=30,scale=800:450,pad=iw+12:ih+12:6:6:color=0xFDF8F2,setsar=1[hosts]', '[2:v]format=yuv420p[bg]', '[bg][screen]overlay=40:40[demo]',f'[demo][hosts]overlay={cx-6}:{cy-6}:shortest=1[v0]'])
  else:filters.append('[0:v]setpts=PTS-STARTPTS,fps=30,scale=1920:1080,format=yuv420p,setsar=1[v0]')
 if s.get('processed_audio'):
  args+=['-threads','2','-i',s['processed_audio']];aud=f'{next_idx}:a:0'
 filters.append(f'[v0]tpad=stop_mode=clone:stop_duration=0.10,trim=duration={dur},setpts=N/(30*TB),setsar=1,setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709[v]')
 af=f'atrim=duration={dur},asetpts=PTS-STARTPTS,aresample=48000,apad=whole_dur={dur},atrim=duration={dur}'
 if s.get('audio_in') is not None:
  ai=max(0,s['audio_in']-s['in']);af+=f",volume=0:enable='lt(t,{ai})'"
 if s.get('audio_out') is not None:
  ao=max(0,s['audio_out']-s['in']);af+=f",volume=0:enable='gte(t,{ao})'"
 for a,b in s.get('mutes',[]):af+=f",volume=0:enable='between(t,{a-s['in']},{b-s['in']})'"
 af+=f',volume={s.get("gain_db",0)}dB,afade=t=in:d=0.005,afade=t=out:st={max(0,dur-.01)}:d=0.01'
 filters.append(f'[{aud}]{af}[a]')
 run([*args,'-filter_complex_threads','2','-filter_complex',';'.join(filters),'-map','[v]','-map','[a]',*ENC,'-c:a','pcm_s16le','-ac','2','-ar','48000','-t',dur,dst],CACHE/f'{K}.log');done.write_text(json.dumps(s,indent=2));return dst

def full(m):
 dst=Q/m['output_file'];work=Q/'render-work';work.mkdir(exist_ok=True)
 if dst.exists():raise FileExistsError(dst)
 files=[]
 for i,s in enumerate(m['segments']):
  print(f'Segment {i+1}/{len(m["segments"])}: {s["id"]}',flush=True);files.append(segment(s))
 concat=work/'concat.txt';concat.write_text(''.join(f"file '{p}'\n" for p in files));ci=['-threads','2','-f','concat','-safe','0','-i',concat];dur=m['duration']
 balance=f"volume='if(lt(t,9.1),0.630957,if(between(t,14.3666667,{dur-10.7666667}),1.995262,1))':eval=frame"
 print('Measure audio',flush=True);run([*ci,'-vn','-af',balance+',loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-'],work/'loudness-pass1.log');st=json.loads(re.findall(r'\{[^{}]+\}',(work/'loudness-pass1.log').read_text())[-1]);(work/'loudness-pass1.json').write_text(json.dumps(st,indent=2))
 af=balance+f",loudnorm=I=-16:TP=-1.5:LRA=11:measured_I={st['input_i']}:measured_TP={st['input_tp']}:measured_LRA={st['input_lra']}:measured_thresh={st['input_thresh']}:offset={st['target_offset']}:linear=true,aresample=48000,apad=whole_dur={dur},atrim=duration={dur},asetpts=N/SR/TB"
 meta=work/'chapters.ffmeta';lines=[';FFMETADATA1','title=Out of Our Depth | El Cruce | Personality pass','comment=Host review proposal; C layout selected']
 for i,c in enumerate(m['chapters']):
  end=m['chapters'][i+1]['time'] if i+1<len(m['chapters']) else dur
  lines+=['[CHAPTER]','TIMEBASE=1/1000',f'START={round(c["time"]*1000)}',f'END={round(end*1000)}',f'title={c["title"]}']
 meta.write_text('\n'.join(lines)+'\n');print('Encode continuous full master',flush=True)
 run([*ci,'-i',meta,'-map','0:v:0','-map','0:a:0','-map_metadata','1','-map_chapters','1','-vf','setpts=N/(30*TB),setsar=1,format=yuv420p,setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709','-af',af,*ENC,'-r','30','-fps_mode','cfr','-c:a','aac','-b:a','256k','-ar','48000','-bsf:a','noise=drop=lt(pts\,0)','-use_editlist','0','-movflags','+faststart',dst],work/'final-render.log');print('FINISHED',dst,flush=True)
if __name__=='__main__':
 m=json.loads(Path(sys.argv[1]).read_text())
 if '--opening-only' in sys.argv:
  for s in m['segments'][:3]:print('Opening',s['id'],segment(s),flush=True)
 else:full(m)
