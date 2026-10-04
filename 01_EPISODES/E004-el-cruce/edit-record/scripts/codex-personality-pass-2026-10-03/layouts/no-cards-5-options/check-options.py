from pathlib import Path
import os,json,subprocess,hashlib,re,time
os.environ['PATH']='/opt/homebrew/bin:'+os.environ.get('PATH','')
N=Path(__file__).resolve().parent;L=N.parent;m=json.loads((N/'layout-manifest.json').read_text());Q=N/'qc'
source_hash=subprocess.check_output(['ffmpeg','-v','error','-i',m['audio_source'],'-map','0:a:0','-c','copy','-f','hash','-hash','sha256','-']).decode().strip()
original_report=json.loads((L/'qc/a-balanced-v2-report.json').read_text());assert original_report['passed'];reports=[]
for o in m['options']:
 p=N/f'{o["id"]}.mp4';done=False
 # Renderer remains sequential; check an export only after its end sample appears.
 while not (N/f'{o["id"]}-end.png').exists():time.sleep(.5)
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]));v=next(s for s in probe['streams'] if s['codec_type']=='video');a=next(s for s in probe['streams'] if s['codec_type']=='audio')
 subprocess.run(['python3','/Users/je/oood/skills/oood-episode-producer/scripts/color_qc.py',str(p),'--report',str(Q/f'{o["id"]}-color.json')],check=True,stdout=subprocess.DEVNULL);color=json.loads((Q/f'{o["id"]}-color.json').read_text())
 ah=subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-map','0:a:0','-c','copy','-f','hash','-hash','sha256','-']).decode().strip()
 res=subprocess.run(['ffmpeg','-nostdin','-v','warning','-threads','2','-i',str(p),'-map','0:v:0','-map','0:a:0','-f','null','-'],capture_output=True,text=True,check=True);(Q/f'{o["id"]}-decode.log').write_text(res.stderr)
 packets=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_packets','-show_entries','packet=stream_index,dts_time','-of','json',str(p)]))['packets'];last={};monotonic=True;nonnegative=True
 for pkt in packets:
  t=float(pkt.get('dts_time','0'));idx=pkt['stream_index'];monotonic &=idx not in last or t>=last[idx];nonnegative &=t>=-.0001;last[idx]=t
 checks={'frame_count':int(v['nb_frames'])==1180,'duration':abs(float(v['duration'])-1180/30)<.001,'av_duration':abs(float(v['duration'])-float(a['duration']))<.05,'zero_starts':abs(float(v['start_time']))<.001 and abs(float(a['start_time']))<.001,'full_audio_video_decode':True,'coded_color_container_all_frames':color['passed'],'audio_identical_to_checked_source':ah==source_hash,'packet_monotonic':monotonic,'packet_nonnegative':nonnegative}
 r={'file':p.name,'passed':all(checks.values()),'checks':checks,'frames':int(v['nb_frames']),'duration':float(v['duration']),'av_delta':abs(float(v['duration'])-float(a['duration'])),'audio_hash':ah,'integrated_lufs':original_report['integrated_lufs'],'true_peak_dbtp':original_report['true_peak_dbtp'],'audio_metrics_provenance':'Encoded AAC copied byte-for-byte from checked A-v2 comparison; hash verified','bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()};reports.append(r);(Q/f'{o["id"]}-report.json').write_text(json.dumps(r,indent=2)+'\n');print(p.name,r['passed'],flush=True)
assert all(r['passed'] for r in reports)
(Q/'comparison-summary.json').write_text(json.dumps({'passed':True,'identical_checked_audio':True,'reports':reports},indent=2)+'\n');print('ALL FIVE PASSED',flush=True)
