"""Exact export gates; checks are evidence of technical readiness, not host approval."""
from pathlib import Path
import json,subprocess,re,hashlib,sys,concurrent.futures,importlib.util
R=Path(__file__).resolve().parent;M=json.loads((R/'edit-manifest-v4.json').read_text())
spec=importlib.util.spec_from_file_location('color_qc',R.parents[3]/'skills/oood-episode-producer/scripts/color_qc.py');C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C)
def cmd(args):
 p=subprocess.run(args,capture_output=True,text=True)
 if p.returncode:raise RuntimeError(p.stderr[-1500:])
 return p
def verify(item):
 name,path,n=item;reportpath=R/'qc'/f'{name}-report.json'
 assert not reportpath.exists(),reportpath
 probe=json.loads(cmd(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)]).stdout)
 v=[s for s in probe['streams'] if s['codec_type']=='video'];a=[s for s in probe['streams'] if s['codec_type']=='audio'];assert len(v)==len(a)==1
 avok=int(v[0]['nb_frames'])==n and v[0]['width']==1920 and v[0]['height']==1080 and v[0]['r_frame_rate']=='30/1' and abs(float(v[0]['duration'])-n/30)<.002 and abs(float(a[0]['duration'])-n/30)<.04 and float(v[0].get('start_time',0))==0 and float(a[0].get('start_time',0))==0
 color=C.verify(path);(R/'qc'/f'{name}-color.json').write_text(json.dumps(color,indent=2)+'\n')
 pack=cmd(['ffprobe','-v','error','-show_packets','-show_entries','packet=codec_type,stream_index,pts_time,dts_time','-of','compact=p=0',str(path)]).stdout
 last={};packetok=True;count={}
 for line in pack.splitlines():
  d=dict(x.split('=',1) for x in line.split('|') if '=' in x)
  if d.get('codec_type') not in ('video','audio'):continue
  k=d['stream_index'];pts=float(d['pts_time']);dts=float(d['dts_time']);packetok &= pts>=0 and dts>=0 and dts>last.get(k,-1);last[k]=dts;count[k]=count.get(k,0)+1
 log=cmd(['ffmpeg','-nostdin','-hide_banner','-nostats','-threads','4','-i',str(path),'-map','0:v:0','-map','0:a:0','-vf','scale=160:90,blackdetect=d=0.12:pix_th=0.10:pic_th=0.98','-af','silencedetect=n=-50dB:d=1.5,loudnorm=I=-16:TP=-1.8:LRA=11:print_format=json','-f','null','-']).stderr
 (R/'qc'/f'{name}-decode-audio.log').write_text(log)
 loud=json.loads(re.findall(r'\{[^{}]+\}',log)[-1]);black=re.findall(r'black_start:([\d.]+) black_end:([\d.]+) black_duration:([\d.]+)',log);silence=re.findall(r'silence_start:([^\s]+)|silence_end:([^\s]+) \| silence_duration:([^\s]+)',log)
 loudok=-17.2<=float(loud['input_i'])<=-14.8 and float(loud['input_tp'])<=-1.0
 errorlines=[l for l in log.splitlines() if re.search(r'error while|invalid data|corrupt|non.monoton|decode_slice_header error',l,re.I)]
 result={'file':str(path),'bytes':path.stat().st_size,'sha256':hashlib.file_digest(path.open('rb'),'sha256').hexdigest(),'video':v[0],'audio':a[0],'expected_frames':n,'expected_duration':n/30,'av_structure_passed':avok,'packet_timing_passed':packetok,'packet_counts':count,'color_passed':color['passed'],'loudness':loud,'loudness_passed':loudok,'black_spans':black,'silence_events':silence,'full_decode_errors':errorlines,'passed':bool(avok and packetok and color['passed'] and loudok and not black and not errorlines),'continuous_host_listening':'not established; pending','caption_auditory_proof':'pending'}
 reportpath.write_text(json.dumps(result,indent=2)+'\n');print(name,'PASS' if result['passed'] else 'FAIL','LUFS',loud['input_i'],'TP',loud['input_tp'],'frames',n,flush=True)
 if not result['passed']:raise RuntimeError(f'Export gate failed: {reportpath}')
 return result
items=[(h['id'],R/h['file'],h['frames']) for h in M['hooks']] if '--hooks' in sys.argv else [('main-v4',R/M['output_file'],M['total_frames'])]
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(verify,items))
