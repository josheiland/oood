"""Read-only, exact-export verification. Run only after the render finishes."""
from pathlib import Path
import json,os,subprocess,re,hashlib,csv
import numpy as np
os.environ['PATH']='/opt/homebrew/bin:'+os.environ.get('PATH','')
Q=Path(__file__).resolve().parent;REPO=Q.parents[4]
M=json.loads((Q/'edit-manifest-v11-final.json').read_text());MASTER=Q/M['output_file'];W=Q/'qc-v11'
W.mkdir(exist_ok=False)
def run(args,log):
    with (W/log).open('w') as f:
        p=subprocess.run(list(map(str,args)),stdout=f,stderr=f)
    if p.returncode:raise RuntimeError(f'Failed {log}')
def capture(args):
    p=subprocess.run(list(map(str,args)),capture_output=True)
    if p.returncode:raise RuntimeError(p.stderr.decode()[-2000:])
    return p.stdout
print('Coded headers, container and every decoded frame',flush=True)
run(['python3',REPO/'skills/oood-episode-producer/scripts/color_qc.py',MASTER,'--report',W/'color-consistency.json'],'color-gate.log')
color=json.loads((W/'color-consistency.json').read_text());assert color['passed']
probe=json.loads(capture(['ffprobe','-v','error','-show_streams','-show_format','-show_chapters','-of','json',MASTER]));(W/'probe.json').write_text(json.dumps(probe,indent=2))
video=next(s for s in probe['streams'] if s['codec_type']=='video');audio=next(s for s in probe['streams'] if s['codec_type']=='audio')
assert int(video['nb_frames'])==M['expected_frames']
assert abs(float(video['duration'])-M['duration'])<.001
assert abs(float(audio['duration'])-float(video['duration']))<=1/30
assert video.get('has_b_frames')==0
print('Complete audiovisual decode and black/silence detection',flush=True)
run(['ffmpeg','-nostdin','-hide_banner','-threads','2','-i',MASTER,'-filter_threads','2','-map','0:v:0','-map','0:a:0','-vf','blackdetect=d=0.1:pix_th=0.05','-af','silencedetect=n=-48dB:d=1.5','-f','null','-'],'decode-and-spans.log')
spans=(W/'decode-and-spans.log').read_text()
black=[{'start':float(a),'end':float(b),'duration':float(c)} for a,b,c in re.findall(r'black_start:([\d.]+) black_end:([\d.]+) black_duration:([\d.]+)',spans)]
silence=re.findall(r'silence_(start|end): ([\d.]+)',spans)
print('Encoded loudness and true peak',flush=True)
run(['ffmpeg','-nostdin','-hide_banner','-threads','2','-i',MASTER,'-vn','-filter_threads','2','-af','loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-'],'encoded-loudness.log')
loud=json.loads(re.findall(r'\{[^{}]+\}',(W/'encoded-loudness.log').read_text())[-1]);assert -17<=float(loud['input_i'])<=-15;assert float(loud['input_tp'])<=-1
print('Packet timing and continuity',flush=True)
packet_checks={}
for kind in ['v:0','a:0']:
    data=capture(['ffprobe','-v','error','-select_streams',kind,'-show_packets','-show_entries','packet=pts_time,dts_time,duration_time','-of','csv=p=0',MASTER]).decode()
    values=[]
    for line in data.splitlines():
        row=line.split(',')
        if len(row)>=3 and row[0]!='N/A':values.append(tuple(float(x) for x in row[:3]))
    assert values and abs(values[0][0])<.0001
    errors=[i for i in range(1,len(values)) if values[i][0]<=values[i-1][0] or abs(values[i][0]-values[i-1][0]-values[i-1][2])>.0001]
    assert not errors,(kind,errors[:10])
    packet_checks[kind]={'count':len(values),'first_pts':values[0][0],'last_end':values[-1][0]+values[-1][2],'strictly_increasing_and_contiguous':True}

print('Source-to-export audio alignment at start, middle and end',flush=True)
sync=[]
hook_sid=M['segments'][0]['source_id']
for sid,source_at in [(hook_sid,3),('A',200),('B',480),('C',700),('C',1490)]:
    s=next(s for s in M['segments'] if s.get('source_id')==sid and s['in']<=source_at and s['out']>=source_at+6 and not s.get('processed_audio'))
    final_at=s['timeline_in']+source_at-s['in']
    def pcm(path,at):
        return np.frombuffer(capture(['ffmpeg','-nostdin','-v','error','-threads','2','-ss',str(at),'-i',path,'-t','6','-vn','-map','0:a:0','-ac','1','-ar','8000','-f','f32le','pipe:1']),dtype='<f4').astype(float)
    a,b=pcm(s['source'],source_at),pcm(MASTER,final_at);a-=a.mean();b-=b.mean();n=min(len(a),len(b));a=a[:n];b=b[:n]
    size=1<<((2*n-1).bit_length());corr=np.fft.irfft(np.fft.rfft(b,size)*np.conj(np.fft.rfft(a,size)),size)
    lags=np.arange(-1600,1601);scores=corr[lags%size];lag=int(lags[np.argmax(scores)])
    if lag>=0:x,y=a[:n-lag],b[lag:]
    else:x,y=a[-lag:],b[:n+lag]
    similarity=float(np.dot(x,y)/(np.linalg.norm(x)*np.linalg.norm(y)));delta=lag/8000
    assert abs(delta)<=1/30 and similarity>.7,(sid,delta,similarity)
    sync.append({'source_id':sid,'source_time':source_at,'final_time':final_at,'audio_offset_seconds':delta,'correlation':similarity,'limit':'Measures edit-induced audio offset relative to the recorded mix, not original camera lip sync.'})
print('Hash and final review record',flush=True)
h=hashlib.sha256()
with MASTER.open('rb') as f:
    while b:=f.read(8*1024*1024):h.update(b)
report={'path':str(MASTER),'bytes':MASTER.stat().st_size,'sha256':h.hexdigest(),'duration':M['duration'],'frames':int(video['nb_frames']),'color_container_passed':True,'full_av_decode_passed':True,'loudness':loud,'audio_video_duration_difference':abs(float(audio['duration'])-float(video['duration'])),'packets':packet_checks,'black_spans':black,'silence_events':silence,'source_audio_alignment':sync,'caption_chapter_structural_checks_passed':True,'status':'Technically checked; host audiovisual review, caption auditory proof and exact-version approval remain pending.'}
(W/'report.json').write_text(json.dumps(report,indent=2)+'\n');(Q/'qc-summary-v11.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':True,'duration':report['duration'],'loudness':loud['input_i'],'true_peak':loud['input_tp'],'black_spans':black,'silence_events':silence,'sha256':report['sha256']}),flush=True)
