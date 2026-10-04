import pathlib,json,subprocess
H=pathlib.Path(__file__).resolve().parent
for c in json.loads((H/'focused-clips-map.json').read_text()):
 p=H/'focused'/c['name'];print(c['name'],flush=True)
 with p.with_suffix('.log').open('w') as f:
  subprocess.run(['whisper-cli','-m','/Users/je/.cache/whisper-cpp/ggml-small.en.bin','-f',str(p.with_suffix('.wav')),'-dtw','small.en','-nfa','-ojf','-otxt','-of',str(p)],stdout=f,stderr=f,check=True)
