#!/usr/bin/env python3
"""Render brand-accurate static OOOD cards. Requires Pillow and Teachers variable TTF."""
import argparse
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

COLORS = {'blue':'#38B6FF', 'cream':'#FBF1E5', 'foam':'#FDF8F2', 'navy':'#0B2A45'}

def font(path, size, weight):
    f = ImageFont.truetype(str(path), size)
    try:
        f.set_variation_by_axes([weight])
    except (OSError, AttributeError) as e:
        raise ValueError('Supply the Teachers variable font; do not substitute a static font silently') from e
    return f

def wrap(draw, text, f, width):
    lines = []
    for paragraph in text.splitlines():
        line = ''
        for word in paragraph.split():
            if draw.textlength(word, font=f) > width:
                raise ValueError('A word is too wide; shorten the copy')
            candidate = (line + ' ' + word).strip()
            if line and draw.textlength(candidate, font=f) > width:
                lines.append(line); line = word
            else:
                line = candidate
        if line: lines.append(line)
    return lines

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--kind', choices=['popup','chapter'], default='popup')
    p.add_argument('--title', required=True)
    p.add_argument('--body', default='')
    p.add_argument('--font', required=True, type=Path)
    p.add_argument('--out', required=True, type=Path)
    a = p.parse_args()
    if a.out.exists() or a.out.with_suffix('.json').exists(): p.error('Use a new output path')
    if not a.font.is_file(): p.error('Teachers font not found')
    im = Image.new('RGBA',(1920,1080),(0,0,0,0)); d=ImageDraw.Draw(im)
    if a.kind == 'popup':
        x,y,w,h=96,705,1220,250
        d.rectangle((x,y,x+w,y+h), fill=COLORS['cream'])
        d.rectangle((x,y+int(h*.59),x+w,y+h), fill=COLORS['foam'])
        d.rectangle((x,y,x+10,y+h),fill=COLORS['blue'])
        title_font=font(a.font,52,800);body_font=font(a.font,38,400)
        titles=wrap(d,a.title.upper(),title_font,w-88)
        body=wrap(d,a.body,body_font,w-88)
        if len(titles)>1 or len(body)>2: p.error('Popup supports one short title and two body lines; shorten copy')
        if titles: d.text((x+40,y+25),titles[0],font=title_font,fill=COLORS['navy'])
        for i,line in enumerate(body): d.text((x+40,y+101+i*47),line,font=body_font,fill=COLORS['navy'])
    else:
        d.rectangle((0,0,1920,1080), fill=COLORS['cream'])
        d.rectangle((0,637,1920,1080), fill=COLORS['foam'])
        title_font=font(a.font,140,800);body_font=font(a.font,44,400)
        titles=wrap(d,a.title.upper(),title_font,1680);body=wrap(d,a.body,body_font,1600)
        if len(titles)>2 or len(body)>2: p.error('Chapter copy is too long')
        top=530 if len(titles)==1 else 385
        for i,line in enumerate(titles):d.text((120,top+i*145),line,font=title_font,fill=COLORS['blue'])
        for i,line in enumerate(body):d.text((125,745+i*55),line,font=body_font,fill=COLORS['navy'])
    a.out.parent.mkdir(parents=True,exist_ok=True)
    im.save(a.out)
    spec={'kind':a.kind,'title':a.title,'body':a.body,'font':str(a.font.resolve()),'size':[1920,1080],'static_only':True,'colors':COLORS,'note':'Check over actual footage and animate in the edit if applicable.'}
    a.out.with_suffix('.json').write_text(json.dumps(spec,indent=2)+'\n')
    print(a.out)

if __name__=='__main__':main()
