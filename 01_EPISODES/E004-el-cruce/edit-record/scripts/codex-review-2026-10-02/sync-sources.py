import json,subprocess,pathlib,numpy as np
root=pathlib.Path(__file__).parent
inv=json.loads((root/'source-review/inventory.json').read_text())
screens=json.loads((root/'source-review/screens-inventory.json').read_text())
def sample(p,t,d):
 b=subprocess.check_output(['ffmpeg','-nostdin','-v','error','-ss',str(t),'-i',p,'-t',str(d),'-map','0:a:0','-ac','1','-ar','2000','-f','f32le','-'])
 return np.frombuffer(b,np.float32)
results=[]
for c in inv:
 name=pathlib.Path(c['path']).stem[-8:].replace('-','')
 if name=='091614':continue
 sc=next(s for s in screens if ('9.36' if name=='093614' else '2.21' if name=='142133' else '2.51') in s['path'])
 item={'camera':c['path'],'screen':sc['path'],'samples':[]}
 dur=float(c['format']['duration'])
 for t in [60,dur/2,dur-100]:
  a=sample(c['path'],t,25).astype(float);b=sample(sc['path'],t-25,75).astype(float)
  a-=a.mean();b-=b.mean()
  n=1<<int(np.ceil(np.log2(len(a)+len(b))))
  corr=np.fft.irfft(np.fft.rfft(b,n)*np.fft.rfft(a[::-1],n),n)[len(a)-1:len(b)]
  energies=np.convolve(b*b,np.ones(1))
  cum=np.r_[0,np.cumsum(energies)]
  den=np.sqrt(np.sum(a*a)*(cum[len(a):]-cum[:-len(a)]))
  scores=corr/np.maximum(den,1e-12)
  idx=int(np.argmax(scores))
  item['samples'].append({'camera_time':t,'screen_minus_camera':idx/2000-25,'correlation':float(scores[idx]),'camera_rms':float(np.std(a)),'screen_rms':float(np.std(b))})
 results.append(item)
(root/'source-review/sync-audio-correlation.json').write_text(json.dumps(results,indent=2))
print(json.dumps(results,indent=2))
