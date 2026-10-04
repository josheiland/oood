"""Local-only, explicitly allowlisted review assets with video byte ranges."""
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json,mimetypes,re
from urllib.parse import urlsplit,unquote

Q=Path(__file__).resolve().parent
M=json.loads((Q/'edit-manifest-v10-final.json').read_text())
names=['review-v10.html','el-cruce-personality-v10.mp4','el-cruce-personality-v10.srt','el-cruce-personality-v10.vtt','include-and-cut-notes-v10.md','omitted-transcript-excerpts-v10.md','claims-and-accuracy-review-v10.md','chapters-v10.txt','description-and-chapters-draft-v10.txt','title-and-thumbnail-options.txt','teachers.ttf','README.md','qc-summary-v10.json']
routes={'/'+name:Q/name for name in names};routes['/']=Q/'review-v10.html'
for sid in 'ABC':
    routes[f'/sources/{sid}.mp4']=Path(next(s['source'] for s in M['segments'] if s.get('source_id')==sid))

class Handler(BaseHTTPRequestHandler):
    def do_HEAD(self):self.send_file(False)
    def do_GET(self):self.send_file(True)
    def send_file(self,body):
        path=routes.get(unquote(urlsplit(self.path).path))
        if path is None or not path.is_file():self.send_error(404);return
        size=path.stat().st_size;start,end=0,size-1;partial=False
        request=self.headers.get('Range')
        if request:
            match=re.fullmatch(r'bytes=(\d*)-(\d*)',request)
            if not match or not any(match.groups()):self.send_error(416);return
            a,b=match.groups()
            if a:start=int(a);end=min(int(b),size-1) if b else size-1
            else:start=max(0,size-int(b))
            if start>=size or end<start:self.send_error(416);return
            partial=True
        self.send_response(206 if partial else 200)
        self.send_header('Content-Type',mimetypes.guess_type(path.name)[0] or 'application/octet-stream')
        self.send_header('Content-Length',str(end-start+1));self.send_header('Accept-Ranges','bytes')
        self.send_header('Cache-Control','no-store')
        if partial:self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
        self.end_headers()
        if body:
            try:
                with path.open('rb') as f:
                    f.seek(start);remaining=end-start+1
                    while remaining:
                        data=f.read(min(256*1024,remaining))
                        if not data:break
                        self.wfile.write(data);remaining-=len(data)
            except (BrokenPipeError,ConnectionResetError):pass
    def log_message(self,*args):pass

if __name__=='__main__':
    print('Private episode review: http://127.0.0.1:8772/review-v10.html',flush=True)
    ThreadingHTTPServer(('127.0.0.1',8772),Handler).serve_forever()
