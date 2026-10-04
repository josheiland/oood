"""Mask the phone screen and finish the actual covered-lens gesture; preserve v3 audio exactly."""
from pathlib import Path
import json,copy,subprocess,csv
R=Path(__file__).resolve().parent;O=json.loads((R/'edit-manifest-v3.json').read_text());M=copy.deepcopy(O)
assert not (R/'edit-manifest-v4.json').exists()
phone=next(s for s in M['segments'] if s['id']=='s025');a=phone['timeline_in'];b=a+5.5
last=next(s for s in M['segments'] if s['id']=='s039');card=M['segments'][-1];extra=15
cover={'id':'s039b','source':M['source'],'source_start_frame':last['source_end_frame'],'source_end_frame':last['source_end_frame']+extra,'in':last['out'],'out':last['out']+extra/30,'frames':extra,'kind':'covered-transition','timeline_in':last['timeline_out'],'timeline_out':last['timeline_out']+extra/30,'reason':'Continue actual hand-cover gesture to a fully covered lens. First 0.5 seconds of existing outro music play under this picture; no added host speech.','audio_source':'Existing v3 outro music; exact AAC packets preserved.'}
card['timeline_in']+=extra/30;card['in']+=extra/30;card['source_start_frame']+=extra;card['frames']-=extra;card['reason']+=' v4: recurring card begins after the fully covered camera frame; music still starts at the original v3 time.'
M['segments'].insert(-1,cover)
M['output_file']='agents-proposed-cut-v4.mp4';M['status']='Proposed for host review; v4 is current. Earlier work renders are superseded; v2 is incomplete.'
M['picture_finishing']={'phone_mask':{'source_in':phone['in'],'source_out':phone['in']+5.5,'output_in':a,'output_out':b,'region':[980,700,280,380],'method':'20-pixel blocks; mask the message-list screen and nearby hand, never host faces.'},'closing_cover':cover,'audio':'All original v3 AAC packets copied without re-encoding. Music begins 0.5s before the outro card, under the actual closing hand cover.'}
(R/'edit-manifest-v4.json').write_text(json.dumps(M,indent=2)+'\n')
with (R/'edit-decision-list-v4.csv').open('x') as f:
 w=csv.writer(f);w.writerow(['id','kind','source','source_start_frame','source_end_frame','timeline_in','timeline_out','frames','reason'])
 for s in M['segments']:w.writerow([s.get(k,'') for k in ['id','kind','source','source_start_frame','source_end_frame','timeline_in','timeline_out','frames','reason']])
W=R/'work/picture-finish-v4';W.mkdir(exist_ok=False);dst=R/M['output_file'];assert not dst.exists()
graph=f'''[0:v:0]split=2[base][patch];
[patch]crop=280:380:980:700,scale=14:19:flags=area,scale=280:380:flags=neighbor[mask];
[base][mask]overlay=x=980:y=700:enable='between(t,{a},{b})',trim=end_frame={round(last['timeline_out']*30)},settb=1/30000,setpts=N*1000[v0];
[1:v:0]fps=30,trim=end_frame=15,settb=1/30000,setpts=N*1000[v1];
[2:v:0]fps=30,scale=1920:1080:out_color_matrix=bt709:out_range=tv,format=yuv420p,trim=end_frame={card['frames']},settb=1/30000,setpts=N*1000[v2];
[v0][v1][v2]concat=n=3:v=1:a=0,settb=1/30000,setpts=N*1000,setsar=1,format=yuv420p,setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709[vout]'''
(W/'filtergraph.txt').write_text(graph)
args=['ffmpeg','-nostdin','-hide_banner','-n','-v','warning','-threads','4','-i',str(R/O['output_file']),'-ss',str(cover['in']),'-t','0.5','-threads','1','-an','-i',M['source'],'-loop','1','-framerate','30','-t',str(card['frames']/30),'-i',card['still'],'-filter_complex_threads','2','-filter_complex_script',str(W/'filtergraph.txt'),'-map','[vout]','-map','0:a:0','-map_metadata','0','-map_chapters','0','-frames:v',str(M['total_frames']),'-r','30','-fps_mode','cfr','-c:v','libx264','-threads','8','-preset','veryfast','-crf','18','-profile:v','high','-level:v','4.0','-pix_fmt','yuv420p','-bf','0','-g','30','-sc_threshold','0','-color_range','tv','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-video_track_timescale','30000','-c:a','copy','-use_editlist','0','-movflags','+faststart','-progress',str(W/'render-progress.log'),str(dst)]
(W/'render-command.json').write_text(json.dumps(args,indent=2)+'\n')
with (W/'render.log').open('x') as f:p=subprocess.run(args,stdout=f,stderr=f)
assert p.returncode==0,(W/'render.log')
print('Rendered current v4',M['duration'],'seconds; audio unchanged.',flush=True)
