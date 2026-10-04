from pathlib import Path
from html.parser import HTMLParser
import json,re,subprocess,urllib.request,urllib.parse

R=Path(__file__).resolve().parent
D=R/'feedback-revision-v5'
url=json.loads((R/'review-server.json').read_text())['url']
base=urllib.parse.urljoin(url,'feedback-revision-v5/review.html')
Q=json.loads((D/'qc/summary.json').read_text())
assert Q['passed'] and Q['current_master']=='agents-feedback-cut-v5-audio-matched.mp4'
assert not (D/'qc/review-page-check.json').exists()

class Links(HTMLParser):
    def __init__(self):super().__init__();self.refs=[]
    def handle_starttag(self,tag,attrs):
        self.refs.extend(v for k,v in attrs if k in ('src','href') and v)

page=(D/'review.html').read_text()
parser=Links();parser.feed(page)
refs=set(parser.refs+re.findall(r"url\(['\"]?([^)'\"]+)",page))
checks=[]
for ref in sorted(refs):
    target=urllib.parse.urljoin(base,ref)
    assert urllib.parse.urlparse(target).netloc=='127.0.0.1:55648'
    request=urllib.request.Request(target,headers={'Range':'bytes=0-1023'})
    with urllib.request.urlopen(request,timeout=20) as response:
        b=response.read(1024)
        assert b and response.status in (200,206)
        if ref.endswith('.mp4'):
            assert response.status==206 and 'ftyp' in b[:80].decode('latin1')
        checks.append(dict(reference=ref,status=response.status,bytes_sampled=len(b)))
js=re.search(r'<script>(.*?)</script>',page,re.S).group(1)
script=D/'qc/review-page-script.js';assert not script.exists();script.write_text(js+'\n')
subprocess.run(['node','--check',str(script)],check=True,capture_output=True)
assert 'range(\'old\'' in page and 'range(\'main\'' in page
assert 'agents-selected-opening-v5-audio-matched.mp4' in page
assert page.count('<article>')==4
(D/'review-server.json').write_text(json.dumps(dict(url=base,local_only=True,source_read_only='/Users/je/Movies/Agents episode.mp4'),indent=2)+'\n')
(D/'qc/review-page-check.json').write_text(json.dumps(dict(passed=True,url=base,links=checks,javascript_syntax='passed',before_after_pairs=4),indent=2)+'\n')
print('Private review page, all file links, four before/after controls and video range requests passed.',flush=True)
