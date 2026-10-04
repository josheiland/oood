#!/usr/bin/env python3
"""Render editable OOOD intro/outro SVGs and matching 1080p PNGs.

The layout follows the two approved blue cards supplied by Josh on 2026-09-28.
Edit the JSON copy for a future episode and render into a new directory.
"""

import argparse
import base64
import html
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, features


HERE = Path(__file__).resolve().parent
FONT_DIR = HERE.parent / "brand-fonts"
TEACHERS = FONT_DIR / "teachers.ttf"
MONO = FONT_DIR / "jetbrains-mono.ttf"
W, H = 1920, 1080
OUTRO_LINE_TOPS = (748, 815, 882)

# Measured from the supplied final-card reference, which supersedes the
# earlier generic blue/white title and outro treatments for these cards.
BLUE = "#3DAFF4"
CREAM = "#F3E8DD"
NAVY = "#0B2842"


def font(path: Path, size: int, weight: int):
    engine = ImageFont.Layout.RAQM if features.check_feature("raqm") else ImageFont.Layout.BASIC
    result = ImageFont.truetype(str(path), size, layout_engine=engine)
    result.set_variation_by_axes([weight])
    return result


def width(draw: ImageDraw.ImageDraw, value: str, face) -> float:
    return draw.textlength(value, font=face)


def draw_top(draw: ImageDraw.ImageDraw, x: int, top: int, value: str,
             face, color: str, tracking: float = 0) -> float:
    """Shape the entire text with the real font and its native kerning."""
    if not value:
        return float(x)
    y = top - face.getbbox(value)[1]
    draw.text((x, y), value, font=face, fill=color, spacing=tracking)
    return x + width(draw, value, face)


def draw_mono_tracked(draw, x, top, value, face, color, tracking):
    """The widely spaced mono labels intentionally use manual tracking."""
    y = top - face.getbbox(value)[1]
    position = float(x)
    for char in value:
        draw.text((round(position), y), char, font=face, fill=color)
        position += draw.textlength(char, font=face) + tracking
    return position - tracking


def fit_title(draw, value, default_size=66, limit=1600):
    for size in range(default_size, 39, -1):
        face = font(TEACHERS, size, 700)
        if width(draw, value, face) <= limit:
            return face
    raise ValueError(f"Episode title does not fit: {value}")


def render_intro(copy):
    image = Image.new("RGB", (W, H), BLUE)
    draw = ImageDraw.Draw(image)
    mono = font(MONO, 30, 500)
    kicker = font(TEACHERS, 77, 800)
    depth = font(TEACHERS, 260, 800)
    title = fit_title(draw, copy["episode_title"])
    if copy.get("show_episode_number", True):
        draw_mono_tracked(draw, 153, 165, f"EPISODE {copy['episode_number']}", mono, CREAM, 8.4)
    draw_top(draw, 152, 374, "OUT OF OUR", kicker, CREAM)
    draw_top(draw, 151, 466, "DEPTH", depth, CREAM)
    draw_top(draw, 153, 864, copy["episode_title"], title, NAVY)
    return image


def render_outro(copy):
    image = Image.new("RGB", (W, H), BLUE)
    draw = ImageDraw.Draw(image)
    mono = font(MONO, 30, 500)
    heading = font(TEACHERS, 156, 800)
    body = font(TEACHERS, 46, 700)
    if copy.get("outro_kicker"):
        draw_mono_tracked(draw, 154, 122, copy["outro_kicker"], mono, CREAM, 8.4)
    for value, top in zip(copy["outro_heading"], (333, 471), strict=True):
        if width(draw, value, heading) > 1620:
            raise ValueError(f"Outro heading does not fit: {value}")
        draw_top(draw, 154, top, value, heading, CREAM)
    for parts, top in zip(copy["outro_lines"], OUTRO_LINE_TOPS, strict=True):
        left, right = parts
        x = draw_top(draw, 154, top, left, body, NAVY) + 16
        end = draw_top(draw, round(x), top, right, body, CREAM)
        if end > 1765:
            raise ValueError(f"Outro line does not fit: {left} {right}")
    return image


def svg_text(x, top, value, family, size, color, spacing=0, weight=800):
    safe = html.escape(value)
    return (f'<text x="{x}" y="{top}" dominant-baseline="hanging" '
            f'font-family="{family}" font-size="{size}" font-weight="{weight}" '
            f'letter-spacing="{spacing}" fill="{color}">{safe}</text>')


def svg_document(elements):
    teacher_data = base64.b64encode(TEACHERS.read_bytes()).decode("ascii")
    mono_data = base64.b64encode(MONO.read_bytes()).decode("ascii")
    css = (f'@font-face{{font-family:Teachers;font-weight:100 900;src:url(data:font/ttf;base64,{teacher_data})}}'
           f'@font-face{{font-family:JetBrainsMono;font-weight:100 900;src:url(data:font/ttf;base64,{mono_data})}}')
    body = "\n  ".join(elements)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
            f'viewBox="0 0 {W} {H}" role="img">\n'
            f'  <style>{css}</style>\n'
            f'  <rect width="{W}" height="{H}" fill="{BLUE}"/>\n'
            f'  {body}\n</svg>\n')


def intro_svg(copy, title_size):
    elements = []
    if copy.get("show_episode_number", True):
        elements.append(svg_text(153, 165, f"EPISODE {copy['episode_number']}", "JetBrainsMono", 30, CREAM, 8.4, 500))
    elements.extend([
        svg_text(152, 374, "OUT OF OUR", "Teachers", 77, CREAM),
        svg_text(151, 466, "DEPTH", "Teachers", 260, CREAM),
        svg_text(153, 864, copy["episode_title"], "Teachers", title_size, NAVY, weight=700),
    ])
    return svg_document(elements)


def outro_svg(copy):
    elements = []
    if copy.get("outro_kicker"):
        elements.append(svg_text(154, 122, copy["outro_kicker"], "JetBrainsMono", 30, CREAM, 8.4, 500))
    for value, top in zip(copy["outro_heading"], (333, 471), strict=True):
        elements.append(svg_text(154, top, value, "Teachers", 156, CREAM))
    probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    body = font(TEACHERS, 46, 700)
    for parts, top in zip(copy["outro_lines"], OUTRO_LINE_TOPS, strict=True):
        left, right = parts
        elements.append(svg_text(154, top, left, "Teachers", 46, NAVY, weight=700))
        x = 154 + width(probe, left, body) + 16
        elements.append(svg_text(round(x), top, right, "Teachers", 46, CREAM, weight=700))
    return svg_document(elements)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=HERE / "episode-000.json")
    parser.add_argument("--output-dir", type=Path, default=HERE)
    args = parser.parse_args()
    copy = json.loads(args.config.read_text())
    if len(copy["episode_number"]) != 3 or not copy["episode_number"].isascii() or not copy["episode_number"].isdigit():
        raise ValueError("episode_number must be exactly three ASCII digits (000, 001, 002, ...)")
    if len(copy["outro_heading"]) != 2 or len(copy["outro_lines"]) != 3:
        raise ValueError("The approved card has two heading and three footer lines")
    if not args.output_dir.is_dir():
        raise FileNotFoundError(args.output_dir)
    files = {
        "intro-template.svg": None,
        "outro-template.svg": None,
        "intro-card.png": None,
        "outro-card.png": None,
    }
    for name in files:
        if (args.output_dir / name).exists():
            raise FileExistsError(args.output_dir / name)
    intro = render_intro(copy)
    outro = render_outro(copy)
    probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    title_size = fit_title(probe, copy["episode_title"]).size
    (args.output_dir / "intro-template.svg").write_text(intro_svg(copy, title_size))
    (args.output_dir / "outro-template.svg").write_text(outro_svg(copy))
    intro.save(args.output_dir / "intro-card.png", optimize=True)
    outro.save(args.output_dir / "outro-card.png", optimize=True)
    for name in files:
        print(args.output_dir / name)


if __name__ == "__main__":
    main()
