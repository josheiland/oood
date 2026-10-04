#!/usr/bin/env python3
"""Render Mary's paired-host thumbnail with editable, native Teachers text."""

import argparse
import base64
import html
import json
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps, features

HERE = Path(__file__).resolve().parent
FONT = HERE.parent / "brand-fonts" / "teachers.ttf"
W, H = 2560, 1440
BLUE = "#45AEF0"   # sampled from Mary's supplied tile
NAVY = "#0D2843"   # sampled from Mary's supplied title strip
CREAM = "#F2E8DE"  # sampled from Mary's supplied lettering
TILE = (103, 88, 613, 596)
STRIP = (103, 1166, 1221, 1339)


def teacher(size):
    engine = ImageFont.Layout.RAQM if features.check_feature("raqm") else ImageFont.Layout.BASIC
    face = ImageFont.truetype(str(FONT), size, layout_engine=engine)
    face.set_variation_by_axes([800])
    return face


def draw_top(draw, xy, value, face, color):
    x, top = xy
    y = top - face.getbbox(value)[1]
    draw.text((x, y), value, font=face, fill=color)


def fit_title(draw, value):
    for size in range(92, 59, -1):
        face = teacher(size)
        if draw.textlength(value, font=face) <= 1040:
            return face
    raise ValueError("Title is too long for Mary's single-line strip; shorten the copy")


def svg(photo_bytes, title, title_size):
    jpg = base64.b64encode(photo_bytes).decode("ascii")
    font = base64.b64encode(FONT.read_bytes()).decode("ascii")
    safe_title = html.escape(title)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img">
  <title>Out of Our Depth thumbnail — {safe_title}</title>
  <style>@font-face{{font-family:Teachers;src:url(data:font/ttf;base64,{font});font-weight:100 900}}</style>
  <image href="data:image/jpeg;base64,{jpg}" x="0" y="0" width="{W}" height="{H}" preserveAspectRatio="xMidYMid slice"/>
  <rect x="{TILE[0]}" y="{TILE[1]}" width="{TILE[2]-TILE[0]}" height="{TILE[3]-TILE[1]}" fill="{BLUE}"/>
  <rect x="{STRIP[0]}" y="{STRIP[1]}" width="{STRIP[2]-STRIP[0]}" height="{STRIP[3]-STRIP[1]}" fill="{NAVY}"/>
  <g font-family="Teachers" font-weight="800" fill="{CREAM}">
    <text x="128" y="244" dominant-baseline="hanging" font-size="78">OUT OF OUR</text>
    <text x="128" y="320" dominant-baseline="hanging" font-size="145">DEPTH</text>
    <text x="165" y="1215" dominant-baseline="hanging" font-size="{title_size}">{safe_title}</text>
  </g>
</svg>
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=HERE / "episode-000.json")
    parser.add_argument("--jpg", type=Path, required=True)
    parser.add_argument("--svg", type=Path, required=True)
    args = parser.parse_args()
    for path in (args.jpg, args.svg):
        if path.exists():
            raise FileExistsError(path)
        if not path.parent.is_dir():
            raise FileNotFoundError(path.parent)
    copy = json.loads(args.config.read_text())
    number = copy["episode_number"]
    if not isinstance(number, str) or re.fullmatch(r"[0-9]{3}", number) is None:
        raise ValueError("episode_number must be exactly three ASCII digits")
    title = copy["episode_title"].strip().upper()
    if not title:
        raise ValueError("episode_title cannot be empty")
    label = f"#{number} {title}"
    photo_path = (args.config.parent / copy["photo"]).resolve()
    photo = Image.open(photo_path).convert("RGB")
    image = ImageOps.fit(photo, (W, H), Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(image)
    face = fit_title(draw, label)
    draw.rectangle(TILE, fill=BLUE)
    draw.rectangle(STRIP, fill=NAVY)
    draw_top(draw, (128, 244), "OUT OF OUR", teacher(78), CREAM)
    draw_top(draw, (128, 320), "DEPTH", teacher(145), CREAM)
    draw_top(draw, (165, 1215), label, face, CREAM)
    image.resize((1280, 720), Image.Resampling.LANCZOS).save(
        args.jpg, format="JPEG", quality=94, subsampling=0, optimize=True
    )
    args.svg.write_text(svg(photo_path.read_bytes(), label, face.size))
    print(args.jpg)
    print(args.svg)


if __name__ == "__main__":
    main()
