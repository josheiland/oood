#!/usr/bin/env python3
"""Build the free "AI from 0 to 1" study guide: the /guide web page and the PDF.

Words come from website/learning-topics.json (the 35 from the old Learning list, wording unchanged) plus
the guide-only words in 03_ASSETS/study-guide/guide-levels.json, which also holds the levels, the name-that-moment
cards, dares, debates, five ways to get started, If you get stuck tips and Where to go next.

    python3 scripts/build-study-guide.py

Writes website/guide.html, website/downloads/ai-0-to-1-study-guide.pdf, website/images/guide-cover.webp
and the print HTML at 03_ASSETS/study-guide/study-guide.html. Needs Python 3, Pillow and Playwright with
Chromium or Chrome (set CHROME=/path/to/chrome to pick one). Fonts load from Google Fonts at build time.

House style (Mary 2026-11-21): no divider lines, pills and the snowflake only sparingly, and no period
at the end of a paragraph, list item or label (soften() strips them from the finished HTML).
"""
import html, json, os, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / 'website'
SRC = ROOT / '03_ASSETS' / 'study-guide'
guide = json.loads((SRC / 'guide-levels.json').read_text())
topics = {t['id']: t for t in json.loads((WEB / 'learning-topics.json').read_text())}
topics.update(guide.get('extra_words', {}))
for k, v in guide.get('overrides', {}).items():
    topics[k] = {**topics[k], **v}  # evergreen wording for the guide; learning-topics.json stays as Josh wrote it
levels = guide['levels']

yt = dict(re.findall(r"'(\d{3})':\s*'([^']+)'", (ROOT / 'scripts' / 'build-learning.js').read_text()))
yt.update(guide.get('episodes', {}))

used = [w for lv in levels for w in lv['words']]
missing = set(topics) - set(used)
unknown = set(used) - set(topics)
if missing or unknown or len(used) != len(set(used)):
    sys.exit(f'every word must appear exactly once; missing {sorted(missing)}, unknown {sorted(unknown)}')
N = len(used)

BANNED = ['—', '–', '·', '…', '“', '”', '‘', '’']
def check(text):
    for ch in BANNED:
        if ch in text:
            sys.exit(f'house style: no dashes, dots, ellipses or curly quotes. Found {ch!r} in: {text}')
    return text
e = lambda s: html.escape(check(str(s)), quote=True)

END_DOT = re.compile(r'\.(\s*</(?:p|li|span|div|a|b|h1|h2|h3)>)')
def soften(doc):
    """Mary: the last sentence or phrase of a block doesn't get a period. Feels more human."""
    return END_DOT.sub(r'\1', doc)

def phrase(s):
    """Drop the final period from a one-clause phrase; keep it when the text holds two sentences."""
    s = s.strip()
    if s.endswith('.') and not re.search(r'[.!?]"? [A-Z"]', s[:-1]):
        return s[:-1]
    return s

def ep_url(number, time=None):
    if number not in yt:
        sys.exit(f'episode {number} has no YouTube id; add it to "episodes" in guide-levels.json')
    secs = 0
    if time:
        m, s = map(int, time.split(':')); secs = m * 60 + s
    return f'https://www.youtube.com/watch?v={yt[number]}' + (f'&t={secs}' if secs else '')

def tag(t):
    """Episode link, only when we found the moment in the captions. No link, no label."""
    ep = t.get('episode')
    if not ep:
        return ''
    label = f"Watch ep {ep['number']} at {ep['time']}" if ep['time'] != '00:00' else f"Watch all of ep {ep['number']}"
    return f'<a class="lbl" href="{html.escape(ep_url(ep["number"], ep["time"]))}" target="_blank" rel="noopener">&#9654;&#xFE0E; {label}</a>'

SPARK = '<svg class="spark" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 1.5v21M2.9 6.75l18.2 10.5M2.9 17.25l18.2-10.5" stroke="currentColor" stroke-width="3.4" stroke-linecap="round"/></svg>'
slug = lambda n: 'level-' + n.replace('.', '-')

# ---------- shared pieces ----------
def word_card(t):
    aka = f'<span class="aka">{e(t["aka"])}</span>' if t.get('aka') else ''
    return (f'<article class="word" id="{t["id"]}">'
            f'<h3>{e(t["title"])}</h3>{aka}<p>{e(t["definition"])}</p>'
            f'<p class="think"><b>Think of it like</b> {e(phrase(t["think"]))}</p>{tag(t)}</article>')

def air_web(lv):
    """Name that moment: three tap-to-flip cards and one dare. Replaces the old try-its (Mary 2026-11-21)."""
    cards = ''.join(
        f'<button class="mo" type="button" aria-label="Tap to see the word"><span class="mo__in">'
        f'<span class="mo__f"><span class="mo__q">{e(q)}</span><span class="mo__hint">Tap to check</span></span>'
        f'<span class="mo__b"><span class="mo__hint">That\'s</span><span class="mo__a">{e(topics[w]["title"])}</span></span></span></button>'
        for q, w in lv['moments'])
    return (f'<div class="air"><p class="kick">Come up for air  /  name that moment</p><div class="mos">{cards}</div>'
            f'<p class="dare"><b>Dare</b> {e(lv["dare"])}</p></div>')

def air_pdf(lv):
    qs = ''.join(f'<li>{e(q)}</li>' for q, w in lv['moments'])
    ans = '  /  '.join(f'{i + 1} {topics[w]["title"]}' for i, (q, w) in enumerate(lv['moments']))
    return (f'<div class="air"><p class="kick">Come up for air  /  name that moment</p><ol>{qs}</ol>'
            f'<p class="ans">{e(ans)}</p><p class="dare"><b>Dare</b> {e(lv["dare"])}</p></div>')

MAP = f'''<div class="map"><p class="kick">{SPARK} The whole thing on one page</p>
  <h3>Learn, look, think, act</h3>
  <p class="map-sub">Almost every AI headline is about one of these four steps. Figure out which one, and the news gets a lot less confusing.</p>
  <div class="map-row">
    <div><b>Learn</b><p>Training. The model reads a mountain of text and the patterns stick. Happens months before you ever open the app.</p><i>Training, GPUs, data centers, fine-tuning</i></div>
    <div><b>Look</b><p>Pulling in fresh info the moment you ask: a web search, your files, your inbox</p><i>RAG, deep research, MCP</i></div>
    <div><b>Think</b><p>Working out the answer, one token at a time, inside the context window</p><i>Tokens, context window, inference</i></div>
    <div><b>Act</b><p>Doing something in the world: sending, booking, clicking, writing code</p><i>Agents, skills, computer use</i></div>
  </div></div>'''

def headline(name, accent):
    if accent and accent.lower() in name.lower():
        i = name.lower().index(accent.lower())
        return html.escape(name[:i]) + f'<span class="blue">{html.escape(name[i:i + len(accent)])}</span>' + html.escape(name[i + len(accent):])
    return e(name)

def level_pdf(lv, i):
    words = ''.join(word_card(topics[w]) for w in lv['words'])
    return f'''<section class="level" id="{slug(lv["n"])}"><div class="page">
  <span class="wm" aria-hidden="true">{lv["n"]}</span>
  <header class="lv-head"><p class="kick">Level {lv["n"]}  /  {e(lv["depth"])}  /  {len(lv["words"])} words</p><h2>{headline(lv["name"], lv.get("accent"))}</h2><p class="promise">{e(lv["promise"])}</p></header>
  <div class="cards{' cards--3' if len(lv["words"]) > 10 else ''}">{words}</div>
  {air_pdf(lv)}
  {MAP if lv["n"] == "1.0" else ""}
</div></section>'''

def level_web(lv, i):
    words = ''.join(word_card(topics[w]) for w in lv['words'])
    return f'''<section class="lv lv--{i}{' dk' if i >= 5 else ''}" data-depth id="{slug(lv["n"])}" aria-labelledby="{slug(lv["n"])}-t"><div class="h-wrap">
  <header class="lv-head{' lv-head--word' if not lv["depth"][0].isdigit() else ''}"><span class="ft" aria-hidden="true">{e(lv["depth"])}</span><div><p class="kick">Level {lv["n"]}  /  {len(lv["words"])} words</p><h2 id="{slug(lv["n"])}-t">{headline(lv["name"], lv.get("accent"))}</h2><p class="promise">{e(lv["promise"])}</p></div></header>
  <div class="cards">{words}</div>
  {MAP if lv["n"] == "0.6" else ""}
  {air_web(lv)}
</div></section>'''

def way_card(b, web):
    watch = f'  /  <a href="{html.escape(ep_url(b["watch"]))}" target="_blank" rel="noopener">&#9654;&#xFE0E; ep {b["watch"]}</a>' if b.get('watch') else ''
    copy = f'<button class="copy" type="button" data-copy="p-{b["id"]}">Copy prompt</button>' if web else ''
    return (f'<article class="build"><p class="lbl">{e(b["time"])}  /  {e(b["level"])}{watch}</p>'
            f'<h3>{e(b["title"])}</h3><p>{e(b["why"])}</p>'
            f'<div class="prompt"><p class="kick">Copy this</p><p id="p-{b["id"]}">{e(b["prompt"])}</p>{copy}</div></article>')

sh = guide['start_here']
start_steps = ''.join(f'<li>{e(s)}</li>' for s in sh['steps'])
TEN = f'<p class="tenhours"><b>The ten-hour rule</b> {e(guide["ten_hours"])}</p>'
START = f'''<div class="start"><p class="kick">{SPARK} Start here</p>
  <h2>{e(sh["title"])}</h2><p class="start-time">{e(sh["time"])}</p>
  <ol class="steps">{start_steps}</ol>
  {TEN}</div>'''

ways = ''.join(way_card(b, True) for b in guide['ways'])
ways_pdf = ''.join(way_card(b, False) for b in guide['ways'])
debates_web = ''.join(
    f'<article class="debate"><span class="debate__n">{i + 1:02d}</span><h3>{e(q)}</h3>'
    f'<div class="sides"><button type="button" class="side">{e(a)}</button><button type="button" class="side">{e(b)}</button></div></article>'
    for i, (q, a, b) in enumerate(guide['debates']))
debates_pdf = ''.join(f'<article class="debate"><h3>{i + 1}. {e(q)}</h3><p><b>A</b> {e(a)}</p><p><b>B</b> {e(b)}</p></article>'
                      for i, (q, a, b) in enumerate(guide['debates']))
stuck = ''.join(f'<p><b>{e(phrase(a))}</b> {e(b)}</p>' for a, b in guide['stuck'])
nxt = ''.join(f'<a class="next" href="{html.escape(u)}" target="_blank" rel="noopener"><span class="lbl">{e(who)}</span><h3>{e(t)}</h3><p>{e(len_)}</p></a>' for t, who, len_, u in guide['next'])
US = ('<a class="next next--us" href="https://www.youtube.com/@OutOfOurDepthPod?sub_confirmation=1" target="_blank" rel="noopener">'
      '<span class="lbl">Us, obviously</span><h3>Out of Our Depth</h3><p>New episodes every week. Would it kill ya to subscribe?</p></a>')
WHY = ''.join(f'<p>{e(x)}</p>' for x in guide['why'])
OURS = ''.join(f'<li>{e(x)}</li>' for x in guide['ourselves'])
HELP = 'Stuck on one? Email <a href="mailto:hi@outofourdepth.com">hi@outofourdepth.com</a>, tell us which one, and we\'ll help'
boxes = ''.join(f'<li>{e(topics[w]["title"])}</li>' for lv in levels for w in lv['words'])
NOTE = "We only email when it's worth it. Written by real humans: Josh handles the spelling, Mary handles the jokes (proudly dyslexic + still wrote this subheader #flex)"
SIGN = "Can't lie, Claude built this"
PITCH = f'{N} words, 10 debates and 5 fun ways to get started'

# ---------- PDF ----------
sticker = (WEB / 'images' / 'hosts-sticker.webp').as_uri()
toc = ''.join(f'<li><span class="toc-n">{lv["n"]}</span><span class="toc-name">{e(lv["name"])}</span><span class="toc-p">{e(phrase(lv["promise"]))}</span></li>' for lv in levels)

PDF_CSS = '''
@page { size: letter; margin: .6in 0 .62in; }
@page :first { margin: 0; }
:root { --cream:#FBF1E5; --foam:#FDF8F2; --navy:#0B2A45; --muted:#4F6072; --blue:#38B6FF; --ink:#0A6BB8; --sky:#BDE5FF; --wm:#E2EEF6; }
html { background: var(--cream); }
body { margin:0; padding:0 .75in; color:var(--navy); font-family:Teachers, sans-serif; font-size:9.8pt; line-height:1.4; -webkit-print-color-adjust:exact; print-color-adjust:exact; }
.kick { font-family:'JetBrains Mono', monospace; font-size:7.5pt; letter-spacing:.14em; text-transform:uppercase; color:var(--ink); margin:0 0 8pt; display:flex; align-items:center; gap:6pt; }
.spark { width:9pt; height:9pt; color:var(--blue); flex:none; }
h1,h2,h3 { font-weight:800; text-transform:uppercase; margin:0; line-height:.95; }
.blue { color:var(--blue); }
a { color:var(--ink); text-decoration:none; }
.lbl { display:block; font-family:'JetBrains Mono', monospace; font-size:6.8pt; letter-spacing:.08em; text-transform:uppercase; color:var(--ink); margin-top:5pt; }
.lbl--off { color:#8C99A6; }
.page { page-break-before:always; position:relative; }
.wm { position:absolute; top:-.35in; right:-.45in; font-weight:800; font-size:150pt; line-height:1; letter-spacing:-.03em; color:var(--wm); z-index:-1; }
.lv-head, .sec-head { margin-bottom:16pt; max-width:5.4in; }
.lv-head h2, .sec-head h2 { font-size:32pt; }
.promise, .sec-head p:not(.kick) { margin:8pt 0 0; font-size:11.5pt; line-height:1.4; }
/* cover: navy, like her full-color cover */
.cover { margin:0 -.75in; height:11in; box-sizing:border-box; padding:.8in .85in .75in; background:var(--navy); color:var(--cream); display:flex; flex-direction:column; page-break-after:always; position:relative; overflow:hidden; }
.cover .brand { font-weight:800; text-transform:uppercase; line-height:.9; font-size:11pt; }
.cover .brand b { display:block; font-size:22pt; }
.cover .kick { color:var(--sky); margin-top:1.5in; }
.cover h1 { font-size:58pt; margin-top:8pt; }
.cover h1 span { display:block; color:var(--blue); font-size:132pt; line-height:.84; }
.cover .sub { font-size:14pt; margin:22pt 0 0; max-width:4.6in; color:var(--sky); }
.cover img { position:absolute; right:.6in; bottom:1.1in; width:3.9in; transform:rotate(-3deg); }
.cover .by { margin-top:auto; font-family:'JetBrains Mono', monospace; font-size:7.5pt; letter-spacing:.14em; text-transform:uppercase; color:var(--sky); }
/* start here + contents */
.start h2 { font-size:30pt; }
.start-time { font-family:'JetBrains Mono', monospace; font-size:7.5pt; letter-spacing:.12em; text-transform:uppercase; color:var(--ink); margin:8pt 0 14pt; }
.steps { margin:0; padding-left:16pt; font-size:12pt; max-width:5.6in; }
.steps li { margin-bottom:4pt; }
.tenhours { margin:10pt 0 0; background:var(--navy); color:var(--cream); border-radius:12pt; padding:13pt 15pt; font-size:10.5pt; max-width:5.6in; }
.tenhours b { color:var(--blue); margin-right:3pt; }
.toc { list-style:none; margin:16pt 0 0; padding:0; }
.toc li { display:grid; grid-template-columns:.7in 1.9in 1fr; align-items:baseline; gap:10pt; padding:3pt 0; }
.toc-n { font-weight:800; font-size:18pt; color:var(--blue); }
.toc-name { font-weight:800; text-transform:uppercase; font-size:11.5pt; }
.toc-p { font-size:9.5pt; color:var(--muted); }
/* words: plain text in two columns, lots of space, no boxes */
.cards { display:grid; grid-template-columns:1fr 1fr; gap:11pt 24pt; }
.word { break-inside:avoid; }
.word h3, .build h3, .next h3 { font-size:12.5pt; }
.aka { display:block; font-family:'JetBrains Mono', monospace; font-size:6.8pt; letter-spacing:.05em; color:var(--muted); margin-top:2pt; }
.word p { margin:4pt 0 0; }
.think { color:var(--muted); font-size:9.3pt; }
.think b { color:var(--navy); font-weight:700; }
/* the one highlighted box per page */
.pair { display:grid; grid-template-columns:1.15fr 1fr; gap:20pt; margin-top:16pt; break-inside:avoid; align-items:start; }
.try { background:var(--navy); color:var(--cream); border-radius:12pt; padding:13pt 15pt; }
.try .kick { color:var(--sky); }
.check { padding:2pt 0; }
.pair ol { margin:0; padding-left:14pt; font-size:9.6pt; }
.pair li { margin-bottom:3.5pt; }
.hint { font-size:9pt; color:var(--muted); margin:0 0 6pt; }
.map { margin-top:20pt; break-inside:avoid; }
.map h3 { font-size:22pt; }
.map-sub { margin:6pt 0 14pt; color:var(--muted); max-width:5.4in; }
.map-row { display:grid; grid-template-columns:repeat(4,1fr); gap:14pt; }
.map-row b { display:block; font-weight:800; text-transform:uppercase; font-size:15pt; margin-bottom:4pt; color:var(--blue); }
.map-row p { margin:0 0 6pt; font-size:9pt; }
.map-row i { font-style:normal; font-family:'JetBrains Mono', monospace; font-size:6.5pt; letter-spacing:.05em; text-transform:uppercase; color:var(--ink); }
/* builds */
.builds { display:grid; grid-template-columns:1fr 1fr; gap:14pt 24pt; }
.build { break-inside:avoid; }
.build .lbl { margin:0 0 5pt; }
.build p { margin:4pt 0 0; }
.prompt { margin-top:8pt; background:var(--foam); border-radius:12pt; padding:10pt 12pt; }
.prompt .kick { margin-bottom:4pt; }
.prompt p { margin:0; font-size:9.3pt; }
/* first week */
.week { list-style:none; margin:0; padding:0; display:grid; gap:5pt; max-width:6.4in; }
.week li { display:grid; grid-template-columns:.6in 1.6in 1fr; align-items:baseline; gap:10pt; }
.week .lbl { margin:0; font-size:8pt; }
.week b { font-weight:800; text-transform:uppercase; font-size:12pt; }
.week span:last-child { font-size:10pt; color:var(--muted); }
/* finish */
.stuck p { margin:0 0 6pt; max-width:6.6in; font-size:10pt; }
.stuck b { font-weight:800; margin-right:3pt; }
.nexts { margin-top:12pt; }
.nexts h2, .done h2 { font-size:22pt; margin-bottom:12pt; }
.next-row { display:grid; grid-template-columns:repeat(4,1fr); gap:10pt; align-items:stretch; }
.next { display:flex; flex-direction:column; background:var(--foam); border-radius:12pt; padding:10pt 11pt; color:var(--navy); }
.next--us { background:var(--navy); color:var(--cream); }
.next--us .lbl { color:var(--sky); }
.next--us p { color:var(--sky) !important; }
.next .lbl { margin:0 0 3pt; }
.next p { margin:4pt 0 0; font-size:9pt; color:var(--muted); }
.done { margin-top:28pt; }
.cards--3 { grid-template-columns:1fr 1fr 1fr; gap:9pt 16pt; font-size:9pt; }
.cards--3 .think { font-size:8.6pt; }
.boxes { columns:5; column-gap:16pt; list-style:none; margin:6pt 0 14pt; padding:0; }
.boxes li { break-inside:avoid; padding:2pt 0 2pt 15pt; position:relative; font-size:9pt; }
.boxes li::before { content:''; position:absolute; left:0; top:4.5pt; width:8pt; height:8pt; border:1.2pt solid var(--navy); border-radius:2pt; }
.why { max-width:5.9in; margin-bottom:16pt; }
.why p:not(.kick) { margin:0 0 5pt; font-size:10.3pt; }
.ours { margin-top:12pt; }
.ours h3 { font-size:16pt; margin-bottom:6pt; }
.ours ul { margin:0; padding-left:14pt; columns:2; column-gap:20pt; font-size:9.6pt; }
.ours li { margin-bottom:3pt; break-inside:avoid; }
.help { margin-top:8pt !important; font-weight:700; }
.contact { margin-top:16pt; font-size:10pt; color:var(--muted); }
.sign { margin-top:14pt; font-family:'JetBrains Mono', monospace; font-size:8pt; letter-spacing:.06em; color:var(--ink); }
.outro { background:var(--navy); color:var(--cream); border-radius:12pt; padding:13pt 15pt; font-size:10.5pt; }
.outro a { color:var(--sky); }
.air { margin-top:16pt; break-inside:avoid; background:var(--navy); color:var(--cream); border-radius:12pt; padding:13pt 15pt; }
.air .kick { color:var(--sky); }
.air ol { margin:0; padding-left:14pt; font-size:10pt; columns:3; column-gap:16pt; }
.air li { break-inside:avoid; margin-bottom:3pt; }
.air .ans { margin:8pt 0 0; font-family:'JetBrains Mono', monospace; font-size:6.5pt; letter-spacing:.06em; text-transform:uppercase; color:var(--sky); transform:rotate(180deg); }
.air .dare { margin:8pt 0 0; font-size:10pt; }
.air .dare b { color:var(--blue); margin-right:3pt; }
.debates { display:grid; grid-template-columns:1fr 1fr; gap:11pt 24pt; }
.debate { break-inside:avoid; }
.debate h3 { font-size:11.5pt; line-height:1.05; }
.debate p { margin:3pt 0 0; font-size:9.3pt; color:var(--muted); }
.debate p b { color:var(--ink); font-weight:700; margin-right:3pt; }
'''

pdf = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><title>AI from 0 to 1 | Out of Our Depth</title>
<link href="https://fonts.googleapis.com/css2?family=Teachers:wght@400..800&family=JetBrains+Mono:wght@400;700&display=block" rel="stylesheet">
<style>{PDF_CSS}</style></head><body>
<section class="cover">
  <div class="brand">Out of our<b>Depth</b></div>
  <p class="kick">A free study guide</p>
  <h1>AI from<span>0 to 1</span></h1>
  <p class="sub">{PITCH}. It gets deeper as you go</p>
  <img src="{sticker}" alt="">
  <p class="by">Mary and Josh  /  outofourdepth.com/guide</p>
</section>
<section class="intro">
  <span class="wm" aria-hidden="true">0</span>
  <div class="why"><p class="kick">Why we made this</p>{WHY}</div>
  {START}
  <ol class="toc">{toc}<li><span class="toc-n">+</span><span class="toc-name">10 debates</span><span class="toc-p">Pick a side, then go start something at dinner</span></li><li><span class="toc-n">+</span><span class="toc-name">5 fun ways to start</span><span class="toc-p">Prompts to copy, no experience needed</span></li></ol>
</section>
{''.join(level_pdf(lv, i) for i, lv in enumerate(levels))}
<section class="page">
  <span class="wm" aria-hidden="true">10</span>
  <div class="sec-head"><p class="kick">{SPARK} The bottom  /  no right answers</p><h2>10 <span class="blue">debates</span></h2><p>We don't agree on half of these. Pick a side, then go start something at dinner.</p></div>
  <div class="debates">{debates_pdf}</div>
  <div class="ours"><p class="kick">The parts that need us</p><h3>What we still do <span class="blue">ourselves</span></h3><ul>{OURS}</ul></div>
</section>
<section class="page">
  <span class="wm" aria-hidden="true">5</span>
  <div class="sec-head"><p class="kick">{SPARK} Steal our homework</p><h2>5 fun ways to get <span class="blue">started</span></h2><p>The fastest way to learn AI is to make something with it. Pick one, paste the prompt into any AI app, and fill in the [brackets].</p></div>
  <div class="builds">{ways_pdf}</div>
</section>
<section class="page">
  <span class="wm" aria-hidden="true">?</span>
  <div class="stuck"><p class="kick">Happens to everyone</p><h2 style="font-size:22pt;margin-bottom:12pt">If you get <span class="blue">stuck</span></h2>{stuck}<p class="help">{HELP}</p></div>
  <div class="nexts" style="margin-top:10pt"><p class="kick">Want more?</p><h2>Where to go <span class="blue">next</span></h2><div class="next-row">{US}{nxt}</div></div>
</section>
<section class="flow" style="margin-top:14pt">
  <div class="sec-head" style="margin-bottom:8pt"><p class="kick">Level 1.0, done</p><h2>You're at <span class="blue">1</span></h2><p>Check off every word you could explain to a friend. Anything left, go back and try it once more.</p></div>
  <ul class="boxes">{boxes}</ul>
  <p class="contact">Which word still confuses you? Tell us at <a href="mailto:hi@outofourdepth.com">hi@outofourdepth.com</a>. Get the notes at <a href="https://outofourdepth.com">outofourdepth.com</a>. {e(NOTE)}</p>
  <p class="sign">{e(SIGN)}</p>
</section>
</body></html>'''
pdf = soften(pdf)
(SRC / 'study-guide.html').write_text(pdf)

# ---------- Web page: The Dive. One scroll that gets deeper, cream at 0 ft to navy at the deep end ----------
gauge = ''.join(f'<a href="#{slug(lv["n"])}"><i></i><span>{e(lv["depth"])}</span></a>' for lv in levels) + '<a href="#debates"><i></i><span>The bottom</span></a>'
PDF_URL = '/downloads/ai-0-to-1-study-guide.pdf'
page = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AI from 0 to 1: a free study guide | Out of Our Depth</title>
  <meta name="description" content="{PITCH}. A free AI study guide that gets deeper as you scroll, by Mary and Josh of Out of Our Depth.">
  <meta name="theme-color" content="#FBF1E5">
  <link rel="canonical" href="https://outofourdepth.com/guide">
  <meta property="og:type" content="article">
  <meta property="og:url" content="https://outofourdepth.com/guide">
  <meta property="og:title" content="AI from 0 to 1: a free study guide">
  <meta property="og:description" content="{PITCH}. Free, no sign-up.">
  <meta property="og:image" content="https://outofourdepth.com/images/og-v7.png">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:site" content="@OutOfOurDepthX">
  <link rel="icon" type="image/png" sizes="32x32" href="/images/favicon-32.png">
  <link rel="apple-touch-icon" href="/images/apple-touch-icon.png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Teachers:wght@400..800&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/styles.css">
  <link rel="stylesheet" href="/home.css">
  <link rel="stylesheet" href="/guide.css">
  <script>window.va = window.va || function () {{ (window.vaq = window.vaq || []).push(arguments); }};</script>
  <script defer src="/_vercel/insights/script.js"></script>
</head>
<body class="home guide">
  <!-- Built by scripts/build-study-guide.py from website/learning-topics.json and 03_ASSETS/study-guide/guide-levels.json. Edit those, not this file. -->
  <a class="skip-link" href="#level-0-0">Skip to the first level</a>
  <header class="h-nav">
    <div class="h-wrap h-nav__inner">
      <a class="h-wm" href="/" aria-label="Out of Our Depth home"><span class="h-wm__k">Out of our</span><span>Depth</span></a>
      <nav class="h-links" aria-label="Main"><a href="/#episodes">Episodes</a><a href="/guide#start-building">Try it</a><a href="/guide" aria-current="page">Study guide</a></nav>
      <a class="h-btn h-btn--sm" href="https://www.youtube.com/@OutOfOurDepthPod" data-link="youtube" target="_blank" rel="noopener">Watch the show</a>
    </div>
  </header>
  <nav class="gauge" aria-label="How deep you are">{gauge}</nav>
  <main>
    <section class="g-hero">
      <div class="h-wrap g-hero__inner">
        <p class="kick">Free study guide  /  no sign-up</p>
        <h1><span class="g-hero__kick">AI from</span><span class="g-hero__big">0 to 1</span></h1>
        <p class="g-hero__sub">{PITCH}. Keep scrolling, it gets deeper</p>
        <div class="g-hero__ctas"><a class="h-btn" href="#level-0-0">Dive in</a><a class="h-btn h-btn--ghost" href="{PDF_URL}" download>Download the PDF</a></div>
        <img class="g-hero__hosts" src="/images/hosts-sticker-640.webp" width="640" height="421" alt="Mary and Josh">
      </div>
    </section>
    <section class="g-why h-wrap"><div class="g-narrow"><p class="kick">Why we made this</p>{WHY}</div></section>
    <section class="g-ways" id="start-building"><div class="h-wrap">
      <div class="sec-head"><p class="kick">{SPARK} Dip a toe in</p><h2>5 fun ways to get <span class="blue">started</span></h2><p>The fastest way to learn AI is to make something with it. Pick one, paste the prompt into any AI app, and fill in the [brackets].</p></div>
      <div class="cards cards--ways">{ways}{TEN}</div>
    </div></section>
    {''.join(level_web(lv, i) for i, lv in enumerate(levels))}
    <section class="lv lv--6 dk" data-depth id="debates"><div class="h-wrap">
      <header class="lv-head lv-head--word"><span class="ft" aria-hidden="true">The bottom</span><div><p class="kick">No right answers down here</p><h2>10 <span class="blue">debates</span></h2><p class="promise">We don't agree on half of these. Tap your side, then go start something at dinner</p></div></header>
      <div class="debates">{debates_web}</div>
      <div class="g-ours"><p class="kick">The parts that need us</p><h3>What we still do <span class="blue">ourselves</span></h3><ul>{OURS}</ul></div>
    </div></section>
    <section class="g-end dk"><div class="h-wrap">
      <div class="g-end__cols">
        <div class="g-stuck" id="stuck"><p class="kick">Happens to everyone</p><h3>If you get <span class="blue">stuck</span></h3>{stuck}<p class="g-help">{HELP}</p></div>
        <div class="g-next"><p class="kick">Want more?</p><h3>Where to go <span class="blue">next</span></h3><div class="next-row">{US}{nxt}</div></div>
      </div>
    </div></section>
    <section class="g-finish dk" id="notes">
      <div class="h-wrap g-finish__inner">
        <p class="kick">You hit the bottom</p>
        <h2>You're at <span class="blue">1</span></h2>
        <p class="g-finish__sub">Want what comes after 1? Get the notes: what we tried, what worked and what flopped.</p>
        <form class="h-form" action="/api/subscribe" method="post" data-notes novalidate>
          <div class="h-form__row">
            <label class="visually-hidden" for="notes-email">Email address</label>
            <input class="h-input" id="notes-email" name="email" type="email" inputmode="email" autocomplete="email" placeholder="Your email" required>
            <button class="h-btn" type="submit">Send me the notes</button>
          </div>
          <input class="notes__hp" name="website" type="text" tabindex="-1" autocomplete="off" aria-hidden="true">
          <p class="h-note">{e(NOTE)}</p>
          <p class="notes__status" data-notes-status role="status" aria-live="polite"></p>
        </form>
        <p class="g-small">Spot something out of date? Tell us at <a href="mailto:hi@outofourdepth.com">hi@outofourdepth.com</a>.</p>
      </div>
    </section>
  </main>
  <footer class="h-foot">
    <div class="h-wrap">
      <p class="h-foot__big" aria-hidden="true">AI for normal <span class="h-blue">people</span></p>
      <div class="h-foot__row">
        <nav class="h-foot__links" aria-label="Footer"><a href="/#episodes">Episodes</a><a href="/guide">Study guide</a><a href="mailto:hi@outofourdepth.com">hi@outofourdepth.com</a></nav>
        <nav class="h-foot__social topbar__social" aria-label="Find us" data-socials></nav>
      </div>
      <p class="h-foot__sign">{e(SIGN)}</p>
    </div>
  </footer>
  <script src="/config.js"></script>
  <script src="/main.js"></script>
  <script>
    document.querySelectorAll('[data-copy]').forEach(function (b) {{
      b.addEventListener('click', function () {{
        var t = document.getElementById(b.getAttribute('data-copy')).textContent;
        var done = function () {{ b.textContent = 'Copied! Go make something'; setTimeout(function () {{ b.textContent = 'Copy prompt'; }}, 2200); }};
        if (navigator.clipboard) navigator.clipboard.writeText(t).then(done, function () {{}}); else done();
      }});
    }});
    document.querySelectorAll('.mo').forEach(function (b) {{ b.addEventListener('click', function () {{ b.classList.toggle('on'); }}); }});
    document.querySelectorAll('.side').forEach(function (b) {{
      b.addEventListener('click', function () {{
        b.parentNode.querySelectorAll('.side').forEach(function (x) {{ x.classList.toggle('on', x === b); x.classList.toggle('off', x !== b); }});
      }});
    }});
    (function () {{
      var g = document.querySelector('.gauge'), links = g.querySelectorAll('a'), secs = [].slice.call(document.querySelectorAll('[data-depth]'));
      function u() {{
        var y = innerHeight * .4, cur = -1;
        secs.forEach(function (s, i) {{ if (s.getBoundingClientRect().top < y) cur = i; }});
        links.forEach(function (a, i) {{ a.classList.toggle('on', i === cur); }});
        g.classList.toggle('dk', cur >= 5); g.classList.toggle('show', cur >= 0);
      }}
      addEventListener('scroll', u, {{ passive: true }}); u();
      if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
      setInterval(function () {{
        var deep = secs.some(function (x, i) {{ var r = x.getBoundingClientRect(); return i >= 3 && r.top < innerHeight && r.bottom > 0; }});
        if (!deep || document.hidden) return;
        var b = document.createElement('i'), z = 6 + Math.random() * 10;
        b.className = 'bub'; b.style.left = (8 + Math.random() * 84) + 'vw'; b.style.width = b.style.height = z + 'px';
        document.body.appendChild(b); setTimeout(function () {{ b.remove(); }}, 6000);
      }}, 600);
    }})();
  </script>
</body>
</html>
'''
page = soften(page)
(WEB / 'guide.html').write_text(page)

# ---------- Render the PDF and the cover image ----------
from playwright.sync_api import sync_playwright
out = WEB / 'downloads' / 'ai-0-to-1-study-guide.pdf'
out.parent.mkdir(exist_ok=True)
# Chrome leaves page margins unpainted, so the header and footer paint them cream.
PAINT = '<style>html,body{margin:0;padding:0;-webkit-print-color-adjust:exact}#header,#footer{padding:0!important}</style>'
head = PAINT + '<div style="position:absolute;inset:0;width:100%;height:.6in;background:#FBF1E5"></div>'
foot = (PAINT + '<div style="position:absolute;left:0;right:0;bottom:0;height:.66in;background:#FBF1E5;'
        'font-family:Helvetica,Arial,sans-serif;font-size:7.5px;letter-spacing:1.2px;color:#4F6072;'
        'display:flex;justify-content:space-between;align-items:center;padding:0 .7in;box-sizing:border-box">'
        '<span>OUT OF OUR DEPTH  /  AI FROM 0 TO 1</span><span class="pageNumber"></span></div>')
import pypdf, io
with sync_playwright() as p:
    kw = {'executable_path': os.environ['CHROME']} if os.environ.get('CHROME') else {}
    b = p.chromium.launch(**kw)
    pg = b.new_page()
    pg.goto((SRC / 'study-guide.html').as_uri(), wait_until='networkidle')
    pg.evaluate('document.fonts.ready')
    # The cream header and footer would paint over the navy cover, so the cover prints on its own.
    cover = pg.pdf(print_background=True, prefer_css_page_size=True, page_ranges='1')
    rest = pg.pdf(print_background=True, prefer_css_page_size=True, display_header_footer=True,
                  header_template=head, footer_template=foot, page_ranges='2-')
    pg.set_viewport_size({'width': 816, 'height': 1056})
    pg.screenshot(path=str(SRC / 'cover.png'), clip={'x': 0, 'y': 0, 'width': 816, 'height': 1056})
    b.close()
w = pypdf.PdfWriter()
for part in (cover, rest):
    for page in pypdf.PdfReader(io.BytesIO(part)).pages:
        w.add_page(page)
w.add_metadata({'/Title': 'AI from 0 to 1: a free study guide', '/Author': 'Out of Our Depth (Mary and Josh)'})
with open(out, 'wb') as f:
    w.write(f)

from PIL import Image
Image.open(SRC / 'cover.png').convert('RGB').resize((612, 792), Image.LANCZOS).save(WEB / 'images' / 'guide-cover.webp', quality=88, method=6)
(SRC / 'cover.png').unlink()
print(f'Built website/guide.html and {out.relative_to(ROOT)} ({out.stat().st_size // 1024} KB): {N} words, {len(levels)} levels, {len(guide["debates"])} debates, {len(guide["ways"])} ways to start')
