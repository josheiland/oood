from pathlib import Path
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from urllib.parse import unquote,urlparse
import mimetypes,re,json
R=Path(__file__).resolve().parent
SOURCE=Path('/Users/je/Movies/Agents episode.mp4')
class Handler(BaseHTTPRequestHandler):
 def do_HEAD(self):self.send_file(False)
 def do_GET(self):self.send_file(True)
 def log_message(self,*args):pass
 def send_file(self,body):
  uri=unquote(urlparse(self.path).path).lstrip('/') or 'review.html'
  if uri=='source.mp4':p=SOURCE
  elif uri=='fact-check.md':p=R.parents[3]/'02_RESEARCH/codex-agents-recording-fact-check-2026-10-03.md'
  else:
   p=(R/uri).resolve()
   if not p.is_relative_to(R):self.send_error(404);return
  if not p.is_file():self.send_error(404);return
  size=p.stat().st_size;start=0;end=size-1;code=200;value=self.headers.get('Range')
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
url=f'http://127.0.0.1:{server.server_port}/review.html'
(R/'review-server.json').write_text(json.dumps({'url':url,'local_only':True,'source_read_only':str(SOURCE)},indent=2)+'\n')
print(url,flush=True);server.serve_forever()
