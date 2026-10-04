#!/usr/bin/env python3
"""Read-only media inventory/QC and a conservative, reproducible baseline episode render."""
import argparse
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
from color_qc import verify as verify_color

def run(args, log=None):
    result=subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    if log: Path(log).write_text(result.stdout+'\n'+result.stderr)
    if result.returncode: raise RuntimeError(f'{args[0]} failed; {result.stderr[-1800:]}')
    return result

def probe(path):
    return json.loads(run(['ffprobe','-v','error','-show_streams','-show_format','-show_chapters','-of','json',str(path)]).stdout)

def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(8*1024*1024),b''):h.update(chunk)
    return h.hexdigest()

def write(path,obj):
    Path(path).write_text(json.dumps(obj,indent=2)+'\n')

def validate(path):
    path=Path(path).resolve();m=json.loads(path.read_text())
    fps=Fraction(str(m.get('fps',30)))
    if fps<=0 or fps>120:raise ValueError('Invalid target fps')
    for k,default in [('width',1920),('height',1080)]:
        value=m.get(k,default)
        if not isinstance(value,int) or isinstance(value,bool):raise ValueError('Dimensions must be integer JSON numbers')
        m[k]=value
        if m[k]<2 or m[k]%2:raise ValueError('Dimensions must be positive even integers')
    if not m.get('segments'):raise ValueError('No segments')
    inventory={};total=0
    for s in m['segments']:
        source=(path.parent/s['source']).resolve()
        if not source.is_file():raise ValueError(f'Missing source: {source}')
        if str(source) not in inventory:inventory[str(source)]=probe(source)
        info=inventory[str(source)];streams=info['streams']
        if not any(t['codec_type']=='video' for t in streams):raise ValueError('No video stream')
        video=next(t for t in streams if t['codec_type']=='video')
        for key,allowed in [('color_range',{'tv','unknown',None}),('color_space',{'bt709','unknown',None}),('color_primaries',{'bt709','unknown',None}),('color_transfer',{'bt709','unknown',None})]:
            if video.get(key) not in allowed:raise ValueError('Baseline SDR renderer requires a real color conversion for this source before encoding; do not relabel different color characteristics')
        if not isinstance(s['audio_stream'],int) or isinstance(s['audio_stream'],bool) or not any(t['index']==s['audio_stream'] and t['codec_type']=='audio' for t in streams):raise ValueError('audio_stream must be an absolute integer audio stream index')
        start=float(s['in']);end=float(s['out']);duration=float(info['format']['duration'])
        if not all(math.isfinite(x) for x in (start,end)) or not 0<=start<end<=duration+0.001:raise ValueError('Invalid/out-of-source range')
        frames=round((end-start)*float(fps))
        if frames<1:raise ValueError('Segment shorter than one frame')
        s.update(source=str(source),frames=frames,timeline_frame=total)
        total+=frames
    m['fps']=str(fps);m['total_frames']=total
    return m,inventory

def ff(args,log):return run(['ffmpeg','-nostdin','-n','-hide_banner','-nostats','-v','info',*args],log)

def stats_from(text):
    matches=re.findall(r'\{[^{}]+\}',text)
    if not matches:raise ValueError('Loudness measurement missing')
    return json.loads(matches[-1])

def qc(path,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=False)
    p=probe(path)
    color=verify_color(path)
    write(out/'color-consistency.json',color)
    if not color['passed']:raise RuntimeError('Video color/container compatibility gate failed; inspect color-consistency.json before handoff')
    ff(['-i',str(path),'-map','0:v:0','-map','0:a:0','-f','null','-'],out/'decode.log')
    a=ff(['-i',str(path),'-vn','-af','loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-'],out/'loudness.log')
    spans=ff(['-i',str(path),'-vf','blackdetect=d=0.1:pix_th=0.05','-af','silencedetect=n=-48dB:d=1.5','-f','null','-'],out/'spans.log')
    black=[{'start':float(x),'end':float(y),'duration':float(z)} for x,y,z in re.findall(r'black_start:([\d.]+) black_end:([\d.]+) black_duration:([\d.]+)',spans.stderr)]
    silence_events=re.findall(r'silence_(start|end): ([\d.]+)',spans.stderr)
    audio=next(s for s in p['streams'] if s['codec_type']=='audio');video=next(s for s in p['streams'] if s['codec_type']=='video')
    duration_delta=abs(float(audio.get('duration',p['format']['duration']))-float(video.get('duration',p['format']['duration'])))
    report={'path':str(Path(path).resolve()),'sha256':sha(path),'probe':p,'color_consistency':color,'loudness':stats_from(a.stderr),'decode_completed':True,'black_spans':black,'silence_events':silence_events,'audio_video_duration_delta':duration_delta,'review_status':'Automated measurements only; inspect flagged spans and listen/watch before approval. Duration agreement does not prove original camera lip sync or packet continuity.'}
    write(out/'report.json',report)
    return report

def metadata_escape(s):return str(s).replace('\\','\\\\').replace('\n',' ').replace('=','\\=').replace(';','\\;').replace('#','\\#')

def render(manifest,out):
    m,inventory=validate(manifest);out=Path(out).resolve();out.mkdir(parents=True,exist_ok=False)
    fps=float(Fraction(m['fps']));duration=m['total_frames']/fps
    write(out/'resolved-edit.json',m)
    before={s:sha(s) for s in inventory};write(out/'source-hashes.json',before)
    clips=[]
    for i,s in enumerate(m['segments']):
        clip=out/f'segment-{i:03d}.mov';dur=s['frames']/fps;start=float(s['in']);end=start+dur
        vf=f"[0:v:0]trim=start={start}:end={end},setpts=PTS-STARTPTS,fps={m['fps']},scale={m['width']}:{m['height']}:force_original_aspect_ratio=decrease,pad={m['width']}:{m['height']}:(ow-iw)/2:(oh-ih)/2,setsar=1,tpad=stop_mode=clone:stop_duration=0.1,trim=end_frame={s['frames']},setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709[v]"
        ramp=min(.008,dur/4)
        af=f"[0:{s['audio_stream']}]atrim=start={start}:end={end},asetpts=PTS-STARTPTS,aresample=48000,apad=whole_dur={dur},atrim=duration={dur},afade=t=in:d={ramp},afade=t=out:st={dur-ramp}:d={ramp}[a]"
        ff(['-i',s['source'],'-filter_complex',vf+';'+af,'-map','[v]','-map','[a]','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-color_range','tv','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-c:a','pcm_s24le','-ac','2','-ar','48000','-t',str(dur),str(clip)],out/f'segment-{i:03d}.log')
        clips.append(clip)
    # Generated safe relative filenames avoid shell/concat quoting of arbitrary source paths.
    concat=out/'concat.txt';concat.write_text(''.join(f"file '{p.name}'\n" for p in clips))
    concat_args=['-f','concat','-safe','1','-i',str(concat)]
    a=ff([*concat_args,'-vn','-af','loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-'],out/'loudness-pass1.log')
    stats=stats_from(a.stderr)
    if not all(math.isfinite(float(stats[k])) for k in ['input_i','input_tp','input_lra','input_thresh','target_offset']):raise ValueError('Invalid loudness: inspect silent or broken audio')
    filt=f"loudnorm=I=-16:TP=-1.5:LRA=11:measured_I={stats['input_i']}:measured_TP={stats['input_tp']}:measured_LRA={stats['input_lra']}:measured_thresh={stats['input_thresh']}:offset={stats['target_offset']}:linear=true,atrim=duration={duration},asetpts=N/SR/TB"
    audio=out/'master-audio.wav'
    ff([*concat_args,'-vn','-af',filt,'-ar','48000','-c:a','pcm_s24le',str(audio)],out/'audio-master.log')
    meta=[';FFMETADATA1','title='+metadata_escape(m.get('title','Out of Our Depth')),'comment=Host review pending']
    chapters=[s for s in m['segments'] if s.get('chapter')]
    for i,s in enumerate(chapters):
        end=chapters[i+1]['timeline_frame'] if i+1<len(chapters) else m['total_frames']
        meta+=['[CHAPTER]','TIMEBASE=1/1000',f"START={round(s['timeline_frame']/fps*1000)}",f'END={round(end/fps*1000)}','title='+metadata_escape(s['chapter'])]
    (out/'chapters.ffmeta').write_text('\n'.join(meta)+'\n')
    master=out/'episode-master.mp4'
    # A single final encoder session removes changing segment configurations.
    # No B-frame delay or MP4 edit lists; discard AAC's negative-time priming packet.
    final_vf=f"setpts=N/({m['fps']}*TB),setsar=1,format=yuv420p,setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709"
    ff([*concat_args,'-i',str(audio),'-i',str(out/'chapters.ffmeta'),'-map','0:v:0','-map','1:a:0','-map_metadata','2','-map_chapters','2','-vf',final_vf,'-c:v','libx264','-preset','fast','-crf','18','-threads','4','-bf','0','-g',str(round(fps)),'-sc_threshold','0','-r',m['fps'],'-fps_mode','cfr','-color_range','tv','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-c:a','aac','-b:a','256k','-bsf:a','noise=drop=lt(pts\\,0)','-use_editlist','0','-movflags','+faststart',str(master)],out/'mux.log')
    report=qc(master,out/'qc')
    v=next(s for s in report['probe']['streams'] if s['codec_type']=='video')
    frames=int(v['nb_frames']);actual=float(v['duration'])
    actual_chapters=report['probe'].get('chapters',[])
    chapters_match=len(actual_chapters)==len(chapters) and all(c.get('tags',{}).get('title')==s['chapter'] and abs(float(c['start_time'])-s['timeline_frame']/fps)<=.002 for c,s in zip(actual_chapters,chapters))
    checks={'frames_match':frames==m['total_frames'],'duration_match':abs(actual-duration)<=1/fps,'chapters_match':chapters_match,'audio_video_durations_match':report['audio_video_duration_delta']<=max(.05,1/fps),'source_hashes_unchanged':all(sha(s)==h for s,h in before.items()),'true_peak_within_target':float(report['loudness']['input_tp'])<=-1.0,'integrated_loudness_within_1_lu':abs(float(report['loudness']['input_i'])+16)<=1}
    write(out/'render-checks.json',checks)
    print(json.dumps({'master':str(master),'checks':checks,'status':'Complete baseline render; editorial/graphics/captions and human review remain separate.'},indent=2))
    if not all(checks.values()):raise RuntimeError('One or more measured checks failed; inspect render-checks.json')

def main():
    p=argparse.ArgumentParser(description=__doc__);subs=p.add_subparsers(dest='mode',required=True)
    for name in ['probe','validate','render','qc']:
        s=subs.add_parser(name);s.add_argument('input',type=Path)
        if name!='validate':s.add_argument('--out',required=True,type=Path)
    a=p.parse_args()
    if not all(shutil.which(t) for t in ['ffmpeg','ffprobe']):p.error('ffmpeg and ffprobe required')
    if a.mode=='probe':
        if a.out.exists():p.error('Use a new inventory path')
        write(a.out,{'source':str(a.input.resolve()),'sha256':sha(a.input),'metadata':probe(a.input)})
    elif a.mode=='validate':
        m,_=validate(a.input);print(json.dumps({'segments':len(m['segments']),'total_frames':m['total_frames'],'fps':m['fps']},indent=2))
    elif a.mode=='qc':qc(a.input,a.out)
    else:render(a.input,a.out)

if __name__=='__main__':main()
