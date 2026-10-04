from pathlib import Path
import json,hashlib,urllib.request
from concurrent.futures import ThreadPoolExecutor
ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
CACHE=Path('/var/folders/08/r25vwn091vl6gksxb2nssyz40000gn/T/composio')
TARGETS=[('1fycZY0Em45E8XyCIYdAwifX-cq6P0wEj',HERE/'inputs/episode-001-published.mp4','181624da06b3255f393fb3dbbe36bfe9f154e9c83fef32fcb5a9ebb6aeb3e87d'),('1z1Zdo2TLCzsOCx2oRYdi83cI9YeGGhE_',HERE/'inputs/episode-001-original-raw.mp4','9f58d3a39c91ce4499fd3215355ddc9873051e6e32a5b26a6c73ce05caf93107'),('17AmIjcA2hbtamuGWVJSkVYIUGOrLiskU',ROOT/'E002-make-ai-useful/edit/codex-no-popups-audit-2026-10-03/episode-002-published.mp4','2d0de694425b1e13523a6a52a4895a1accb994d7b763434f7838b7c53753e858')]
entries=sorted(CACHE.rglob('GOOGLEDRIVE_DOWNLOAD_FILE_OUTPUT_*.json'),key=lambda p:p.stat().st_mtime,reverse=True)
def download(item):
 id,path,sha=item
 assert not path.exists(),path
 url=None
 for entry in entries:
  result=json.loads(entry.read_text());data=result.get('data',result)
  if data.get('id')==id and data.get('downloaded_file_content'):
   url=data['downloaded_file_content']['s3url'];break
 if not url:raise ValueError('No task download response found for '+id)
 path.parent.mkdir(parents=True,exist_ok=True)
 with urllib.request.urlopen(url,timeout=90) as response,path.open('xb') as f:
  while chunk:=response.read(4*1024*1024):f.write(chunk)
 with path.open('rb') as f:actual=hashlib.file_digest(f,'sha256').hexdigest()
 assert actual==sha,(path,actual)
 print(json.dumps({'path':str(path),'bytes':path.stat().st_size,'sha256_verified':True}),flush=True)
with ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(download,TARGETS))
