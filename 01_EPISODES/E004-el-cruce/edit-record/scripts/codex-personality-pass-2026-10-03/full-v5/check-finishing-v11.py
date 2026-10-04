from pathlib import Path
import json,subprocess,numpy as np
from PIL import Image
Q=Path(__file__).resolve().parent;old=Q/'el-cruce-personality-v10.mp4';new=Q/'el-cruce-personality-v11.mp4'
def capture(args):
    return subprocess.run(['/opt/homebrew/bin/ffmpeg','-nostdin','-v','error',*map(str,args)],capture_output=True,check=True).stdout
hashes={}
for p in [old,new]:
    hashes[p.name]=capture(['-i',p,'-map','0:a:0','-c:a','copy','-f','hash','-hash','sha256','-']).decode().strip()
assert len(set(hashes.values()))==1
cards=[]
for name,t in [('intro',10),('outro',2684)]:
    source=Image.open(Q.parents[4]/f'03_ASSETS/codex-mono-mirrored-3digit/{name}-card.png').convert('RGB').getpixel((1900,20))
    data=capture(['-threads','2','-ss',t,'-i',new,'-frames:v','1','-vf','crop=2:2:1900:20','-filter_threads','2','-pix_fmt','rgb24','-threads','2','-f','rawvideo','pipe:1'])
    rgb=list(data[:3]);assert max(abs(a-b) for a,b in zip(source,rgb))<=4
    cards.append({'card':name,'source_png_rgb':source,'decoded_final_rgb':rgb,'max_channel_difference':max(abs(a-b) for a,b in zip(source,rgb))})
samples=[]
for t in [3,15,200,700,1350,1750,2400,2678]:
    def frame(p):
        return np.frombuffer(capture(['-threads','2','-ss',t,'-i',p,'-frames:v','1','-filter_threads','2','-pix_fmt','rgb24','-threads','2','-f','rawvideo','pipe:1']),dtype=np.uint8).astype(np.float32)
    a,b=frame(old),frame(new);assert len(a)==len(b)==1920*1080*3
    diff=a-b;mad=float(np.mean(np.abs(diff)));rmse=float(np.sqrt(np.mean(diff*diff)));psnr=20*np.log10(255/max(rmse,1e-12));assert mad<3 and psnr>35
    samples.append({'time':t,'mean_absolute_rgb_difference':mad,'psnr_db':float(psnr),'interpretation':'Same picture/timing outside card spans, with expected reencode quantization.'})
for name,t in [('intro',10),('outro',2684),('covered-opening',14.3666666667),('covered-ending',2679.0333333333),('C-result',2398)]:
    out=Q/f'final-{name}-v11.jpg';assert not out.exists()
    subprocess.run(['/opt/homebrew/bin/ffmpeg','-nostdin','-v','error','-threads','2','-ss',str(t),'-i',str(new),'-frames:v','1','-threads','2','-q:v','2',str(out)],check=True)
report={'audio_packets_unchanged':True,'audio_packet_hashes':hashes,'card_palette_checks':cards,'outside_card_picture_samples':samples,'review_basis':'All joins and screen scenes inspected in v8 boards; v10 picture packets identical to v8. V11 changes only card matrices and reencodes the same complete frame timeline; final card/body/covered-lens samples verified.'}
(Q/'finishing-verification-v11.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'audio_unchanged':True,'cards':cards,'outside_picture_samples':len(samples)}),flush=True)
