#!/usr/bin/env python3
"""Build the free "AI from 0 to 1" study guide PDF for outofourdepth.com/guide.

Words come from website/learning-topics.json (the same 35 the Learning list used, unchanged).
Levels, try-its and check-yourself questions come from 03_ASSETS/study-guide/guide-levels.json.

    python3 scripts/build-study-guide.py

Writes website/guide.html (the guide as a web page), website/downloads/ai-0-to-1-study-guide.pdf, a cover preview at
website/images/guide-cover.webp, and the print HTML at 03_ASSETS/study-guide/study-guide.html.
Needs Python 3, Pillow and Playwright with a Chromium or Chrome (set CHROME=/path to pick one).
Fonts load from Google Fonts at build time, so no font files live in Git.
"""
import html, json, os, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / 'website'
SRC = ROOT / '03_ASSETS' / 'study-guide'
topics = {t['id']: t for t in json.loads((WEB / 'learning-topics.json').read_text())}
guide = json.loads((SRC / 'guide-levels.json').read_text())
levels = guide['levels']

# Public episode ids, kept in one place: the Learning build script.
yt = dict(re.findall(r"'(\d{3})':\s*'([^']+)'", (ROOT / 'scripts' / 'build-learning.js').read_text()))

used = [w for lv in levels for w in lv['words']]
missing = set(topics) - set(used)
if missing or len(used) != len(set(used)):
    sys.exit(f'every word must appear exactly once; missing {sorted(missing)}')

BANNED = ['—', '–', '·', '…', '“', '”', '‘', '’']
def check(text):
    for ch in BANNED:
        if ch in text:
            sys.exit(f'house style: no dashes, dots, ellipses or curly quotes. Found {ch!r} in: {text}')
    return text

e = lambda s: html.escape(check(s), quote=True)

def watch(t):
    ep = t.get('episode')
    if not ep:
        return '<span class="watch off">Not on the show yet</span>'
    m, s = map(int, ep['time'].split(':'))
    secs = m * 60 + s
    url = f"https://www.youtube.com/watch?v={yt[ep['number']]}" + (f'&t={secs}' if secs else '')
    label = f"Watch us explain it: ep {ep['number']} at {ep['time']}" if secs else f"Watch all of ep {ep['number']}"
    return f'<a class="watch" href="{html.escape(url)}">{label}</a>'

def word(t):
    aka = f'<span class="aka">{e(t["aka"])}</span>' if t.get('aka') else ''
    return f'''<article class="word">
  <h3>{e(t["title"])}{aka}</h3>
  <p class="def">{e(t["definition"])}</p>
  <p class="think"><b>Think of it like</b> {e(t["think"])}</p>
  {watch(t)}
</article>'''

MAP = '''<div class="map"><p class="kick">The whole thing on one page</p>
  <h3>Learn, look, think, act</h3>
  <p class="map-sub">Almost every AI headline is about one of these four steps. Figure out which one, and the news gets a lot less confusing.</p>
  <div class="map-row">
    <div><b>Learn</b><p>Training. The model reads a mountain of text and the patterns stick. Happens once, months before you ever open the app.</p><i>Training, GPUs, data centers, fine-tuning</i></div>
    <div><b>Look</b><p>Pulling in fresh info at the moment you ask: a web search, your files, your inbox.</p><i>RAG, deep research, MCP</i></div>
    <div><b>Think</b><p>Working out the answer, one token at a time, inside the context window.</p><i>Tokens, context window, reasoning models</i></div>
    <div><b>Act</b><p>Doing something in the world: sending, booking, clicking, writing code.</p><i>Agents, skills, computer use</i></div>
  </div></div>'''

def level(lv, i):
    words = '\n'.join(word(topics[w]) for w in lv['words'])
    tries = ''.join(f'<li>{e(x)}</li>' for x in lv['try'])
    checks = ''.join(f'<li>{e(x)}</li>' for x in lv['check'])
    return f'''<section class="level">
  <header class="lv-head">
    <div class="lv-n">{lv["n"]}</div>
    <div><p class="kick">Level {i + 1} of {len(levels)}  /  {len(lv["words"])} words</p>
    <h2>{e(lv["name"])}</h2><p class="promise">{e(lv["promise"])}</p></div>
  </header>
  <div class="words">{words}</div>
  <div class="pair">
    <div class="try"><p class="kick">Try it  /  about 10 minutes</p><ol>{tries}</ol></div>
    <div class="check"><p class="kick">Check yourself</p><p class="hint">Say the answer out loud, like you're explaining it to a friend.</p><ol>{checks}</ol></div>
  </div>
  {MAP if lv["n"] == "0.6" else ""}
</section>'''

toc = ''.join(f'<li><span class="toc-n">{lv["n"]}</span><span class="toc-name">{e(lv["name"])}</span><span class="toc-p">{e(lv["promise"])}</span></li>' for lv in levels)
boxes = ''.join(f'<li>{e(topics[w]["title"])}</li>' for lv in levels for w in lv['words'])
sticker = (WEB / 'images' / 'hosts-sticker.webp').as_uri()

doc = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><title>AI from 0 to 1 | Out of Our Depth</title>
<link href="https://fonts.googleapis.com/css2?family=Teachers:wght@400..800&family=JetBrains+Mono:wght@400;700&display=block" rel="stylesheet">
<style>
@page {{ size: letter; margin: .55in 0 .62in; }}
@page :first {{ margin: 0; }}
:root {{ --cream:#FBF1E5; --foam:#FDF8F2; --navy:#0B2A45; --muted:#3C5A73; --blue:#38B6FF; --ink:#0E6FC0; --line:#E6D8C6; }}
html {{ background: var(--cream); }}
body {{ margin:0; padding:0 .7in; color:var(--navy); font-family:Teachers, sans-serif; font-size:11pt; line-height:1.4; -webkit-print-color-adjust:exact; print-color-adjust:exact; }}
.kick {{ font-family:'JetBrains Mono', monospace; font-size:8pt; letter-spacing:.16em; text-transform:uppercase; color:var(--ink); margin:0 0 6pt; }}
h1,h2,h3 {{ font-weight:800; text-transform:uppercase; margin:0; line-height:.95; letter-spacing:-.005em; }}
a {{ color:var(--ink); }}
/* cover */
.cover {{ margin:0 -.7in; height:11in; box-sizing:border-box; padding:.75in .8in .7in; display:flex; flex-direction:column; align-items:center; text-align:center; page-break-after:always; }}
.cover .brand {{ font-weight:800; text-transform:uppercase; line-height:.9; font-size:12pt; align-self:flex-start; text-align:left; }}
.cover .brand b {{ display:block; font-size:24pt; }}
.cover .free {{ margin-top:.55in; }}
.cover h1 {{ font-size:66pt; margin-top:8pt; }}
.cover h1 span {{ color:var(--blue); display:block; font-size:118pt; line-height:.86; }}
.cover .sub {{ font-size:17pt; margin:16pt 0 0; max-width:5.4in; }}
.cover img {{ width:4.3in; margin-top:.5in; }}
.cover .by {{ margin-top:auto; font-family:'JetBrains Mono', monospace; font-size:8.5pt; letter-spacing:.14em; text-transform:uppercase; color:var(--muted); }}
/* intro */
.intro {{ page-break-after:always; }}
.intro h2 {{ font-size:32pt; margin-bottom:10pt; }}
.intro .lede {{ font-size:13pt; max-width:6.2in; margin:0 0 14pt; }}
.how {{ display:grid; grid-template-columns:repeat(3,1fr); gap:12pt; margin:0 0 18pt; }}
.how div {{ background:var(--foam); border:1px solid var(--line); border-radius:10pt; padding:12pt; }}
.how b {{ display:block; font-weight:800; text-transform:uppercase; font-size:12pt; margin-bottom:4pt; }}
.how p {{ margin:0; font-size:10.5pt; color:var(--muted); }}
.toc {{ list-style:none; margin:0; padding:0; border-top:1.5pt solid var(--navy); }}
.toc li {{ display:grid; grid-template-columns:.8in 1.9in 1fr; align-items:baseline; gap:10pt; padding:6pt 0; border-bottom:1px solid var(--line); }}
.toc-n {{ font-weight:800; font-size:21pt; color:var(--blue); }}
.toc-name {{ font-weight:800; text-transform:uppercase; font-size:13pt; }}
.toc-p {{ font-size:10.5pt; color:var(--muted); }}
.note {{ font-size:9.5pt; color:var(--muted); margin-top:14pt; }}
/* levels */
.level {{ page-break-before:always; }}
.lv-head {{ display:grid; grid-template-columns:auto 1fr; gap:16pt; align-items:end; padding-bottom:10pt; border-bottom:1.5pt solid var(--navy); margin-bottom:4pt; }}
.lv-n {{ font-weight:800; font-size:64pt; line-height:.78; color:var(--blue); }}
.lv-head h2 {{ font-size:27pt; }}
.promise {{ margin:4pt 0 0; font-size:11.5pt; color:var(--muted); }}
.words {{ columns:2; column-gap:16pt; }}
.word {{ break-inside:avoid; padding:7pt 0 7pt; border-bottom:1px solid var(--line); }}
.word h3 {{ font-size:13.5pt; margin-bottom:3pt; }}
.aka {{ font-family:'JetBrains Mono', monospace; font-weight:400; text-transform:none; font-size:7.5pt; letter-spacing:.06em; color:var(--muted); margin-left:6pt; vertical-align:2pt; }}
.def {{ margin:0 0 3pt; }}
.think {{ margin:0 0 3pt; font-size:10pt; color:var(--muted); }}
.think b {{ font-weight:700; color:var(--navy); }}
.watch {{ font-family:'JetBrains Mono', monospace; font-size:7.5pt; letter-spacing:.08em; text-transform:uppercase; text-decoration:none; }}
.watch::before {{ content:'\\25B6\\FE0E  '; font-size:6.5pt; }}
.watch.off {{ color:#8A9AA8; }} .watch.off::before {{ content:''; }}
.pair {{ display:grid; grid-template-columns:1fr 1fr; gap:12pt; margin-top:12pt; break-inside:avoid; }}
.try {{ background:var(--navy); color:var(--cream); border-radius:10pt; padding:11pt 13pt; }}
.try .kick {{ color:var(--blue); }}
.check {{ background:var(--foam); border:1px solid var(--line); border-radius:10pt; padding:11pt 13pt; }}
.pair ol {{ margin:0; padding-left:15pt; font-size:10pt; }}
.pair li {{ margin-bottom:4pt; }} .pair li:last-child {{ margin-bottom:0; }}
.hint {{ font-size:9.5pt; color:var(--muted); margin:0 0 6pt; }}
/* map */
.map {{ margin-top:26pt; break-inside:avoid; }}
.map h3 {{ font-size:24pt; }}
.map-sub {{ margin:5pt 0 12pt; color:var(--muted); max-width:5.8in; }}
.map-row {{ display:grid; grid-template-columns:repeat(4,1fr); gap:10pt; }}
.map-row div {{ border-top:4pt solid var(--blue); background:var(--foam); border-radius:0 0 10pt 10pt; padding:10pt 11pt; }}
.map-row b {{ display:block; font-weight:800; text-transform:uppercase; font-size:15pt; margin-bottom:4pt; }}
.map-row p {{ margin:0 0 6pt; font-size:10pt; }}
.map-row i {{ font-style:normal; font-family:'JetBrains Mono', monospace; font-size:7pt; letter-spacing:.06em; text-transform:uppercase; color:var(--ink); }}
/* finish */
.finish {{ page-break-before:always; }}
.finish h2 {{ font-size:40pt; }} .finish h2 span {{ color:var(--blue); }}
.finish .lede {{ font-size:13pt; margin:10pt 0 14pt; max-width:6in; }}
.boxes {{ columns:3; column-gap:14pt; list-style:none; margin:0 0 20pt; padding:0; }}
.boxes li {{ break-inside:avoid; padding:3.5pt 0 3.5pt 18pt; position:relative; font-size:10.5pt; border-bottom:1px solid var(--line); }}
.boxes li::before {{ content:''; position:absolute; left:0; top:6pt; width:9pt; height:9pt; border:1.3pt solid var(--navy); border-radius:2pt; }}
.next {{ display:grid; grid-template-columns:repeat(3,1fr); gap:12pt; }}
.next div {{ background:var(--foam); border:1px solid var(--line); border-radius:10pt; padding:12pt; }}
.next b {{ display:block; font-weight:800; text-transform:uppercase; font-size:12pt; margin-bottom:4pt; }}
.next p {{ margin:0; font-size:10.5pt; }}
.sign {{ margin-top:18pt; font-family:'JetBrains Mono', monospace; font-size:8pt; letter-spacing:.12em; text-transform:uppercase; color:var(--muted); }}
</style></head><body>
<section class="cover">
  <div class="brand">Out of our<b>Depth</b></div>
  <p class="kick free">Free study guide  /  {e(guide["edition"])}</p>
  <h1>AI from <span>0 to 1</span></h1>
  <p class="sub">The 35 words and ideas you need to actually get AI, explained the way we explain them to each other.</p>
  <img src="{sticker}" alt="">
  <p class="by">Mary and Josh  /  outofourdepth.com</p>
</section>
<section class="intro">
  <p class="kick">Start here</p>
  <h2>You don't need to be technical</h2>
  <p class="lede">We're Mary and Josh. We started the show because AI kept moving faster than we could keep up. This is the guide we wish someone had handed us: six short levels, from "what even is this" to the big debates.</p>
  <div class="how">
    <div><b>Read</b><p>Each word gets one plain-English line and something to think of it like.</p></div>
    <div><b>Try</b><p>Every level ends with about 10 minutes of hands-on stuff. Any AI app works.</p></div>
    <div><b>Say it</b><p>Answer the check-yourself questions out loud. If you can explain it, you've got it.</p></div>
  </div>
  <p class="kick">The six levels</p>
  <ol class="toc">{toc}</ol>
  <p class="note">AI changes fast. Model names and features here are current as of November 2026. When a word links to an episode, tap it to watch us explain it.</p>
</section>
{''.join(level(lv, i) for i, lv in enumerate(levels))}
<section class="finish">
  <p class="kick">Level 1.0, done</p>
  <h2>You're at <span>1</span></h2>
  <p class="lede">Check off every word you could explain to a friend. Anything left unchecked, go back and try it once more.</p>
  <ul class="boxes">{boxes}</ul>
  <div class="next">
    <div><b>Watch the show</b><p>New episodes every week.<br><a href="https://outofourdepth.com/youtube">outofourdepth.com/youtube</a></p></div>
    <div><b>Get the notes</b><p>We only email when we've got something worth writing. Written by us, not AI.<br><a href="https://outofourdepth.com">outofourdepth.com</a></p></div>
    <div><b>Tell us</b><p>Which word still confuses you?<br><a href="mailto:hi@outofourdepth.com">hi@outofourdepth.com</a></p></div>
  </div>
  <p class="sign">Built with AI, argued over by humans.</p>
</section>
</body></html>'''

(SRC / 'study-guide.html').write_text(doc)

from playwright.sync_api import sync_playwright
out = WEB / 'downloads' / 'ai-0-to-1-study-guide.pdf'
out.parent.mkdir(exist_ok=True)
# Chrome leaves page margins unpainted, so the header and footer paint them cream.
PAINT = '<style>html,body{margin:0;padding:0;-webkit-print-color-adjust:exact}#header,#footer{padding:0!important}</style>'
head = PAINT + '<div style="position:absolute;inset:0;width:100%;height:.6in;background:#FBF1E5"></div>'
foot = (PAINT + '<div style="position:absolute;left:0;right:0;bottom:0;height:.66in;background:#FBF1E5;'
        'font-family:Helvetica,Arial,sans-serif;font-size:7.5px;letter-spacing:1.2px;color:#3C5A73;'
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
    # Cover preview for the website
    pg.set_viewport_size({'width': 816, 'height': 1056})
    pg.screenshot(path=str(SRC / 'cover.png'), clip={'x': 0, 'y': 0, 'width': 816, 'height': 1056})
    b.close()

from PIL import Image
Image.open(SRC / 'cover.png').convert('RGB').resize((612, 792), Image.LANCZOS).save(WEB / 'images' / 'guide-cover.webp', quality=88, method=6)
(SRC / 'cover.png').unlink()

# ---------- The same guide as a web page: website/guide.html ----------
def wword(t):
    aka = f' <span class="g-aka">{e(t["aka"])}</span>' if t.get('aka') else ''
    w = watch(t).replace('class="watch"', 'class="g-watch" target="_blank" rel="noopener"').replace('class="watch off"', 'class="g-watch g-watch--off"')
    return f'<article class="g-word" id="{t["id"]}"><h3>{e(t["title"])}{aka}</h3><p>{e(t["definition"])}</p><p class="g-think"><b>Think of it like</b> {e(t["think"])}</p>{w}</article>'

WMAP = MAP.replace('class="map"', 'class="g-map"').replace('class="kick"', 'class="h-mono"').replace('class="map-sub"', 'class="g-map__sub"').replace('class="map-row"', 'class="g-map__row"')

def wlevel(lv, i):
    words = ''.join(wword(topics[w]) for w in lv['words'])
    tries = ''.join(f'<li>{e(x)}</li>' for x in lv['try'])
    checks = ''.join(f'<li>{e(x)}</li>' for x in lv['check'])
    slug = 'level-' + lv['n'].replace('.', '-')
    return f"""<section class="g-level" id="{slug}" aria-labelledby="{slug}-t">
  <div class="h-wrap">
    <header class="g-lv-head"><span class="g-lv-n">{lv["n"]}</span><div><p class="h-mono">Level {i + 1} of {len(levels)}  /  {len(lv["words"])} words</p><h2 id="{slug}-t">{e(lv["name"])}</h2><p class="g-promise">{e(lv["promise"])}</p></div></header>
    <div class="g-words">{words}</div>
    <div class="g-pair"><div class="g-try"><p class="h-mono">Try it  /  about 10 minutes</p><ol>{tries}</ol></div><div class="g-check"><p class="h-mono">Check yourself</p><p class="g-hint">Say the answer out loud, like you're explaining it to a friend.</p><ol>{checks}</ol></div></div>
    {WMAP if lv["n"] == "0.6" else ""}
  </div>
</section>"""

jump = ''.join(f'<a href="#level-{lv["n"].replace(".", "-")}"><b>{lv["n"]}</b> {e(lv["name"])}</a>' for lv in levels)
PDF = '/downloads/ai-0-to-1-study-guide.pdf'
NOTE = "We only email when we've got something worth writing. Written by us, not AI."
page = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AI from 0 to 1: a free study guide | Out of Our Depth</title>
  <meta name="description" content="The 35 AI words and ideas you need, in six short levels from 0 to 1, explained in plain English by Mary and Josh. Read it here or download the free PDF.">
  <meta name="theme-color" content="#FBF1E5">
  <link rel="canonical" href="https://outofourdepth.com/guide">
  <meta property="og:type" content="article">
  <meta property="og:url" content="https://outofourdepth.com/guide">
  <meta property="og:title" content="AI from 0 to 1: a free study guide">
  <meta property="og:description" content="The 35 AI words you need, in six short levels, explained the way we explain them to each other.">
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
  <a class="skip-link" href="#level-0-0">Skip to level 0.0</a>
  <header class="h-nav">
    <div class="h-wrap h-nav__inner">
      <a class="h-wm" href="/" aria-label="Out of Our Depth home"><span class="h-wm__k">Out of our</span><span>Depth</span></a>
      <nav class="h-links" aria-label="Main"><a href="/#episodes">Episodes</a><a href="/guide" aria-current="page">Study guide</a></nav>
      <a class="h-btn h-btn--sm" href="https://www.youtube.com/@OutOfOurDepthPod" data-link="youtube" target="_blank" rel="noopener">Watch the show</a>
    </div>
  </header>
  <main>
    <section class="g-hero">
      <div class="h-wrap g-hero__inner">
        <div class="g-hero__copy">
          <p class="h-mono">Free study guide  /  {e(guide["edition"])}</p>
          <h1><span class="g-hero__kick">AI from</span><span class="g-hero__big h-blue">0 to 1</span></h1>
          <p class="g-hero__sub">The 35 words and ideas you need to actually get AI, explained the way we explain them to each other. Six short levels. Read it here, or take the PDF with you.</p>
          <div class="g-hero__ctas"><a class="h-btn" href="{PDF}" download>Download the PDF</a><a class="g-link" href="#level-0-0">Start reading <span aria-hidden="true">&darr;</span></a></div>
          <p class="g-small">Free, no email needed. 10 pages.</p>
        </div>
        <a class="g-hero__cover" href="{PDF}" download><img src="/images/guide-cover.webp" width="612" height="792" alt="Cover of the AI from 0 to 1 study guide"></a>
      </div>
    </section>
    <section class="g-how h-rule">
      <div class="h-wrap">
        <div class="h-three">
          <div><p class="h-mono">Read</p><h2>One line each</h2><p>Every word gets one plain-English line and something to think of it like.</p></div>
          <div><p class="h-mono">Try</p><h2>Ten minutes</h2><p>Each level ends with a few hands-on things to try. Any AI app works.</p></div>
          <div><p class="h-mono">Say it</p><h2>Out loud</h2><p>Answer the check-yourself questions out loud. If you can explain it, you've got it.</p></div>
        </div>
        <nav class="g-jump" aria-label="Levels">{jump}</nav>
      </div>
    </section>
    {''.join(wlevel(lv, i) for i, lv in enumerate(levels))}
    <section class="g-finish" id="notes">
      <div class="h-wrap g-finish__inner">
        <p class="h-mono">Level 1.0, done</p>
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
        <p class="g-small">Spot something out of date? Tell us at <a href="mailto:hi@outofourdepth.com">hi@outofourdepth.com</a>. AI changes fast. Model names here are current as of {e(guide["edition"].replace(" edition", ""))}.</p>
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
      <p class="h-foot__sign">Built with AI, argued over by humans.</p>
    </div>
  </footer>
  <script src="/config.js"></script>
  <script src="/main.js"></script>
</body>
</html>
"""
(WEB / 'guide.html').write_text(page)

print(f'Built website/guide.html and {out.relative_to(ROOT)} ({out.stat().st_size // 1024} KB), {len(used)} words in {len(levels)} levels')
