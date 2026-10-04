from pathlib import Path
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from urllib.parse import unquote,urlparse
import mimetypes,re
H=Path(__file__).resolve().parent
MASTER=H.parent/'codex-no-popups-2026-10-03/episode-001-no-popups.mp4'
FILES={f'/{H.name}/{n}':H/n for n in ['review.html','episode-001-30min-alternative.mp4','teachers.ttf','episode-001-30min-alternative.vtt','episode-001-30min-alternative.srt','removed-footage.md','removed-material-transcript.txt']}
FILES[f'/{MASTER.parent.name}/{MASTER.name}']=MASTER
class Handler(BaseHTTPRequestHandler):
 def do_HEAD(self):self.send_file(False)
 def do_GET(self):self.send_file(True)
 def log_message(self,*args):pass
 def send_file(self,body):
  uri=unquote(urlparse(self.path).path)
  if uri=='/':uri=f'/{H.name}/review.html'
  p=FILES.get(uri)
  if p is None or not p.is_file():self.send_error(404);return
  size=p.stat().st_size;start=0;end=size-1;code=200
  value=self.headers.get('Range')
  if value:
   match=re.fullmatch(r'bytes=(\d*)-(\d*)',value)
   if not match:self.send_error(416);return
   a,b=match.groups()
   if a:start=int(a);end=min(end,int(b)) if b else end
   elif b:start=max(0,size-int(b))
   if start>end or start>=size:self.send_error(416);return
   code=206
  self.send_response(code);self.send_header('Content-Type',mimetypes.guess_type(p.name)[0] or 'application/octet-stream');self.send_header('Content-Length',str(end-start+1));self.send_header('Accept-Ranges','bytes');self.send_header('Cache-Control','no-cache')
  if code==206:self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
  self.end_headers()
  if body:
   try:
    with p.open('rb') as f:
     f.seek(start);left=end-start+1
     while left:
      chunk=f.read(min(262144,left))
      if not chunk:break
      self.wfile.write(chunk);left-=len(chunk)
   except (BrokenPipeError,ConnectionResetError):pass
server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
print(f'http://127.0.0.1:{server.server_port}/{H.name}/review.html',flush=True)
server.serve_forever()
