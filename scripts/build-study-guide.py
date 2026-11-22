#!/usr/bin/env python3
"""Build the free "AI from 0 to 1" study guide: the /guide web page and the PDF.

Words come from website/learning-topics.json (the 35 from the old Learning list, wording unchanged) plus
the guide-only words in 03_ASSETS/study-guide/guide-levels.json, which also holds the levels, try-its,
check-yourself questions, Start building projects, If you get stuck tips and Where to go next.

    python3 scripts/build-study-guide.py

Writes website/guide.html, website/downloads/ai-0-to-1-study-guide.pdf, website/images/guide-cover.webp
and the print HTML at 03_ASSETS/study-guide/study-guide.html. Needs Python 3, Pillow and Playwright with
Chromium or Chrome (set CHROME=/path/to/chrome to pick one). Fonts load from Google Fonts at build time.

House style (Mary 2026-11-21): no divider lines, and no period after a phrase that isn't a full
sentence. "Think of it like" lines and level promises lose a final period unless they hold two sentences.
"""
import html, json, os, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / 'website'
SRC = ROOT / '03_ASSETS' / 'study-guide'
guide = json.loads((SRC / 'guide-levels.json').read_text())
topics = {t['id']: t for t in json.loads((WEB / 'learning-topics.json').read_text())}
topics.update(guide.get('extra_words', {}))
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
    ep = t.get('episode')
    if not ep:
        return '<span class="tag tag--off">Not on the show yet</span>'
    label = f"Ep {ep['number']} at {ep['time']}" if ep['time'] != '00:00' else f"All of ep {ep['number']}"
    return f'<a class="tag" href="{html.escape(ep_url(ep["number"], ep["time"]))}" target="_blank" rel="noopener">&#9654;&#xFE0E; {label}</a>'

SPARK = '<svg class="spark" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 1.5v21M2.9 6.75l18.2 10.5M2.9 17.25l18.2-10.5" stroke="currentColor" stroke-width="3.4" stroke-linecap="round"/></svg>'
slug = lambda n: 'level-' + n.replace('.', '-')

# ---------- shared pieces ----------
def word_card(t):
    aka = f'<span class="aka">{e(t["aka"])}</span>' if t.get('aka') else ''
    return (f'<article class="card word" id="{t["id"]}"><div class="tags">{tag(t)}</div>'
            f'<h3>{e(t["title"])}</h3>{aka}<p>{e(t["definition"])}</p>'
            f'<p class="think"><b>Think of it like</b> {e(phrase(t["think"]))}</p></article>')

def try_check(lv):
    tries = ''.join(f'<li>{e(x)}</li>' for x in lv['try'])
    checks = ''.join(f'<li>{e(x)}</li>' for x in lv['check'])
    return (f'<div class="pair"><div class="try"><p class="kick">{SPARK} Try it  /  about 10 minutes</p><ol>{tries}</ol></div>'
            f'<div class="check"><p class="kick">Check yourself</p><p class="hint">Say it out loud, like you\'re explaining it to a friend</p><ol>{checks}</ol></div></div>')

MAP = f'''<div class="map"><p class="kick">{SPARK} The whole thing on one page</p>
  <h3>Learn, look, think, act</h3>
  <p class="map-sub">Almost every AI headline is about one of these four steps. Figure out which one, and the news gets a lot less confusing.</p>
  <div class="map-row">
    <div><b>Learn</b><p>Training. The model reads a mountain of text and the patterns stick. Happens months before you ever open the app.</p><i>Training, GPUs, data centers, fine-tuning</i></div>
    <div><b>Look</b><p>Pulling in fresh info the moment you ask: a web search, your files, your inbox</p><i>RAG, deep research, MCP</i></div>
    <div><b>Think</b><p>Working out the answer, one token at a time, inside the context window</p><i>Tokens, context window, reasoning models</i></div>
    <div><b>Act</b><p>Doing something in the world: sending, booking, clicking, writing code</p><i>Agents, skills, computer use</i></div>
  </div></div>'''

def level_block(lv, i, wrap=''):
    words = ''.join(word_card(topics[w]) for w in lv['words'])
    return f'''<section class="level" id="{slug(lv["n"])}" aria-labelledby="{slug(lv["n"])}-t"><div class="{wrap}">
  <header class="lv-head"><span class="lv-n">{lv["n"]}</span><div><p class="kick">Level {i + 1} of {len(levels)}  /  {len(lv["words"])} words</p><h2 id="{slug(lv["n"])}-t">{e(lv["name"])}</h2><p class="promise">{e(phrase(lv["promise"]))}</p></div></header>
  <div class="cards">{words}</div>
  {try_check(lv)}
  {MAP if lv["n"] == "0.6" else ""}
</div></section>'''

def build_card(b, web):
    watch = f'<a class="tag" href="{html.escape(ep_url(b["watch"]))}" target="_blank" rel="noopener">&#9654;&#xFE0E; Watch ep {b["watch"]}</a>' if b.get('watch') else ''
    copy = f'<button class="copy" type="button" data-copy="p-{b["id"]}">Copy prompt</button>' if web else ''
    return (f'<article class="card build"><div class="tags"><span class="tag tag--solid">{e(b["time"])}</span><span class="tag tag--off">{e(b["level"])}</span>{watch}</div>'
            f'<h3>{e(b["title"])}</h3><p>{e(b["why"])}</p>'
            f'<div class="prompt"><p class="kick">Copy this</p><p id="p-{b["id"]}">{e(b["prompt"])}</p>{copy}</div></article>')

sh = guide['start_here']
start_steps = ''.join(f'<li>{e(s)}</li>' for s in sh['steps'])
START = f'''<div class="card start"><span class="badge">{SPARK} Start here</span>
  <h2>{e(sh["title"])}</h2><p class="start-time">{e(sh["time"])}</p>
  <ol class="steps">{start_steps}</ol>
  <p class="tenhours"><b>The ten-hour rule</b> {e(guide["ten_hours"])}</p></div>'''

builds = ''.join(build_card(b, True) for b in guide['builds'])
builds_pdf = ''.join(build_card(b, False) for b in guide['builds'])
stuck = ''.join(f'<p><b>{e(phrase(a))}</b> {e(b)}</p>' for a, b in guide['stuck'])
nxt = ''.join(f'<a class="card next" href="{html.escape(u)}" target="_blank" rel="noopener"><span class="tag tag--off">{e(who)}</span><h3>{e(t)}</h3><p>{e(len_)}</p></a>' for t, who, len_, u in guide['next'])
boxes = ''.join(f'<li>{e(topics[w]["title"])}</li>' for lv in levels for w in lv['words'])
NOTE = "We only email when we've got something worth writing. Written by us, not AI."
edition = guide['edition']
month = edition.replace(' edition', '')

# ---------- PDF ----------
sticker = (WEB / 'images' / 'hosts-sticker.webp').as_uri()
toc = ''.join(f'<li><span class="toc-n">{lv["n"]}</span><span class="toc-name">{e(lv["name"])}</span><span class="toc-p">{e(phrase(lv["promise"]))}</span></li>' for lv in levels)

PDF_CSS = '''
@page { size: letter; margin: .55in 0 .62in; }
@page :first { margin: 0; }
:root { --cream:#FBF1E5; --foam:#FDF8F2; --navy:#0B2A45; --muted:#4F6072; --blue:#38B6FF; --ink:#0A6BB8; --sky:#BDE5FF; --dash:#CDBBA4; }
html { background: var(--cream); }
body { margin:0; padding:0 .7in; color:var(--navy); font-family:Teachers, sans-serif; font-size:10.5pt; line-height:1.4; -webkit-print-color-adjust:exact; print-color-adjust:exact; }
.kick { font-family:'JetBrains Mono', monospace; font-size:7.5pt; letter-spacing:.14em; text-transform:uppercase; color:var(--ink); margin:0 0 5pt; display:flex; align-items:center; gap:5pt; }
.spark { width:9pt; height:9pt; color:var(--blue); flex:none; }
h1,h2,h3 { font-weight:800; text-transform:uppercase; margin:0; line-height:.95; }
a { color:var(--ink); text-decoration:none; }
.card { background:var(--foam); border-radius:12pt; padding:8pt 10pt; break-inside:avoid; }
.tags { display:flex; flex-wrap:wrap; gap:4pt; margin-bottom:5pt; }
.tag { display:inline-block; font-family:'JetBrains Mono', monospace; font-size:6.5pt; letter-spacing:.08em; text-transform:uppercase; padding:3pt 6pt; border-radius:5pt; background:var(--sky); color:var(--navy); }
.tag--off { background:var(--cream); color:var(--muted); }
.tag--solid { background:var(--navy); color:var(--cream); }
.aka { display:block; font-family:'JetBrains Mono', monospace; font-size:7pt; letter-spacing:.05em; color:var(--muted); margin-top:2pt; }
.word h3, .build h3, .next h3 { font-size:12.5pt; }
.word p, .build p { margin:3pt 0 0; font-size:9.8pt; line-height:1.35; }
.think { color:var(--muted); font-size:9pt !important; }
.think b { color:var(--navy); }
/* cover */
.cover { margin:0 -.7in; height:11in; box-sizing:border-box; padding:.75in .8in .7in; display:flex; flex-direction:column; align-items:center; text-align:center; page-break-after:always; }
.cover .brand { font-weight:800; text-transform:uppercase; line-height:.9; font-size:12pt; align-self:flex-start; text-align:left; }
.cover .brand b { display:block; font-size:24pt; }
.cover .badge { margin-top:.6in; }
.badge { display:inline-flex; align-items:center; gap:5pt; background:var(--navy); color:var(--cream); font-family:'JetBrains Mono', monospace; font-size:7.5pt; letter-spacing:.12em; text-transform:uppercase; padding:5pt 9pt; border-radius:6pt; }
.cover h1 { font-size:64pt; margin-top:14pt; }
.cover h1 span { color:var(--blue); display:inline-flex; align-items:center; gap:10pt; font-size:120pt; line-height:.86; }
.cover h1 .spark { width:56pt; height:56pt; }
.cover .sub { font-size:16pt; margin:16pt 0 0; max-width:5.3in; }
.cover img { width:4.2in; margin-top:.45in; transform:rotate(-2deg); }
.cover .by { margin-top:auto; font-family:'JetBrains Mono', monospace; font-size:8pt; letter-spacing:.14em; text-transform:uppercase; color:var(--muted); }
/* intro */
.intro { page-break-after:always; }
.start { padding:16pt 18pt; margin-bottom:22pt; }
.start h2 { font-size:26pt; margin-top:10pt; }
.start-time { font-family:'JetBrains Mono', monospace; font-size:8pt; letter-spacing:.12em; text-transform:uppercase; color:var(--ink); margin:5pt 0 8pt; }
.steps { margin:0; padding-left:16pt; font-size:11pt; }
.steps li { margin-bottom:5pt; }
.tenhours { margin:12pt 0 0; background:var(--cream); border-radius:10pt; padding:9pt 11pt; font-size:10pt; color:var(--muted); }
.tenhours b { color:var(--navy); margin-right:3pt; }
.toc { list-style:none; margin:0; padding:0; display:grid; gap:5pt; }
.toc li { display:grid; grid-template-columns:.75in 1.9in 1fr; align-items:center; gap:10pt; padding:7pt 12pt; background:var(--foam); border-radius:10pt; }
.toc-n { font-weight:800; font-size:20pt; color:var(--blue); }
.toc-name { font-weight:800; text-transform:uppercase; font-size:12pt; }
.toc-p { font-size:10pt; color:var(--muted); }
.toc li.extra .toc-n .spark { width:16pt; height:16pt; }
/* levels */
.level { page-break-before:always; }
.lv-head { display:grid; grid-template-columns:auto 1fr; gap:14pt; align-items:end; margin-bottom:10pt; }
.lv-n { font-weight:800; font-size:52pt; line-height:.78; color:var(--blue); }
.lv-head h2 { font-size:24pt; }
.promise { margin:4pt 0 0; font-size:11pt; color:var(--muted); }
.cards { display:grid; grid-template-columns:1fr 1fr; gap:6pt; }
.pair { display:grid; grid-template-columns:1fr 1fr; gap:6pt; margin-top:8pt; break-inside:avoid; }
.try { background:var(--navy); color:var(--cream); border-radius:12pt; padding:9pt 11pt; }
.try .kick { color:var(--sky); }
.check { background:var(--sky); border-radius:12pt; padding:9pt 11pt; }
.check .kick { color:var(--navy); }
.pair ol { margin:0; padding-left:14pt; font-size:9.2pt; line-height:1.35; }
.pair li { margin-bottom:3pt; }
.hint { font-size:9pt; color:var(--muted); margin:0 0 5pt; }
.map { margin-top:18pt; break-inside:avoid; }
.map h3 { font-size:22pt; }
.map-sub { margin:4pt 0 9pt; color:var(--muted); }
.map-row { display:grid; grid-template-columns:repeat(4,1fr); gap:8pt; }
.map-row div { background:var(--foam); border-radius:12pt; padding:10pt; }
.map-row b { display:block; font-weight:800; text-transform:uppercase; font-size:14pt; margin-bottom:3pt; color:var(--blue); }
.map-row p { margin:0 0 5pt; font-size:9pt; }
.map-row i { font-style:normal; font-family:'JetBrains Mono', monospace; font-size:6.5pt; letter-spacing:.05em; text-transform:uppercase; color:var(--ink); }
/* builds */
.builds-sec { page-break-before:always; }
.sec-head h2 { font-size:34pt; display:flex; align-items:center; gap:8pt; }
.sec-head h2 .spark { width:24pt; height:24pt; }
.sec-head p { margin:6pt 0 12pt; font-size:11.5pt; color:var(--muted); max-width:6in; }
.prompt { margin-top:8pt; background:var(--cream); border:1.2px dashed var(--dash); border-radius:10pt; padding:8pt 10pt; }
.prompt .kick { margin-bottom:3pt; }
.prompt p { margin:0; font-size:9.5pt; }
/* stuck, next, finish */
.finish { page-break-before:always; }
.stuck h2, .nexts h2, .done h2 { font-size:24pt; margin-bottom:8pt; }
.stuck p { margin:0 0 6pt; }
.stuck b { font-weight:800; margin-right:3pt; }
.nexts { margin-top:18pt; }
.next-row { display:grid; grid-template-columns:repeat(3,1fr); gap:8pt; }
.next h3 { font-size:13pt; margin-top:2pt; }
.next p { margin:4pt 0 0; font-size:9.5pt; color:var(--muted); }
.done { margin-top:18pt; }
.done h2 span { color:var(--blue); }
.boxes { columns:3; column-gap:14pt; list-style:none; margin:6pt 0 12pt; padding:0; }
.boxes li { break-inside:avoid; padding:2.5pt 0 2.5pt 15pt; position:relative; font-size:9.5pt; }
.boxes li::before { content:''; position:absolute; left:0; top:4.5pt; width:8pt; height:8pt; border:1.2pt solid var(--navy); border-radius:2pt; }
.sign { font-family:'JetBrains Mono', monospace; font-size:7.5pt; letter-spacing:.12em; text-transform:uppercase; color:var(--muted); margin-top:8pt; }
'''

pdf = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><title>AI from 0 to 1 | Out of Our Depth</title>
<link href="https://fonts.googleapis.com/css2?family=Teachers:wght@400..800&family=JetBrains+Mono:wght@400;700&display=block" rel="stylesheet">
<style>{PDF_CSS}</style></head><body>
<section class="cover">
  <div class="brand">Out of our<b>Depth</b></div>
  <span class="badge">{SPARK} Free study guide  /  {e(edition)}</span>
  <h1>AI from<br><span>0 to 1 {SPARK}</span></h1>
  <p class="sub">The {N} words and ideas you need to actually get AI, plus eight fun things to build first</p>
  <img src="{sticker}" alt="">
  <p class="by">Mary and Josh  /  outofourdepth.com/guide</p>
</section>
<section class="intro">
  {START}
  <p class="kick">What's inside</p>
  <ol class="toc">{toc}<li class="extra"><span class="toc-n">{SPARK}</span><span class="toc-name">Start building</span><span class="toc-p">Eight fun first projects with prompts to copy</span></li><li class="extra"><span class="toc-n">{SPARK}</span><span class="toc-name">If you get stuck</span><span class="toc-p">Quick fixes, where to go next and your checklist</span></li></ol>
</section>
{''.join(level_block(lv, i) for i, lv in enumerate(levels))}
<section class="builds-sec">
  <div class="sec-head"><p class="kick">Steal our homework</p><h2>Start building {SPARK}</h2><p>The fastest way to learn AI is to make something with it. Pick one, paste the prompt into any AI app, and fill in the [brackets].</p></div>
  <div class="cards">{builds_pdf}</div>
</section>
<section class="finish">
  <div class="stuck"><p class="kick">{SPARK} Happens to everyone</p><h2>If you get stuck</h2>{stuck}</div>
  <div class="nexts"><p class="kick">Want more?</p><h2>Where to go next</h2><div class="next-row">{nxt}</div></div>
  <div class="done"><p class="kick">Level 1.0, done</p><h2>You're at <span>1</span></h2><p>Check off every word you could explain to a friend.</p><ul class="boxes">{boxes}</ul>
  <p>Watch the show at <a href="https://outofourdepth.com/youtube">outofourdepth.com/youtube</a>. Get the notes at <a href="https://outofourdepth.com">outofourdepth.com</a>. {e(NOTE)} Which word still confuses you? Tell us at <a href="mailto:hi@outofourdepth.com">hi@outofourdepth.com</a></p>
  <p class="sign">AI changes fast. Model names here are current as of {e(month)}. Built with AI, argued over by humans</p></div>
</section>
</body></html>'''
(SRC / 'study-guide.html').write_text(pdf)

# ---------- Web page ----------
jump = ('<a href="#start-here">Start here</a>' +
        ''.join(f'<a href="#{slug(lv["n"])}"><b>{lv["n"]}</b> {e(lv["name"])}</a>' for lv in levels) +
        '<a href="#start-building">Start building</a><a href="#stuck">If you get stuck</a>')
PDF_URL = '/downloads/ai-0-to-1-study-guide.pdf'
page = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AI from 0 to 1: a free study guide | Out of Our Depth</title>
  <meta name="description" content="The {N} AI words and ideas you need, in six short levels from 0 to 1, plus eight fun first builds with prompts to copy. Free, by Mary and Josh of Out of Our Depth.">
  <meta name="theme-color" content="#FBF1E5">
  <link rel="canonical" href="https://outofourdepth.com/guide">
  <meta property="og:type" content="article">
  <meta property="og:url" content="https://outofourdepth.com/guide">
  <meta property="og:title" content="AI from 0 to 1: a free study guide">
  <meta property="og:description" content="The {N} AI words you need, six short levels and eight fun first builds. Free, no sign-up.">
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
  <a class="skip-link" href="#start-here">Skip to Start here</a>
  <header class="h-nav">
    <div class="h-wrap h-nav__inner">
      <a class="h-wm" href="/" aria-label="Out of Our Depth home"><span class="h-wm__k">Out of our</span><span>Depth</span></a>
      <nav class="h-links" aria-label="Main"><a href="/#episodes">Episodes</a><a href="/guide#start-building">Try it</a><a href="/guide" aria-current="page">Study guide</a></nav>
      <a class="h-btn h-btn--sm" href="https://www.youtube.com/@OutOfOurDepthPod" data-link="youtube" target="_blank" rel="noopener">Watch the show</a>
    </div>
  </header>
  <main>
    <section class="g-hero">
      <div class="h-wrap g-hero__inner">
        <span class="badge">{SPARK} Free, no sign-up needed</span>
        <h1><span class="g-hero__kick">AI from</span><span class="g-hero__big">0 to 1 {SPARK}</span></h1>
        <p class="g-hero__sub">The {N} words and ideas you need to actually get AI, explained the way we explain them to each other. Six short levels, then eight fun things to build.</p>
        <div class="g-hero__ctas"><a class="h-btn" href="#start-here">Start reading</a><a class="h-btn h-btn--ghost" href="{PDF_URL}" download>Download the PDF</a></div>
        <img class="g-hero__hosts" src="/images/hosts-sticker-640.webp" width="640" height="421" alt="Mary and Josh">
      </div>
    </section>
    <nav class="g-jump h-wrap" aria-label="Sections">{jump}</nav>
    <section class="g-start h-wrap" id="start-here">{START}</section>
    {''.join(level_block(lv, i, 'h-wrap') for i, lv in enumerate(levels))}
    <section class="level g-builds" id="start-building"><div class="h-wrap">
      <div class="sec-head"><p class="kick">{SPARK} Steal our homework</p><h2>Start building</h2><p>The fastest way to learn AI is to make something with it. Pick one, paste the prompt into any AI app, and fill in the [brackets].</p></div>
      <div class="cards">{builds}</div>
    </div></section>
    <section class="level g-stuck" id="stuck"><div class="h-wrap g-narrow">
      <p class="kick">{SPARK} Happens to everyone</p><h2>If you get stuck</h2>
      {stuck}
    </div></section>
    <section class="level g-next"><div class="h-wrap">
      <p class="kick">Want more?</p><h2>Where to go next</h2>
      <div class="next-row">{nxt}<a class="card next" href="https://www.youtube.com/@OutOfOurDepthPod" target="_blank" rel="noopener"><span class="tag tag--off">Us</span><h3>Out of Our Depth</h3><p>New episodes every week</p></a></div>
    </div></section>
    <section class="g-finish" id="notes">
      <div class="h-wrap g-finish__inner">
        <p class="kick">Level 1.0, done</p>
        <h2>You're at <span class="h-blue">1</span></h2>
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
        <p class="g-small">Spot something out of date? Tell us at <a href="mailto:hi@outofourdepth.com">hi@outofourdepth.com</a>. AI changes fast. Model names here are current as of {e(month)}.</p>
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
      <p class="h-foot__sign">Built with AI, argued over by humans</p>
    </div>
  </footer>
  <script src="/config.js"></script>
  <script src="/main.js"></script>
  <script>
    document.querySelectorAll('[data-copy]').forEach(function (b) {{
      b.addEventListener('click', function () {{
        var t = document.getElementById(b.getAttribute('data-copy')).textContent;
        var done = function () {{ b.textContent = 'Copied'; setTimeout(function () {{ b.textContent = 'Copy prompt'; }}, 1600); }};
        if (navigator.clipboard) navigator.clipboard.writeText(t).then(done, function () {{}}); else done();
      }});
    }});
  </script>
</body>
</html>
'''
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
with sync_playwright() as p:
    kw = {'executable_path': os.environ['CHROME']} if os.environ.get('CHROME') else {}
    b = p.chromium.launch(**kw)
    pg = b.new_page()
    pg.goto((SRC / 'study-guide.html').as_uri(), wait_until='networkidle')
    pg.evaluate('document.fonts.ready')
    pg.pdf(path=str(out), print_background=True, prefer_css_page_size=True, display_header_footer=True,
           header_template=head, footer_template=foot)
    pg.set_viewport_size({'width': 816, 'height': 1056})
    pg.screenshot(path=str(SRC / 'cover.png'), clip={'x': 0, 'y': 0, 'width': 816, 'height': 1056})
    b.close()

from PIL import Image
Image.open(SRC / 'cover.png').convert('RGB').resize((612, 792), Image.LANCZOS).save(WEB / 'images' / 'guide-cover.webp', quality=88, method=6)
(SRC / 'cover.png').unlink()
print(f'Built website/guide.html and {out.relative_to(ROOT)} ({out.stat().st_size // 1024} KB): {N} words, {len(levels)} levels, {len(guide["builds"])} builds')
