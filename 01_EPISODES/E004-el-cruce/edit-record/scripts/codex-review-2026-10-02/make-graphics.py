from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,textwrap
R=Path(__file__).resolve().parent
O=R/'graphics';O.mkdir(exist_ok=True)
FONT='/Users/je/oood/03_ASSETS/brand-fonts/teachers.ttf'
def font(sz,w=600):
 f=ImageFont.truetype(FONT,sz);f.set_variation_by_axes([w]);return f
navy='#0B2A45';blue='#38B6FF';cream='#FBF1E5';foam='#FDF8F2'
data=[
 ('context','GIVE IT CONTEXT','Goals, constraints and real examples beat a generic request.'),
 ('plan','ASK FOR A PLAN','Before it builds, ask what it will do and what it still needs.'),
 ('preferences','SHOW YOUR TASTE','Start with options you like. Ask AI to compare them against your requirements.'),
 ('check','CHECK THE OUTPUT','A polished layout can still contain basic mistakes.'),
 ('logistics','MAKE IT ACTIONABLE','Ask for priorities, deadlines and an output you can actually use.'),
 ('result','DEFINE GOOD ENOUGH','Name the essentials before spending time polishing the details.'),
 ('feedback','GIVE SPECIFIC FEEDBACK','Say what to remove, what to keep and how you will use it.')]
for slug,title,body in data:
 p=O/f'{slug}-layout.png'
 if p.exists():continue
 im=Image.new('RGB',(1920,1080),navy);d=ImageDraw.Draw(im)
 d.rectangle((1232,420,1919,660),fill=cream);d.rectangle((1232,660,1919,1079),fill=foam)
 d.rectangle((1270,460,1880,516),fill=blue);d.text((1290,467),'OUT OF OUR DEPTH',font=font(34,800),fill=navy)
 y=555
 for line in textwrap.wrap(title,19):d.text((1270,y),line,font=font(48,800),fill=navy);y+=55
 y+=30
 for line in textwrap.wrap(body,26):d.text((1270,y),line,font=font(36,600),fill=navy);y+=48
 d.text((1270,1000),'BUILD WITH US',font=font(27,700),fill=navy)
 im.save(p)
 p=O/f'{slug}-popup.png'
 im=Image.new('RGBA',(1920,1080),(0,0,0,0));d=ImageDraw.Draw(im)
 d.rectangle((72,828,1232,929),fill=cream);d.rectangle((72,929,1232,1020),fill=foam)
 d.rectangle((72,828,87,1020),fill=blue)
 d.text((116,845),title,font=font(42,800),fill=navy)
 lines=textwrap.wrap(body,66)
 for i,line in enumerate(lines):d.text((116,913+i*42),line,font=font(33,600),fill=navy)
 im.save(p)
(O/'editable-copy.json').write_text(json.dumps(data,indent=2))
