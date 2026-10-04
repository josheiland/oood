from pathlib import Path
import subprocess,json,concurrent.futures
R=Path(__file__).resolve().parent; D=R/'source-review/chunks';D.mkdir(exist_ok=False)
source=R/'source-review/source-audio-16k.wav';length=4224.532;stride=300
jobs=[]
for k,start in enumerate(range(0,4225,stride)):
 p=D/f'chunk-{k:02}.wav';n=min(stride,length-start)
 subprocess.run(['ffmpeg','-v','error','-n','-ss',str(start),'-i',str(source),'-t',str(n),str(p)],check=True)
 jobs.append((k,start,n,p))
def one(job):
 k,start,n,p=job;out=D/f'chunk-{k:02}'
 with (D/f'chunk-{k:02}.log').open('x') as log:
  subprocess.run(['whisper-cli','-m','/Users/je/.cache/whisper-cpp/ggml-small.en.bin','-f',str(p),'-ng','-t','4','-bs','1','-bo','1','-l','en','-ojf','-osrt','-otxt','-of',str(out)],stdout=log,stderr=log,check=True)
 print(f'Completed source section {k+1}/{len(jobs)}: {start/60:.0f}–{(start+n)/60:.1f} minutes',flush=True)
 return k,start,json.loads(out.with_suffix('.json').read_text())
results=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
 for result in pool.map(one,jobs):results.append(result)
segments=[]
for k,start,j in results:
 for s in j['transcription']:
  a={'start':start+s['offsets']['from']/1000,'end':start+s['offsets']['to']/1000,'text':s['text'].strip(),'chunk':k,'tokens':s.get('tokens',[])}
  for tok in a['tokens']:
   if 'offsets' in tok:tok['offsets']={key:value+int(start*1000) for key,value in tok['offsets'].items()}
  segments.append(a)
(R/'source-review/transcript-full.json').write_text(json.dumps({'engine':'local whisper.cpp small.en; CPU; five-minute chunks; machine draft','segments':segments},indent=2))
(R/'source-review/transcript-full.txt').write_text('\n'.join(f"[{s['start']:08.2f}–{s['end']:08.2f}] {s['text']}" for s in segments)+'\n')
print('Full source transcript complete',flush=True)
