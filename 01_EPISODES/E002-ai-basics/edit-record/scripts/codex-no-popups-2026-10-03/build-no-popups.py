#!/usr/bin/env python3
from pathlib import Path
import subprocess,json,hashlib
HERE=Path(__file__).resolve().parent
BASE=HERE/'inputs/episode-001-published.mp4'
RAW=HERE/'inputs/episode-001-original-raw.mp4'
OUT=HERE/'episode-001-no-popups.mp4'
PLAN=json.loads((HERE/'popup-removal-plan.json').read_text())
for source,expected in [(BASE,'181624da06b3255f393fb3dbbe36bfe9f154e9c83fef32fcb5a9ebb6aeb3e87d'),(RAW,'9f58d3a39c91ce4499fd3215355ddc9873051e6e32a5b26a6c73ce05caf93107')]:
 with source.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==expected
assert not OUT.exists()
args=['ffmpeg','-hide_banner','-nostdin','-n','-threads','4','-i',str(BASE)]
for patch in PLAN['patches']:
 args+=['-ss',f"{patch['raw_start_frame']/30:.9f}",'-t',f"{(patch['raw_end_frame']-patch['raw_start_frame'])/30:.9f}",'-threads','4','-i',str(RAW)]
filters=['[0:v]settb=1/30000,setpts=N*1000,format=yuv420p,setsar=1[base]']
last='base'
for index,patch in enumerate(PLAN['patches'],1):
 start=patch['final_start_frame'];end=patch['final_end_frame'];count=end-start
 filters+=[f'[{index}:v]trim=end_frame={count},settb=1/30000,setpts=(N+{start})*1000,format=yuv420p,setsar=1[patch{index}]',f"[{last}][patch{index}]overlay=eof_action=pass:repeatlast=0:shortest=0:format=yuv420:enable='gte(t,{start/30-0.000001:.9f})*lt(t,{end/30-0.000001:.9f})'[repaired{index}]"]
 last=f'repaired{index}'
filters+=[f'[{last}]setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709[vout]']
graph=HERE/'no-popups-filtergraph.txt';graph.write_text(';\n'.join(filters)+'\n')
args+=['-filter_complex_threads','2','-filter_complex_script',str(graph),'-map','[vout]','-map','0:a:0','-map_metadata','0','-map_chapters','0','-frames:v',str(PLAN['total_frames']),'-r','30','-fps_mode','cfr','-c:v','libx264','-threads','4','-preset','veryfast','-crf','17','-profile:v','high','-level:v','4.0','-pix_fmt','yuv420p','-bf','0','-g','30','-sc_threshold','0','-color_range','tv','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-video_track_timescale','30000','-c:a','copy','-bsf:a',r'noise=drop=lt(pts\,0)','-use_editlist','0','-movflags','+faststart','-progress',str(HERE/'render-progress.log'),str(OUT)]
(HERE/'render-command.json').write_text(json.dumps(args,indent=2)+'\n')
with (HERE/'render-log.txt').open('x') as log:subprocess.run(args,stdout=log,stderr=log,check=True)
print(OUT,flush=True)
