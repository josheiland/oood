#!/usr/bin/env python3
from pathlib import Path
import subprocess,json,hashlib,re,sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
BASE=HERE/'inputs/episode-001-published.mp4'
RAW=HERE/'inputs/episode-001-original-raw.mp4'
OUT=HERE/'episode-001-no-popups.mp4'
PLAN=json.loads((HERE/'popup-removal-plan.json').read_text())
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-show_chapters','-of','json',str(p)]))
a,b=probe(BASE),probe(OUT)
assert int(b['streams'][0]['nb_frames'])==94372
assert abs(float(b['format']['duration'])-float(a['format']['duration']))<0.002
assert a['chapters']==b['chapters']
assert b['streams'][0]['width']==1920 and b['streams'][0]['height']==1080
assert b['streams'][0]['has_b_frames']==0
print('Frame count, duration and all chapters match.',flush=True)
def audio_hash(p):
 return subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-map','0:a:0','-c:a','copy','-bsf:a',r'noise=drop=lt(pts\,0)','-f','streamhash','-hash','sha256','-']).decode().strip()
ah,bh=audio_hash(BASE),audio_hash(OUT)
assert ah==bh
print('All nonnegative-time AAC content matches exactly.',flush=True)
subprocess.run(['ffmpeg','-nostdin','-v','error','-i',str(OUT),'-map','0:a:0','-vn','-f','null','-'],check=True)
print('Complete retained audio decodes without errors.',flush=True)
visual=[]
for i,patch in enumerate(PLAN['patches'],1):
 t=patch['final_start_frame']/30;rt=patch['raw_start_frame']/30
 cmd=['ffmpeg','-nostdin','-hide_banner','-v','info','-ss',f'{t-0.000001:.9f}','-threads','4','-i',str(OUT),'-ss',f'{rt-0.000001:.9f}','-threads','4','-i',str(RAW),'-filter_complex_threads','2','-filter_complex','[0:v]setpts=PTS-STARTPTS[a];[1:v]setpts=PTS-STARTPTS[b];[a][b]ssim=stats_file='+str(HERE/f'popup-{i}-frame-similarity.log'),'-frames:v','165','-an','-f','null','-']
 r=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,check=True)
 values=[float(v) for v in re.findall(r'All:([0-9.]+)',(HERE/f'popup-{i}-frame-similarity.log').read_text())]
 assert len(values)==165 and min(values)>0.98,(i,len(values),min(values))
 visual.append({'id':patch['id'],'frames':len(values),'min_similarity_to_original_camera':min(values),'mean_similarity_to_original_camera':sum(values)/len(values)})
 for label,frame in [('first',patch['final_start_frame']),('middle',patch['final_start_frame']+60),('last',patch['final_end_frame']-1),('after',patch['final_end_frame'])]:
  subprocess.run(['ffmpeg','-v','error','-n','-ss',f'{frame/30-0.000001:.9f}','-threads','4','-i',str(OUT),'-frames:v','1',str(HERE/f'popup-{i}-clean-{label}.png')],check=True)
 print('Original camera restored for all 165 frames of '+patch['id'],flush=True)
for label,t in [('hook',1.),('intro',10.),('covered-lens',421/30),('outro',3137.)]:
 subprocess.run(['ffmpeg','-v','error','-n','-ss',f'{t-0.000001:.9f}','-threads','4','-i',str(OUT),'-frames:v','1',str(HERE/f'kept-{label}.png')],check=True)
with OUT.open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
report={'sha256':sha,'duration':b['format']['duration'],'frames':94372,'chapters_identical':True,'audio_full_decode_passed':True,'aac_nonnegative_time_payload_sha256':ah,'restored_picture_checks':visual,'caption_bytes_identical':(HERE/'episode-001-no-popups.srt').read_bytes()==(ROOT/'01_EPISODES/E001-ai-basics/captions.srt').read_bytes()}
assert report['caption_bytes_identical']
with (HERE/'integrity-checks.json').open('x') as f:json.dump(report,f,indent=2);f.write('\n')
print('Running complete coded-header/container/full-frame gate.',flush=True)
r=subprocess.run(['python3',str(ROOT/'skills/oood-episode-producer/scripts/color_qc.py'),str(OUT),'--report',str(HERE/'color-qc.json')],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
if r.returncode:raise RuntimeError(r.stderr+r.stdout[-3000:])
print('Complete export color/container gate passed.',flush=True)
