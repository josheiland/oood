from pathlib import Path
import subprocess,json,hashlib,re,numpy as np
from PIL import Image,ImageDraw,ImageFont
H=Path(__file__).resolve().parent;ROOT=H.parents[3];Q=H/'qc';P=json.loads((H/'edit-decisions.json').read_text());S=Path(P['source']);O=H/'episode-001-30min-alternative.mp4'
def run(args):return subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
def probe(p):return json.loads(run(['ffprobe','-v','error','-show_streams','-show_format','-show_chapters','-of','json',str(p)]).stdout)
m=probe(O);v=next(s for s in m['streams'] if s['codec_type']=='video');a=next(s for s in m['streams'] if s['codec_type']=='audio')
assert int(v['nb_frames'])==P['total_frames'] and v['width']==1920 and v['height']==1080 and v['has_b_frames']==0
assert abs(float(v['duration'])-P['duration_seconds'])<.001 and abs(float(a['duration'])-P['duration_seconds'])<.001
assert float(v['start_time'])==float(a['start_time'])==0
chap=json.loads((H/'chapters.json').read_text());assert len(m['chapters'])==len(chap)
for x,y in zip(m['chapters'],chap):assert abs(float(x['start_time'])-y['frame']/30)<.001 and x['tags']['title']==y['title']
print('Exact frame count, A/V timing and all 16 chapters passed.',flush=True)
def pcm(p,t,length=2):
 r=run(['ffmpeg','-nostdin','-v','error','-ss',f'{t:.9f}','-threads','1','-i',str(p),'-t',str(length),'-map','0:a:0','-vn','-ac','1','-ar','48000','-f','f32le','-'])
 return np.frombuffer(r.stdout,dtype='<f4').astype(float)
checks=[]
for i,s in enumerate(P['segments'],1):
 frame=(s['source_start_frame']+s['source_end_frame'])//2;out=s['output_start_frame']+frame-s['source_start_frame']
 x=pcm(S,frame/30);y=pcm(O,out/30);n=min(len(x),len(y));x=x[:n];y=y[:n]
 size=1<<(2*n-1).bit_length();cross=np.fft.irfft(np.fft.rfft(y,size)*np.conj(np.fft.rfft(x,size)),size);lags=np.arange(-240,241);lag=int(lags[np.argmax(cross[lags%size])])
 if lag>0:xx=x[:-lag];yy=y[lag:]
 elif lag<0:xx=x[-lag:];yy=y[:lag]
 else:xx=x;yy=y
 correlation=float(np.corrcoef(xx,yy)[0,1]);assert correlation>.98 and abs(lag)<=2,(i,lag,correlation)
 r=run(['ffmpeg','-nostdin','-hide_banner','-v','info','-ss',f'{frame/30-1e-6:.9f}','-threads','1','-i',str(S),'-ss',f'{out/30-1e-6:.9f}','-threads','1','-i',str(O),'-filter_complex_threads','1','-filter_complex','[0:v]trim=end_frame=1,setpts=PTS-STARTPTS[a];[1:v]trim=end_frame=1,setpts=PTS-STARTPTS[b];[a][b]ssim','-frames:v','1','-an','-f','null','-'])
 sim=float(re.findall(rb'All:([0-9.]+)',r.stderr)[-1]);assert sim>.98,(i,sim)
 checks.append({'segment':i,'source_frame':frame,'output_frame':out,'audio_lag_samples':lag,'audio_correlation':correlation,'picture_similarity':sim})
print('All 13 retained sections match source picture/audio timing.',flush=True)
levels=run(['ffmpeg','-nostdin','-hide_banner','-v','info','-threads','2','-i',str(O),'-map','0:a:0','-vn','-filter_threads','1','-af','ebur128=peak=true','-f','null','-']).stderr.decode()
(Q/'audio-full-decode-and-levels.log').write_text(levels)
lufs=float(re.findall(r'I:\s*(-?[0-9.]+) LUFS',levels)[-1]);peak=float(re.findall(r'Peak:\s*(-?[0-9.]+) dBFS',levels)[-1]);assert peak<=-1.0,(lufs,peak)
print(f'Complete audio decode passed: {lufs} LUFS, {peak} dBTP.',flush=True)
def snap(frame,p):run(['ffmpeg','-nostdin','-v','error','-n','-ss',f'{max(0,frame/30-1e-6):.9f}','-threads','1','-i',str(O),'-frames:v','1','-vf','scale=480:-1',str(p)])
for c in P['cuts']:
 start=c['new_join_start_frame'];fade=c['transition_frames']
 snap(start-4,Q/f'cut-{c["number"]:02d}-before.jpg');snap(start+fade+4,Q/f'cut-{c["number"]:02d}-after.jpg')
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',18)
for sheetno in range(2):
 sheet=Image.new('RGB',(960,1800),'#161616');d=ImageDraw.Draw(sheet)
 for row in range(6):
  cut=sheetno*6+row+1
  for col,label in enumerate(['before','after']):
   im=Image.open(Q/f'cut-{cut:02d}-{label}.jpg');sheet.paste(im,(col*480,row*300+30));d.text((col*480+8,row*300+5),f'Cut {cut:02d}: {label} dissolve',font=font,fill='white')
 sheet.save(Q/f'join-picture-sheet-{sheetno+1}.jpg',quality=92)
for label,frame in [('hook',30),('intro',300),('covered-beginning',421),('covered-ending',P['total_frames']-324),('outro',P['total_frames']-200)]:snap(frame,Q/f'kept-{label}.jpg')
with O.open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
report={'duration_seconds':P['duration_seconds'],'frames':P['total_frames'],'bytes':O.stat().st_size,'sha256':sha,'av_start_seconds':[0,0],'av_duration_seconds':[float(v['duration']),float(a['duration'])],'chapters_checked':len(chap),'audio_full_decode_passed':True,'integrated_lufs':lufs,'true_peak_dbtp':peak,'source_transfer_checks':checks,'caption_cues':len(json.loads((H/'retimed-caption-cues.json').read_text())),'picture_sheets_created':True,'status':'numerical checks passed; sampled picture review pending; host listening pending'}
with (Q/'integrity-checks.json').open('x') as f:json.dump(report,f,indent=2);f.write('\n')
print('Integrity and review samples saved.',flush=True)
