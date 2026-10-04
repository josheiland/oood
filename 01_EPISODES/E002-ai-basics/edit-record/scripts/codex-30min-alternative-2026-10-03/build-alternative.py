#!/usr/bin/env python3
from pathlib import Path
import subprocess,json,hashlib
H=Path(__file__).resolve().parent
P=json.loads((H/'edit-decisions.json').read_text())
S=Path(P['source']);O=H/'episode-001-30min-alternative.mp4'
assert not O.exists()
with S.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==P['source_sha256']
args=['ffmpeg','-nostdin','-hide_banner','-v','warning','-n']
filters=[]
for i,seg in enumerate(P['segments']):
 frames=seg['source_end_frame']-seg['source_start_frame']
 args+=['-ss',f"{seg['source_start_frame']/30:.9f}",'-t',f'{frames/30:.9f}','-threads','1','-i',str(S)]
 filters+=[f'[{i}:v]trim=end_frame={frames},settb=1/30000,setpts=N*1000,format=yuv420p,setsar=1[v{i}]',f'[{i}:a:0]aresample=48000:first_pts=0,atrim=end_sample={frames*1600},asetpts=N/SR/TB[a{i}]']
lastv='v0';lasta='a0'
for i,seg in enumerate(P['segments'][1:],1):
 fade=seg['incoming_transition_frames'];offset=seg['output_start_frame']/30
 filters+=[f'[{lastv}][v{i}]xfade=transition=fade:duration={fade/30:.9f}:offset={offset:.9f}[xv{i}]',f'[{lasta}][a{i}]acrossfade=ns={fade*1600}:c1=tri:c2=tri[xa{i}]']
 lastv=f'xv{i}';lasta=f'xa{i}'
filters+=[f'[{lastv}]format=yuv420p,setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709[vout]',f'[{lasta}]atrim=end_sample={P["total_frames"]*1600},asetpts=N/SR/TB[aout]']
graph=H/'alternative-filtergraph.txt';graph.write_text(';\n'.join(filters)+'\n')
args+=['-f','ffmetadata','-i',str(H/'alternative.ffmeta'),'-filter_complex_threads','2','-filter_complex_script',str(graph),'-map','[vout]','-map','[aout]','-map_metadata',str(len(P['segments'])),'-map_chapters',str(len(P['segments'])),'-frames:v',str(P['total_frames']),'-r','30','-fps_mode','cfr','-c:v','libx264','-threads','4','-preset','veryfast','-crf','18','-profile:v','high','-level:v','4.0','-pix_fmt','yuv420p','-bf','0','-g','30','-sc_threshold','0','-color_range','tv','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-video_track_timescale','30000','-c:a','aac','-b:a','256k','-ar','48000','-bsf:a',r'noise=drop=lt(pts\,0)','-use_editlist','0','-movflags','+faststart','-progress',str(H/'render-progress.log'),str(O)]
(H/'render-command.json').write_text(json.dumps(args,indent=2)+'\n')
with (H/'render-log.txt').open('x') as f:subprocess.run(args,stdout=f,stderr=f,check=True)
print(O,flush=True)
