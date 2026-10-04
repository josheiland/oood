#!/usr/bin/env python3
"""Episode 002 full theme cut: hook -> EPISODE 002 card -> the raw take in its
recorded order with only the clear mishaps removed -> outro card.

Usage: build-full.py <hook-id> <output.mp4>
"""

import json
import re
import sys
from pathlib import Path

import e002_common as c
from importlib import import_module

hooks = import_module("build-hooks")

# (reason, cut starts before these words, approx s, cut resumes before these words, approx s).
# Ints are hand-placed raw frames where overlapping speech leaves no clean gap.
REMOVALS = [
    ("Granola free-tier number is wrong: the free plan has unlimited meetings (30-day history), not 20-25 a month",
     11828, 394, 11948, 398),  # after "their like pro plan." -> "And yeah, transcribes"
    ("Josh's abandoned restart ('you now, if your AI tool is your intern, or sort of like giving it supervisees')",
     "So like you know you now", 909, 27499, 917),  # resumes on "So like when I'm calling"
    ("Mary's claim that Humanizer is built into Claude is wrong (it's a community skill); the default-skills guess goes with it",
     28408, 947, 28746, 958),  # "I have a humanizer one that" -> "makes it sound" (ASR-checked on the stitched join); v1 resumed at 28759 and clipped "makes"
    ("Names a Charlottesville shop as 'very clearly made by AI'",
     50559, 1685,  # after "you can see it."
     "I think in clod specifically", 1694),
    ("Canvas assignment story: Mary says on tape 'I don't think I can use that example' and 'I probably won't use that'",
     "Oh my God I don't think I can use", 1833, "Where it missed the mark", 1877),
]
HEAD = ("And we're live", 2.4)
TAIL = ("took me a second", 2048)   # drops the off-air "And that was good."

CHAPTERS = [  # name, words, approx raw s
    ("Meet your AI intern", "And we're live", 2.4),
    ("Projects: background", "So let me talk through", 92),
    ("Connectors: access", "Then we have connectors", 350),
    ("Skills: reusable directions", "then we have skills", 486),
    ("Composio: more accounts", "One thing that I know is helpful", 1202),
    ("Recap", "We kind of zoomed through that", 1315),
    ("What we built with AI", "with the time we have left", 1337),
    ("Where AI missed", "are there any other things", 1826),
    ("What's next", "Last question before we sign off", 1993),
]

FIXES = [
    (r"\bOOD\b", "OOOD"),
    (r"\b[Cc]omposi[a-z]*\b|\b[Cc]ompos[ie]o\b", "Composio"),
    (r"\bgranola\b", "Granola"), (r"\bcloud\b", "Claude"), (r"\bClod\b", "Claude"),
    (r"\bclock\b", "Claude"), (r"\bChad\b", "Chat"), (r"\bchat GPT\b", "ChatGPT"),
    (r"\b[Jj]im and I\b", "Gemini"), (r"\b[Ww]hisper [Ff]low\b", "Wispr Flow"),
    (r"\bM dashes\b", "em dashes"), (r"\bR Y C\b|\bRIC\b", "RYC"),
    (r"\b(?:[Rr]ener|[Rr]enier|[Rr]ender|[Rr]en|[Ww]hen your|[Rr]un your|[Rr]ent your severe) [Cc]ity\b", "Run Your City"),
    (r"www\.renercity\.org|www\.runyourcity\.org", "runyourcity.org"),
    (r"\bundyslexify\b|\bun dyslexify\b|\bdyslexia five\b", "Dyslexify"),
    (r"\bnotion\b", "Notion"), (r"\bmercury\b", "Mercury"), (r"\bcanvas\b", "Canvas"),
    (r"\bUSB\b", "GSB"), (r"\bsiri\b", "Siri"), (r"\blocues\b", "Loki's"),
]


def fmt(t):
    ms = round(t * 1000)
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def fix(text):
    for pat, rep in FIXES:
        text = re.sub(pat, rep, text)
    return text


def main():
    hook_id, output = sys.argv[1], Path(sys.argv[2])
    c.check_raw()
    h = next(x for x in hooks.HOOKS if x[0] == hook_id)
    ha = h[2] if isinstance(h[2], int) else c.cut_before(h[2], h[3])
    hb = h[4] if isinstance(h[4], int) else c.cut_after(h[4], h[5])

    start, end = c.cut_before(*HEAD), c.cut_after(*TAIL)
    ranges, cur, removed = [], start, []
    for reason, w0, t0, w1, t1 in REMOVALS:
        a = w0 if isinstance(w0, int) else c.cut_before(w0, t0)
        b = w1 if isinstance(w1, int) else c.cut_before(w1, t1)
        ranges.append((cur, a))
        removed.append({"reason": reason, "raw_frames": [a, b],
                        "raw": [round(a / c.FPS, 3), round(b / c.FPS, 3)],
                        "seconds": round((b - a) / c.FPS, 3),
                        "text": " ".join(w for w, s, e in c.words() if a / c.FPS <= s < b / c.FPS)})
        cur = b
    ranges.append((cur, end))

    body0 = (hb - ha) + c.TITLE_FRAMES
    timeline, pos = [], body0
    for a, b in ranges:
        timeline.append((a, b, pos))
        pos += b - a
    outro0 = pos
    total = outro0 + c.OUTRO_FRAMES

    def to_export(t):
        for a, b, p in timeline:
            if a / c.FPS <= t < b / c.FPS:
                return (p + (t * c.FPS - a)) / c.FPS
        return None

    chapters = [(0.0, "Cold open"), ((hb - ha) / c.FPS, "Theme and title")]
    for name, words, t in CHAPTERS:
        _, s, _ = c.find(words, t)
        chapters.append((max(to_export(s) - 0.3, chapters[-1][0] + 1), name))
    chapters[2] = (body0 / c.FPS, chapters[2][1])
    chapters.append((outro0 / c.FPS, "Outro"))

    pieces = [("src", ha, hb, *h[6:]), ("intro",)] + [("src", a, b) for a, b in ranges] + [("outro",)]
    n = c.render(pieces, output, crf=18, chapters=chapters,
                 title="Out of Our Depth | Episode 002: Make AI useful")
    assert n == total, (n, total)

    # captions: whisper words in export time, grouped into short cues
    cues = []

    CW = None

    def add_words(a, b, offset):
        ws = [(w, s, e) for w, s, e in CW if a / c.FPS <= s < b / c.FPS - 0.05]
        group = []
        for w, s, e in ws:
            es, ee = offset + s - a / c.FPS, offset + min(e, b / c.FPS) - a / c.FPS
            if group and (len(" ".join(x[0] for x in group) + " " + w) > 84
                          or ee - group[0][1] > 5.5 or es - group[-1][2] > 0.8):
                cues.append(group)
                group = []
            group.append((w, es, ee))
            if w[-1] in ".?!" and len(" ".join(x[0] for x in group)) > 30:
                cues.append(group)
                group = []
        if group:
            cues.append(group)

    CW = c.caption_words()
    add_words(ha, hb, 0.0)
    cues.append([("[Theme music]", (hb - ha) / c.FPS, body0 / c.FPS)])
    for a, b, p in timeline:
        add_words(a, b, p / c.FPS)
    cues.append([("[Theme music]", outro0 / c.FPS, total / c.FPS)])
    blocks = []
    for i, g in enumerate(cues, 1):
        s, e = g[0][1], max(g[-1][2] + 0.25, g[0][1] + 1.0)
        e = min(e, cues[i][0][1] if i < len(cues) else total / c.FPS)
        text = fix(" ".join(x[0] for x in g))
        if len(text) > 42:
            cut = text.rfind(" ", 0, len(text) // 2 + 8)
            text = text[:cut] + "\n" + text[cut + 1:]
        blocks.append(f"{i}\n{fmt(s)} --> {fmt(e)}\n{text}")
    output.with_suffix(".srt").write_text("\n\n".join(blocks) + "\n")

    chap_md = "\n".join(f"- {fmt(t)[:-4]} {name}" for t, name in chapters)
    output.with_suffix(".chapters.md").write_text(chap_md + "\n")
    output.with_suffix(".edl.json").write_text(json.dumps({
        "source": str(c.RAW), "source_sha256": c.RAW_SHA, "fps": c.FPS,
        "hook": {"id": hook_id, "raw_frames": [ha, hb]},
        "title_frames": c.TITLE_FRAMES, "outro_frames": c.OUTRO_FRAMES,
        "body_ranges_raw_frames": ranges,
        "body_ranges_export_start_frame": [p for _, _, p in timeline],
        "removed": removed, "head_trim_frames": start, "tail_from_frame": end,
        "chapters": chapters, "total_frames": total,
    }, indent=1, ensure_ascii=False))
    print(output, total / c.FPS)
    for r in removed:
        print(f"- {r['raw']} {r['seconds']}s | {r['text']}")


if __name__ == "__main__":
    main()
