from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import re,os
ROOT='/Users/je/oood'
class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=ROOT,**kw)
 def send_head(self):
  self.remaining=None
  path=Path(self.translate_path(self.path))
  if not path.is_file():return super().send_head()
  f=path.open('rb');size=path.stat().st_size;start=0;end=size-1;status=200
  v=self.headers.get('Range')
  if v:
   m=re.fullmatch(r'bytes=(\d*)-(\d*)',v)
   if m:
    if m[1]:start=int(m[1]);end=min(size-1,int(m[2]) if m[2] else size-1)
    elif m[2]:start=max(0,size-int(m[2]))
    if start>=size or end<start:
     f.close();self.send_error(416);return None
    status=206
  self.send_response(status);self.send_header('Content-Type',self.guess_type(str(path)));self.send_header('Accept-Ranges','bytes');self.send_header('Content-Length',str(end-start+1))
  if status==206:self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
  self.end_headers();f.seek(start);self.remaining=end-start+1;return f
 def copyfile(self,src,dst):
  if self.remaining is None:return super().copyfile(src,dst)
  left=self.remaining
  try:
   while left:
    block=src.read(min(1024*1024,left))
    if not block:break
    dst.write(block);left-=len(block)
  except (BrokenPipeError,ConnectionResetError):pass
 def log_message(self,*a):pass
ThreadingHTTPServer(('127.0.0.1',8769),Handler).serve_forever()
