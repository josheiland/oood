import importlib.util,json,pathlib
H=pathlib.Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('renderer',H.parent/'render-review.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
for o in json.loads((H/'comparison-manifest.json').read_text())['options']:
 r.render(o['segments'],H/o['file'],H/'work'/o['file'].removesuffix('.mp4'))
