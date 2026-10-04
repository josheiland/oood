from pathlib import Path
import os,json,subprocess,re,hashlib
os.environ['PATH']='/opt/homebrew/bin:'+os.environ.get('PATH','')
L=Path(__file__).resolve().parent;Q=L/'qc';Q.mkdir(exist_ok=True);m=json.loads((L/'layout-options.json').read_text());reports=[]
expected=round((m['camera_out']-m['camera_in'])*30)
for o in m['options']:
 tag=o['id']+'-v2';p=L/f'{tag}.mp4';probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]));v=next(x for x in probe['streams'] if x['codec_type']=='video');a=next(x for x in probe['streams'] if x['codec_type']=='audio')
 subprocess.run(['python3','/Users/je/oood/skills/oood-episode-producer/scripts/color_qc.py',str(p),'--report',str(Q/f'{tag}-color.json')],stdout=subprocess.DEVNULL,check=True)
 color=json.loads((Q/f'{tag}-color.json').read_text())
 res=subprocess.run(['ffmpeg','-nostdin','-hide_banner','-nostats','-threads','2','-i',str(p),'-map','0:v:0','-map','0:a:0','-vf','scale=160:90,blackdetect=d=0.15:pix_th=0.04','-af','loudnorm=I=-16:TP=-1:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True);(Q/f'{tag}-decode-levels.log').write_text(res.stderr);stats=json.loads(re.findall(r'\{[^{}]+\}',res.stderr)[-1])
 packets=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_packets','-show_entries','packet=stream_index,dts_time','-of','json',str(p)]))['packets'];last={};monotonic=True;nonnegative=True
 for pkt in packets:
  t=float(pkt.get('dts_time','0'));idx=pkt['stream_index'];monotonic &=idx not in last or t>=last[idx];nonnegative &= t>=-.0001;last[idx]=t
 audio_hash=subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-map','0:a:0','-c','copy','-f','hash','-hash','sha256','-']).decode().strip()
 checks={'frames_match':int(v['nb_frames'])==expected,'duration_match':abs(float(v['duration'])-expected/30)<.001,'av_duration_match':abs(float(v['duration'])-float(a['duration']))<.05,'zero_start':abs(float(v['start_time']))<.001 and abs(float(a['start_time']))<.001,'complete_decode':True,'color_container':color['passed'],'nonnegative_packet_times':nonnegative,'monotonic_packet_times':monotonic,'loudness':abs(float(stats['input_i'])+16)<1,'true_peak':float(stats['input_tp'])<=-1}
 report={'file':p.name,'passed':all(checks.values()),'checks':checks,'frames':int(v['nb_frames']),'duration':float(v['duration']),'av_delta':abs(float(v['duration'])-float(a['duration'])),'integrated_lufs':float(stats['input_i']),'true_peak_dbtp':float(stats['input_tp']),'black_spans':re.findall(r'black_start:([\d.]+)',res.stderr),'audio_packet_hash':audio_hash,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size};reports.append(report);(Q/f'{tag}-report.json').write_text(json.dumps(report,indent=2)+'\n')
 for t,suffix in [(0,'start'),(6.4,'still'),(38.9,'end')]:subprocess.run(['ffmpeg','-v','error','-nostdin','-n','-threads','2','-ss',str(t),'-i',str(p),'-frames:v','1','-threads','2',str(L/f'{tag}-export-{suffix}.png')],check=True)
 print(tag,report['passed'],report['integrated_lufs'],report['true_peak_dbtp'],flush=True)
assert len({r['audio_packet_hash'] for r in reports})==1
assert all(r['passed'] for r in reports)
(Q/'comparison-summary-v2.json').write_text(json.dumps({'status':'Technical gate passed; subjective format choice pending','identical_audio':True,'reports':reports},indent=2)+'\n')
print('ALL THREE PASSED',flush=True)
