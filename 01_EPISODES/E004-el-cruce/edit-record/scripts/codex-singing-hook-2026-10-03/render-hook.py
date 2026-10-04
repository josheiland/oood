from pathlib import Path
import os,json,hashlib,subprocess,importlib.util
os.environ['PATH']='/opt/homebrew/bin:'+os.environ.get('PATH','')
H=Path(__file__).resolve().parent;R=H.parent/'codex-review-2026-10-02'
raw=Path('/Users/je/Movies/2026-10-02 09-16-14.mp4');saved=H.parents[1]/'almost cruce hook.mp4'
tail=H/'laugh-tail-0-8s.mov'
cmd=['ffmpeg','-nostdin','-hide_banner','-n','-ss','37','-i',str(raw),'-filter_complex','[0:v:0]trim=duration=0.7,setpts=(PTS-STARTPTS)/0.875,fps=30,trim=duration=0.8,setpts=N/(30*TB),setsar=1,format=yuv420p,setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709[v];[0:a:0]atrim=duration=0.7,asetpts=PTS-STARTPTS,atempo=0.875,aresample=48000,apad=whole_dur=0.8,atrim=duration=0.8,asetpts=N/SR/TB[a]','-map','[v]','-map','[a]','-c:v','libx264','-preset','veryfast','-crf','18','-threads','4','-pix_fmt','yuv420p','-bf','0','-g','30','-color_range','tv','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-c:a','pcm_s16le','-ac','2','-ar','48000','-t','0.8',str(tail)]
with (H/'laugh-tail-render.log').open('w') as f:subprocess.run(cmd,stdout=f,stderr=f,check=True)
segments=[
 {'source':str(raw),'in':28.7,'out':37.0,'reason':'Same picture start as Josh’s saved clip, normal timing through singing/question/probably/NOT.'},
 {'source':str(tail),'in':0,'out':.8,'reason':'Original final 0.7-second laugh stretched to 0.8 seconds without pitch shift; no loop or synthesized reaction.'},
 {'source':str(Path('/Users/je/oood/03_ASSETS/music/oood-sting-5s.wav')),'in':0,'out':158/30,'still':'/Users/je/oood/03_ASSETS/codex-mono-mirrored-3digit/intro-card.png','gain_db':-3,'reason':'Current recurring intro card, tagline and music.'},
 {'source':str(R/'refinement-v4/el-cruce-refined-v4.mp4'),'in':17.6,'out':17.6+569/30,'reason':'Same first 18.967 seconds of the current revised episode body, without the duplicated race introduction.'}
]
cursor=0
for s in segments:s['timeline_in']=cursor;cursor+=round((s['out']-s['in'])*30)/30;s['timeline_out']=cursor
manifest={'status':'Requested shortened singing hook; exact-version laugh timing review pending','saved_reference':str(saved),'saved_sha256':hashlib.file_digest(saved.open('rb'),'sha256').hexdigest(),'saved_intro_begins':8.6,'raw_picture_start':28.7,'audio_alignment_offset':28.7125,'original_hook_duration':8.6,'new_hook_duration':9.1,'extension':.5,'extension_detail':'0.4 seconds of unused real source plus 0.1 seconds from pitch-preserving slowdown of final laugh only','segments':segments,'duration':cursor,'output':'almost-cruce-singing-hook-v1.mp4'}
(H/'hook-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
spec=importlib.util.spec_from_file_location('renderer',R/'render-review.py');renderer=importlib.util.module_from_spec(spec);spec.loader.exec_module(renderer)
renderer.render(segments,H/manifest['output'],H/'render-work')
