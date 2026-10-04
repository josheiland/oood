from pathlib import Path
import json,subprocess,re,hashlib,sys
R=Path(__file__).resolve().parent
m=json.loads((R/'edit-manifest-v3.json').read_text());q=R/'qc';q.mkdir(exist_ok=True)
def capture(cmd,log):
 p=subprocess.run(cmd,capture_output=True,text=True);log.write_text(p.stdout+'\n'+p.stderr)
 if p.returncode:raise RuntimeError(str(log))
 return p
reports=[]
for file,segments in [('el-cruce-proposed-cut-v3.mp4',m['segments'])]:
 p=R/file;tag=p.stem
 if not p.exists():raise FileNotFoundError(p)
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-show_chapters','-of','json',str(p)]))
 video=next(s for s in probe['streams'] if s['codec_type']=='video');audio=next(s for s in probe['streams'] if s['codec_type']=='audio')
 expected=sum(round((s['out']-s['in'])*30) for s in segments)
 col=q/f'{tag}-color.json'
 if not col.exists():
  subprocess.run(['python3','/Users/je/oood/skills/oood-episode-producer/scripts/color_qc.py',str(p),'--report',str(col)],check=True,stdout=subprocess.DEVNULL)
 color=json.loads(col.read_text())
 # This pass decodes audio and video, scans black/silence spans, and measures encoded audio.
 result=capture(['ffmpeg','-nostdin','-hide_banner','-nostats','-i',str(p),'-map','0:v:0','-map','0:a:0','-vf','scale=160:90,blackdetect=d=0.15:pix_th=0.04','-af','silencedetect=n=-48dB:d=1.5,loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-'],q/f'{tag}-decode-levels.log')
 stats=json.loads(re.findall(r'\{[^{}]+\}',result.stderr)[-1])
 packets=subprocess.check_output(['ffprobe','-v','error','-show_packets','-show_entries','packet=stream_index,pts_time,dts_time,duration_time','-of','json',str(p)])
 packets=json.loads(packets)['packets'];last={};monotonic=True;negative=False
 for packet in packets:
  idx=packet['stream_index']
  if idx not in [video['index'],audio['index']]:continue
  t=float(packet.get('dts_time',packet.get('pts_time','0')))
  if idx in last and t<last[idx]:monotonic=False
  if t<-.0001:negative=True
  last[idx]=t
 duration=float(video['duration']);audio_delta=abs(float(audio['duration'])-duration)
 check={'expected_frames':expected,'actual_frames':int(video['nb_frames']),'frame_count_matches':int(video['nb_frames'])==expected,'duration':duration,'duration_matches':abs(duration-expected/30)<.001,'color_container_passed':color['passed'],'audio_video_delta':audio_delta,'audio_video_duration_matches':audio_delta<.05,'full_decode_completed':True,'packet_dts_monotonic':monotonic,'no_negative_packet_time':not negative,'integrated_lufs':float(stats['input_i']),'true_peak_dbtp':float(stats['input_tp']),'loudness_within_target':abs(float(stats['input_i'])+16)<=1,'true_peak_within_target':float(stats['input_tp'])<=-1,'black_spans':re.findall(r'black_start:([\d.]+) black_end:([\d.]+) black_duration:([\d.]+)',result.stderr),'silence_events':re.findall(r'silence_(start|end): ([\d.]+)',result.stderr),'sha256':hashlib.file_digest(p.open('rb'),'sha256').hexdigest(),'bytes':p.stat().st_size,'file':file,'chapters':probe.get('chapters',[])}
 check['passed']=all(check[k] for k in ['frame_count_matches','duration_matches','color_container_passed','audio_video_duration_matches','full_decode_completed','packet_dts_monotonic','no_negative_packet_time','loudness_within_target','true_peak_within_target'])
 (q/f'{tag}-report.json').write_text(json.dumps(check,indent=2));reports.append(check);print(file,check['passed'],check['integrated_lufs'],check['true_peak_dbtp'],flush=True)
(q/'full-summary-v3.json').write_text(json.dumps(reports,indent=2))
source_checks=[]
for inv in ['inventory.json','screens-inventory.json']:
 for s in json.loads((R/'source-review'/inv).read_text()):
  p=Path(s['path']);source_checks.append({'path':str(p),'sha256_matches':hashlib.file_digest(p.open('rb'),'sha256').hexdigest()==s['sha256']})
(q/'originals-unchanged-full-v3.json').write_text(json.dumps(source_checks,indent=2))
assert all(r['passed'] for r in reports)
assert all(c['sha256_matches'] for c in source_checks)
print('ALL EXPORTS PASSED; ORIGINALS UNCHANGED',flush=True)
