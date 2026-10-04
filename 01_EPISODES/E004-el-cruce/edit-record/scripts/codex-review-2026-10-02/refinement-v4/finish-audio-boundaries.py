from pathlib import Path
import copy,json,subprocess
H=Path(__file__).resolve().parent
m=json.loads((H/'edit-manifest-v4-tightened.json').read_text())
edges=[]
for s in m['segments']:
 if s['id']=='v4-002':s['audio_out']=74.73333333333333
 if s['id']=='v4-013':s['audio_out']=748.1333333333333
 if 'audio_out' in s:
  silence=s['out']-s['audio_out'];a=s['timeline_out']-silence;b=s['timeline_out']
  s['audio_tail_silence']=silence
  s['reason']+=' Audio ends at the preceding waveform gap; two quiet frames preserve the picture timeline without the next sentence’s first sound.'
  edges.append((a,b))
m['output_file']='refinement-v4/el-cruce-refined-v4.mp4'
p=H/'edit-manifest-v4-final.json'
if p.exists():raise FileExistsError(p)
p.write_text(json.dumps(m,indent=2)+'\n')
duration=m['duration'];bounds=[0]+[x for e in edges for x in e]+[duration]
filters=[]
for i,(a,b) in enumerate(zip(bounds,bounds[1:])):
 dur=b-a
 if i%2:
  filters.append(f'anullsrc=r=48000:cl=stereo,atrim=duration={dur},asetpts=N/SR/TB[p{i}]')
 else:
  f=f'[0:a:0]atrim=start={a}:end={b},asetpts=PTS-STARTPTS'
  if i<len(bounds)-2:f+=f',afade=t=out:st={max(0,dur-.008)}:d=0.008'
  filters.append(f+'[p'+str(i)+']')
filters.append(''.join(f'[p{i}]' for i in range(len(bounds)-1))+f'concat=n={len(bounds)-1}:v=0:a=1,aresample=48000,apad=whole_dur={duration},atrim=duration={duration},asetpts=N/SR/TB[a]')
cmd=['ffmpeg','-nostdin','-hide_banner','-n','-i',str(H/'el-cruce-proposed-cut-v4-tightened.mp4'),'-filter_complex',';'.join(filters),'-map','0:v:0','-map','[a]','-map_metadata','0','-map_chapters','0','-c:v','copy','-c:a','aac','-b:a','320k','-ar','48000','-bsf:a','noise=drop=lt(pts\\,0)','-use_editlist','0','-movflags','+faststart',str(H/'el-cruce-refined-v4.mp4')]
with (H/'audio-boundary-finish.log').open('w') as f:subprocess.run(cmd,stdout=f,stderr=f,check=True)
print('Finished current review master; video preserved, two 66.7ms speech-edge trims',flush=True)
