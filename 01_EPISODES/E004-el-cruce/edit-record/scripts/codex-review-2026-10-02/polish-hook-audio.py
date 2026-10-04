from pathlib import Path
import json,subprocess,math
R=Path(__file__).resolve().parent;dest=R/'hooks-v2';dest.mkdir(exist_ok=True)
for p in sorted((R/'hooks').glob('*.mp4')):
 d=json.loads((R/'qc'/f'{p.stem}-report.json').read_text());out=dest/p.name;assert not out.exists()
 gain=-16-d['integrated_lufs'];dur=d['duration'];af=f'aresample=192000,volume={gain}dB,alimiter=limit={10**(-2.5/20)}:level=false:latency=true,aresample=48000,apad=whole_dur={dur},atrim=duration={dur},asetpts=N/SR/TB'
 cmd=['ffmpeg','-hide_banner','-nostdin','-n','-i',str(p),'-map','0:v:0','-map','0:a:0','-map_metadata','0','-map_chapters','0','-c:v','copy','-af',af,'-c:a','aac','-b:a','256k','-ar','48000','-bsf:a',r'noise=drop=lt(pts\,0)','-use_editlist','0','-movflags','+faststart',str(out)]
 with (R/'qc'/f'{p.stem}-audio-polish.log').open('w') as log:subprocess.run(cmd,stdout=log,stderr=log,check=True)
 print(out.name,flush=True)
