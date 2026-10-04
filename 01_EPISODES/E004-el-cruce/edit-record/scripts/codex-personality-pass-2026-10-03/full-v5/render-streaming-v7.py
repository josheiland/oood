#!/usr/bin/env python3
"""Sample-exact streamed assembly: preserve every source and output; no new video intermediates."""
from pathlib import Path
import os,sys,json,subprocess,re,importlib.util,time
os.environ['PATH']='/opt/homebrew/bin:'+os.environ.get('PATH','')
Q=Path(__file__).resolve().parent;W=Q/'stream-render-work-v7';W.mkdir(exist_ok=True)
M=json.loads((Q/'edit-manifest-v7-final.json').read_text());DUR=M['duration'];BAL=f"volume='if(lt(t,9.1),0.630957,if(between(t,14.3666667,{DUR-10.7666667}),1.995262,1))':eval=frame"
# Reuse this pass's own exact composition graph, changing only the transport codec/container.
source=(Q/'render-personality.py').read_text();body=source[source.index(' dur=round((s[\'out\']'):source.index('\ndef full(m):')]
body=body[:body.index(' run([*args')]+" return [*args,'-filter_complex_threads','2','-filter_complex',';'.join(filters),'-map','[v]','-map','[a]','-c:v','rawvideo','-threads','2','-pix_fmt','yuv420p','-c:a','pcm_s16le','-ac','2','-ar','48000','-t',dur,'-f','nut',dst]\n"
ns={};body=body.replace("args+=['-threads','2','-i',s['processed_audio']]","args+=['-threads','2','-ss',s.get('processed_audio_offset',0),'-i',s['processed_audio']]")
body=body.replace("afade=t=in:d={s.get('fade_in',.005)},afade=t=out:st={max(0,dur-s.get('fade_out',.01))}:d={s.get('fade_out',.01)}","afade=t=in:d={s.get('fade_in',.005)},afade=t=out:st={max(0,dur-s.get('fade_out',.01))}:d={s.get('fade_out',.01)}")
exec('def graph(s,dst):\n'+body,ns);graph=ns['graph']
def af(s,dur):
 f=f'atrim=duration={dur},asetpts=PTS-STARTPTS,aresample=48000,apad=whole_dur={dur},atrim=duration={dur}'
 if s.get('audio_in') is not None:f+=f",volume=0:enable='lt(t,{max(0,s['audio_in']-s['in'])})'"
 if s.get('audio_out') is not None:f+=f",volume=0:enable='gte(t,{max(0,s['audio_out']-s['in'])})'"
 for a,b in s.get('mutes',[]):f+=f",volume=0:enable='between(t,{a-s['in']},{b-s['in']})'"
 return f+f',volume={s.get("gain_db",0)}dB,afade=t=in:d={s.get('fade_in',.005)},afade=t=out:st={max(0,dur-s.get('fade_out',.01))}:d={s.get('fade_out',.01)}'
def audio_measure():
 dst=W/'loudness-pass1.json'
 if dst.exists():return json.loads(dst.read_text())
 with (W/'audio-measure.log').open('w') as log:
  read=subprocess.Popen(['ffmpeg','-nostdin','-hide_banner','-f','s16le','-ar','48000','-ac','2','-i','pipe:0','-af',BAL+',loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-'],stdin=subprocess.PIPE,stdout=log,stderr=log)
  counts=[]
  try:
   for i,s in enumerate(M['segments']):
    dur=round((s['out']-s['in'])*30)/30;audio=s.get('processed_audio',s['source']);seek=s.get('processed_audio_offset',0) if s.get('processed_audio') else s['in'];cmd=['ffmpeg','-nostdin','-hide_banner','-v','error','-threads','2','-ss',str(seek),'-i',audio,'-map','0:a:0','-vn','-t',str(dur),'-af',af(s,dur),'-ac','2','-ar','48000','-f','s16le','pipe:1']
    p=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE);total=0
    while data:=p.stdout.read(1024*1024):read.stdin.write(data);total+=len(data)
    err=p.stderr.read();rc=p.wait()
    if rc:raise RuntimeError(err.decode()[-1200:])
    assert total==round(dur*48000)*4,(s['id'],total,round(dur*48000)*4)
    counts.append({'segment':s['id'],'samples':total//4});print('Measured audio',i+1,len(M['segments']),flush=True)
   read.stdin.close();assert read.wait()==0
  except BaseException:read.terminate();raise
 st=json.loads(re.findall(r'\{[^{}]+\}',(W/'audio-measure.log').read_text())[-1]);dst.write_text(json.dumps(st,indent=2));(W/'audio-sample-counts.json').write_text(json.dumps(counts,indent=2));return st

def render():
 out=Q/M['output_file']
 if out.exists():raise FileExistsError(out)
 st=audio_measure();print('Audio measurement complete:',st,flush=True)
 pipes=[]
 for i,s in enumerate(M['segments']):
  p=W/f'segment-{i:03}.nut'
  if p.exists():
   if not p.is_fifo():raise RuntimeError(p)
  else:os.mkfifo(p)
  pipes.append(p)
 concat=W/'stream-list.txt';concat.write_text(''.join(f"file '{p}'\nduration {round((s['out']-s['in'])*30)/30}\n" for p,s in zip(pipes,M['segments'])))
 meta=W/'chapters.ffmeta';lines=[';FFMETADATA1','title=Out of Our Depth | El Cruce | Personality pass','comment=Proposed for host review; C layout selected']
 for i,c in enumerate(M['chapters']):
  end=M['chapters'][i+1]['time'] if i+1<len(M['chapters']) else DUR
  lines+=['[CHAPTER]','TIMEBASE=1/1000',f'START={round(c["time"]*1000)}',f'END={round(end*1000)}',f'title={c["title"]}']
 meta.write_text('\n'.join(lines)+'\n')
 filt=BAL+f",loudnorm=I=-16:TP=-1.5:LRA=11:measured_I={st['input_i']}:measured_TP={st['input_tp']}:measured_LRA={st['input_lra']}:measured_thresh={st['input_thresh']}:offset={st['target_offset']}:linear=true,aresample=48000,apad=whole_dur={DUR},atrim=duration={DUR},asetpts=N/SR/TB"
 cmd=['ffmpeg','-nostdin','-n','-hide_banner','-threads','2','-probesize','1000000','-analyzeduration','1000000','-f','concat','-safe','0','-i',str(concat),'-i',str(meta),'-map','0:v:0','-map','0:a:0','-map_metadata','1','-map_chapters','1','-vf','setpts=N/(30*TB),setsar=1,format=yuv420p,setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709','-af',filt,'-c:v','libx264','-preset','veryfast','-crf','20','-threads','4','-pix_fmt','yuv420p','-bf','0','-g','30','-sc_threshold','0','-r','30','-fps_mode','cfr','-color_range','tv','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-c:a','aac','-b:a','256k','-ar','48000','-bsf:a',r'noise=drop=lt(pts\,0)','-use_editlist','0','-movflags','+faststart',str(out)]
 log=(W/'final-render.log').open('w');reader=subprocess.Popen(cmd,stdout=log,stderr=log);(W/'process-ids.json').write_text(json.dumps({'python':os.getpid(),'encoder':reader.pid,'output':str(out)}))
 try:
  for i,(s,p) in enumerate(zip(M['segments'],pipes)):
   print('Render',i+1,len(pipes),s['id'],flush=True)
   with p.open('wb',buffering=0) as target,(W/f'segment-{i:03}.log').open('w') as wl:
    args=graph(s,'pipe:1');producer=subprocess.Popen(['ffmpeg','-nostdin','-hide_banner',*map(str,args)],stdout=target,stderr=wl);(W/'current-segment.json').write_text(json.dumps({'segment':s['id'],'producer':producer.pid,'encoder':reader.pid}));rc=producer.wait()
    if rc:raise RuntimeError(f'Producer failed {s["id"]}: {W/f"segment-{i:03}.log"}')
   if reader.poll() is not None and reader.returncode:raise RuntimeError('Final reader failed')
  rc=reader.wait();log.close()
  if rc:raise RuntimeError('Master encoder failed; inspect final-render.log')
 except BaseException:
  reader.terminate();raise
 print('FINISHED',out,flush=True)
if __name__=='__main__':
 (W/'supervisor.json').write_text(json.dumps({'pid':os.getpid(),'manifest':'edit-manifest-v7-final.json'}));render()
