"""Match restored raw dialogue to finished v4; remux unchanged video, without re-encoding it."""
from pathlib import Path
import json,subprocess,numpy as np,concurrent.futures,wave,re,hashlib,shutil
R=Path(__file__).resolve().parent;D=R/'feedback-revision-v5'
M=json.loads((D/'edit-manifest-v5.json').read_text());OLD=R/'agents-proposed-cut-v4.mp4'
W=D/'work/audio-match';W.mkdir(exist_ok=False)

def rms(path,t,raw=False):
    af='pan=stereo|c0=0.5*c0+0.5*c1|c1=0.5*c0+0.5*c1,highpass=f=60' if raw else 'anull'
    b=subprocess.run(['ffmpeg','-nostdin','-v','error','-ss',str(t),'-i',str(path),'-t','1.2','-map','0:a:0','-af',af,'-ac','1','-ar','48000','-f','f32le','-'],capture_output=True,check=True).stdout
    a=np.frombuffer(b,dtype='<f4')[960:];return float(np.sqrt(np.mean(a*a)))

refs=[('reaction-complete',[(125,106.8),(130,111.8),(134,115.8)]),
      ('guardrails-complete',[(2145,1119.433333),(2150,1124.433333),(2165,1139.433333),(2180,1154.433333)]),
      ('gym-ai-link',[(3910,1928.133333),(3921,1939.133333),(3926,1944.133333)])]
measurements=[];gains={}
for name,windows in refs:
    values=[]
    for source_t,out_t in windows:
        raw,finished=rms(M['source'],source_t,True),rms(OLD,out_t)
        gain=float(20*np.log10(finished/raw));values.append(gain)
        measurements.append(dict(section=name,source_time=source_t,v4_time=out_t,gain_db=gain))
    gains[name]=float(np.median(values))
gains['pricing-bridge']=float(np.median([gains['reaction-complete'],gains['guardrails-complete']]))
(W/'gain-reference.json').write_text(json.dumps(dict(gains=gains,measurements=measurements,
    method='One-second-plus matching spoken windows; median raw-pan/highpass to v4 RMS gain. New pricing bridge uses median established dialogue gain. Raw-only latency-compensated peak limiter prevents amplified peaks.'),indent=2)+'\n')
print('Matched raw gains',gains,flush=True)
with wave.open(str(W/'assembled-audio.wav'),'wb') as out:
    out.setnchannels(2);out.setsampwidth(2);out.setframerate(48000)
    for s in M['assembly_segments']:
        n=s['frames']*1600;duration=n/48000
        af='aresample=48000:first_pts=0'
        if s.get('mix_raw'):
            af+=f',pan=stereo|c0=0.5*c0+0.5*c1|c1=0.5*c0+0.5*c1,highpass=f=60,volume={gains[s["id"]]}dB,alimiter=limit=0.78:attack=5:release=50:level=false:latency=true'
        elif s['kind']=='card':af+=f',volume={s.get("gain_db",-5)}dB'
        af+=f',apad,atrim=end_sample={n},asetpts=N/SR/TB,afade=t=in:d=0.005,afade=t=out:st={max(0,duration-(.22 if s["kind"]=="card" else .008))}:d={.22 if s["kind"]=="card" else .008}'
        p=subprocess.run(['ffmpeg','-nostdin','-v','error','-ss',str(s['in']),'-i',s['source'],'-t',str(duration),'-map',f'0:{s["audio_stream"]}','-af',af,'-ac','2','-ar','48000','-f','s16le','-'],capture_output=True,check=True)
        assert len(p.stdout)==n*4;out.writeframesraw(p.stdout)
with (W/'loudness-pass1.log').open('x') as log:
    p=subprocess.run(['ffmpeg','-nostdin','-hide_banner','-i',str(W/'assembled-audio.wav'),'-af','loudnorm=I=-16:TP=-1.8:LRA=11:print_format=json','-f','null','-'],stdout=log,stderr=log);assert p.returncode==0
stats=json.loads(re.findall(r'\{[^{}]+\}',(W/'loudness-pass1.log').read_text())[-1]);(W/'loudness-pass1.json').write_text(json.dumps(stats,indent=2)+'\n')
af=f"loudnorm=I=-16:TP=-1.8:LRA=11:measured_I={stats['input_i']}:measured_TP={stats['input_tp']}:measured_LRA={stats['input_lra']}:measured_thresh={stats['input_thresh']}:offset={stats['target_offset']}:linear=true,aresample=48000,apad,atrim=end_sample={M['total_frames']*1600},asetpts=N/SR/TB"
new=D/'agents-feedback-cut-v5-audio-matched.mp4';assert not new.exists()
cmd=['ffmpeg','-nostdin','-hide_banner','-n','-v','warning','-i',str(D/M['output_file']),'-i',str(W/'assembled-audio.wav'),'-map','0:v:0','-map','1:a:0','-map_metadata','0','-map_chapters','0','-c:v','copy','-af',af,'-c:a','aac','-b:a','256k','-ar','48000','-t',str(M['duration']),'-bsf:a',r'noise=drop=lt(pts\,0)','-use_editlist','0','-movflags','+faststart',str(new)]
(W/'remux-command.json').write_text(json.dumps(cmd,indent=2)+'\n')
with (W/'remux.log').open('x') as f:p=subprocess.run(cmd,stdout=f,stderr=f);assert p.returncode==0
def video_hash(path):
    p=subprocess.Popen(['ffmpeg','-nostdin','-v','error','-i',str(path),'-map','0:v:0','-c:v','copy','-f','h264','-'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    h=hashlib.sha256()
    while True:
        b=p.stdout.read(1024*1024)
        if not b:break
        h.update(b)
    assert p.wait()==0;return h.hexdigest()
vold=video_hash(D/M['output_file']);vnew=video_hash(new);assert vold==vnew
(D/'qc/video-identity-audio-match.json').write_text(json.dumps(dict(before=M['output_file'],after=new.name,
    h264_sha256=vnew,byte_identical_video=True,picture_samples_reused='87 sampled frames across six boards; identical encoded video proves unchanged pictures and edit timing.'),indent=2)+'\n')
prior=D/'edit-manifest-v5-before-audio-match.json';assert not prior.exists();prior.write_text(json.dumps(M,indent=2)+'\n')
for ext in ['srt','vtt']:shutil.copy2(D/Path(M['output_file']).with_suffix('.'+ext),new.with_suffix('.'+ext))
M['output_file']=new.name;M['audio_finishing']=dict(raw_clip_gain_db=gains,raw_peak_limiter='0.78 amplitude; 5ms attack, 50ms release; latency compensation enabled',picture_unchanged=True,reason='Correct quieter restored raw passages; preserve surrounding v4 dialogue levels.')
(D/'edit-manifest-v5.json').write_text(json.dumps(M,indent=2)+'\n')
print('Audio-matched export rendered; encoded video byte-identical.',flush=True)
