"""Reversible local assembly; single final H.264 encoder; no source mutation."""
from pathlib import Path
import argparse,json,subprocess,wave,re
R=Path(__file__).resolve().parent
M=json.loads((R/'edit-manifest-v3.json').read_text());FPS=30;SR=48000

def run(args,log):
 with log.open('x') as f:
  p=subprocess.run(['ffmpeg','-nostdin','-hide_banner','-n',*map(str,args)],stdout=f,stderr=f)
 if p.returncode:raise RuntimeError(f'Failed: {log}')

def audio(segments,work):
 wav=work/'assembled-audio.wav'
 assert not wav.exists()
 with wave.open(str(wav),'wb') as out:
  out.setnchannels(2);out.setsampwidth(2);out.setframerate(SR)
  for k,s in enumerate(segments):
   samples=s['frames']*1600;dur=samples/SR
   af=f'aresample=48000:first_pts=0,apad,atrim=end_sample={samples},asetpts=N/SR/TB'
   if s['kind']=='camera':af+=',pan=stereo|c0=0.5*c0+0.5*c1|c1=0.5*c0+0.5*c1,highpass=f=60'
   else:af+=f',volume={s.get("gain_db",-5)}dB'
   af+=f',afade=t=in:d=0.005,afade=t=out:st={max(0,dur-(.22 if s["kind"]=="card" else .008))}:d={.22 if s["kind"]=="card" else .008}'
   cmd=['ffmpeg','-nostdin','-v','error','-ss',str(s['in']),'-i',s['source'],'-t',str(dur),'-map',f'0:{s["audio_stream"]}','-af',af,'-ac','2','-ar','48000','-f','s16le','-']
   p=subprocess.run(cmd,capture_output=True,check=True);b=p.stdout
   assert len(b)==samples*4,(k,len(b),samples*4)
   out.writeframesraw(b)
 print('Audio assembled',wav.name,flush=True)
 run(['-i',wav,'-af','loudnorm=I=-16:TP=-1.8:LRA=11:print_format=json','-f','null','-'],work/'loudness-pass1.log')
 stats=json.loads(re.findall(r'\{[^{}]+\}',(work/'loudness-pass1.log').read_text())[-1]);(work/'loudness-pass1.json').write_text(json.dumps(stats,indent=2))
 return wav,stats

def render(segments,dst,work,chapters):
 assert not dst.exists(),dst
 work.mkdir(exist_ok=False,parents=True);wav,stats=audio(segments,work)
 args=['-v','warning'];graph=[]
 total=sum(s['frames'] for s in segments);duration=total/FPS
 for i,s in enumerate(segments):
  if s['kind']=='camera':args+=['-ss',str(s['in']),'-t',str(s['frames']/FPS),'-threads','1','-an','-i',s['source']]
  else:args+=['-loop','1','-framerate','30','-t',str(s['frames']/FPS),'-i',s['still']]
  conversion='scale=1920:1080:out_color_matrix=bt709:out_range=tv' if s['kind']=='card' else 'scale=1920:1080'
  graph.append(f'[{i}:v:0]fps=30,{conversion},setsar=1,format=yuv420p,trim=end_frame={s["frames"]},settb=1/30000,setpts=N*1000[v{i}]')
 n=len(segments)
 args+=['-i',str(wav)]
 graph.append(''.join(f'[v{i}]' for i in range(n))+f'concat=n={n}:v=1:a=0[vcat]')
 graph.append('[vcat]settb=1/30000,setpts=N*1000,setsar=1,format=yuv420p,setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709[vout]')
 af=f"loudnorm=I=-16:TP=-1.8:LRA=11:measured_I={stats['input_i']}:measured_TP={stats['input_tp']}:measured_LRA={stats['input_lra']}:measured_thresh={stats['input_thresh']}:offset={stats['target_offset']}:linear=true,aresample=48000,apad,atrim=end_sample={total*1600},asetpts=N/SR/TB"
 graph.append(f'[{n}:a:0]{af}[aout]')
 gf=work/'filtergraph.txt';gf.write_text(';\n'.join(graph)+'\n')
 meta=work/'chapters.ffmeta';lines=[';FFMETADATA1','title=Out of Our Depth | AI agents | Proposed cut','comment=Host review pending; provisional hook']
 for i,c in enumerate(chapters):
  end=chapters[i+1]['time'] if i+1<len(chapters) else duration
  lines+=['[CHAPTER]','TIMEBASE=1/1000',f'START={round(c["time"]*1000)}',f'END={round(end*1000)}',f'title={c["title"]}']
 meta.write_text('\n'.join(lines)+'\n');args+=['-f','ffmetadata','-i',str(meta)]
 args+=['-filter_complex_threads','2','-filter_complex_script',str(gf),'-map','[vout]','-map','[aout]','-map_metadata',str(n+1),'-map_chapters',str(n+1),'-frames:v',str(total),'-r','30','-fps_mode','cfr','-c:v','libx264','-threads','4','-preset','veryfast','-crf','19','-profile:v','high','-level:v','4.0','-pix_fmt','yuv420p','-bf','0','-g','30','-sc_threshold','0','-color_range','tv','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-video_track_timescale','30000','-c:a','aac','-b:a','256k','-ar','48000','-bsf:a',r'noise=drop=lt(pts\,0)','-use_editlist','0','-movflags','+faststart','-progress',str(work/'render-progress.log'),str(dst)]
 (work/'render-command.json').write_text(json.dumps(args,indent=2))
 print('Encoding',dst.name,total,'frames',flush=True)
 run(args,work/'render.log')
 print('Rendered',dst.name,flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--full',action='store_true');p.add_argument('--hooks',action='store_true');a=p.parse_args()
 if a.full:render(M['segments'],R/M['output_file'],R/'work/full-v3',M['chapters'])
 if a.hooks:
  for h in M['hooks']:render(h['segments'],R/h['file'],R/'work'/h['id'],[])
