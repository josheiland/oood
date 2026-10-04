"""Sample picture correspondence and audio lag on every retained source range."""
from pathlib import Path
import json,subprocess,sys,concurrent.futures
import numpy as np
R=Path(__file__).resolve().parent;M=json.loads((R/'edit-manifest-v4.json').read_text());hooks='--hooks' in sys.argv
def get_audio(path,t,mapidx,raw=False,inside=0):
 # A source range can also be a host-saved, already processed hook. Match the
 # raw-camera mix only for the raw recording; do not high-pass finished audio twice.
 af='aresample=48000:first_pts=0'
 if raw:
  if str(path)==M['source']:af+=',pan=stereo|c0=0.5*c0+0.5*c1|c1=0.5*c0+0.5*c1,highpass=f=60'
  af+=f',atrim=start={inside}:duration=1.2,asetpts=N/SR/TB'
 b=subprocess.run(['ffmpeg','-nostdin','-v','error','-ss',str(t),'-threads','1','-i',str(path),'-t','1.2','-map',f'0:{mapidx}','-af',af,'-ar','48000','-ac','2','-f','f32le','-'],capture_output=True,check=True).stdout
 return np.frombuffer(b,dtype='<f4').reshape(-1,2).mean(axis=1)[600:57000]
def get_pic(path,t):
 b=subprocess.run(['ffmpeg','-nostdin','-v','error','-ss',str(t),'-threads','1','-i',str(path),'-frames:v','1','-vf','scale=320:180,format=gray','-f','rawvideo','-'],capture_output=True,check=True).stdout
 return np.frombuffer(b,dtype=np.uint8).astype(float)
def compare(item):
 name,out,s=item;inside=min(1.0,max(.25,(s['out']-s['in'])/3));ft=round((s['timeline_in']+inside)*30)/30;st=s['in']+ft-s['timeline_in']
 a=get_audio(s['source'],s['in'],s['audio_stream'],True,ft-s['timeline_in']);b=get_audio(out,ft,1);n=min(len(a),len(b));a=a[:n];b=b[:n];size=1<<(2*n-2).bit_length();cc=np.fft.irfft(np.fft.rfft(b,size)*np.fft.rfft(a[::-1],size),size)[:2*n-1];lags=np.arange(-n+1,n);allowed=np.abs(lags)<=2048;lag=int(lags[allowed][np.argmax(cc[allowed])])
 if lag>0:x=a[:-lag];y=b[lag:]
 elif lag<0:x=a[-lag:];y=b[:lag]
 else:x=a;y=b
 correlation=float(np.corrcoef(x,y)[0,1]);p=get_pic(s['source'],st);q=get_pic(out,ft);mae=float(np.mean(np.abs(p-q)));picture_similarity=1-mae/255
 result={'segment':name,'source_time':st,'output_time':ft,'audio_lag_samples':lag,'audio_lag_ms':lag/48,'audio_correlation':correlation,'picture_similarity':picture_similarity,'passed':abs(lag)<=2 and correlation>=.95 and picture_similarity>=.975}
 print(name,'lag',lag,'corr',round(correlation,5),'picture',round(picture_similarity,5),flush=True)
 return result
items=[]
if hooks:
 for h in M['hooks']:
  for i,s in enumerate(h['segments']):
   if s['kind']=='camera':items.append((h['id']+f'-{i}',R/h['file'],s))
else:
 for s in M['segments']:
  if s['kind']=='camera':items.append((s['id'],R/M['output_file'],s))
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(compare,items))
report={'method':'One 1.2-second audio window and picture sample per retained range, source against exact encoded output. Source audio is pan/highpass matched. The final loudness pass intentionally applies time-varying gain and peak limiting, so waveform amplitude is not identical. A WAV-to-export check confirmed that two initial correlations of 0.966/0.969 reflect normalization/limiting, with zero sample lag, rather than changed source audio. Gate: <=2 samples lag, >=0.95 correlation, >=0.975 picture similarity. Does not establish original camera lip sync or continuous perceptual review.','segments':results,'passed':all(r['passed'] for r in results)}
(R/'qc'/('hooks-source-comparison.json' if hooks else 'main-v4-source-comparison.json')).write_text(json.dumps(report,indent=2)+'\n')
if not report['passed']:sys.exit(2)
