#!/usr/bin/env python3
"""Build the free "AI from 0 to 1" study guide: the /guide web page and the PDF.

Words come from website/learning-topics.json (the 35 from the old Learning list, wording unchanged) plus
the guide-only words in 03_ASSETS/study-guide/guide-levels.json, which also holds the levels, quizzes,
debates, and resources. The PDF prints the same page with guide-print.css.

    python3 scripts/build-study-guide.py

Writes website/guide.html, website/downloads/ai-0-to-1-study-guide.pdf, website/images/guide-cover.webp
and the print HTML at 03_ASSETS/study-guide/study-guide.html. Needs Python 3, Pillow and Playwright with
Chromium or Chrome (set CHROME=/path/to/chrome to pick one). Uses local brand fonts if available.

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
    source = ''
    if t.get('source'):
        label, url = t['source']
        source = f'<a class="lbl" href="{html.escape(url, quote=True)}" target="_blank" rel="noopener">{e(label)}</a>'
    return (f'<article class="word" id="{t["id"]}">'
            f'<h3>{e(t["title"])}</h3>{aka}<p>{e(t["definition"])}</p>'
            f'<p class="think"><b>Think of it like</b> {e(phrase(t["think"]))}</p>{tag(t)}{source}</article>')

def air_quiz(lv):
    quiz_id = f'{slug(lv["n"])}-quiz'
    cards = ''.join(
        f'<button class="mo" type="button" aria-label="Tap to see the word"><span class="mo__in">'
        f'<span class="mo__f"><span class="mo__n g-print-only">{i}.</span>'
        f'<span class="mo__q">{e(q)}</span><span class="mo__hint">Tap to check</span></span>'
        f'<span class="mo__b"><span class="mo__hint">That\'s</span><span class="mo__a">{e(topics[w]["title"])}</span></span></span></button>'
        for i, (q, w) in enumerate(lv['moments'], 1))
    return (f'<div class="air" id="{quiz_id}"><p class="kick">Come up for air  /  name that moment</p>'
            f'<div class="mos">{cards}</div>'
            f'<a class="air__answers g-print-only" href="#{quiz_id}-answers">Check answers</a>'
            f'<p class="dare"><b>Dare</b> {e(lv["dare"])}</p></div>')

def answer_group(lv):
    quiz_id = f'{slug(lv["n"])}-quiz'
    answers = ''.join(f'<li>{e(topics[word]["title"])}</li>' for _, word in lv['moments'])
    return (f'<div class="answer-key__group" id="{quiz_id}-answers">'
            f'<p class="kick">Level {e(lv["n"])}</p><h3>{e(lv["name"])}</h3>'
            f'<ol>{answers}</ol><a href="#{quiz_id}">Back to quiz</a></div>')

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

def level_section(lv, i):
    words = ''.join(word_card(topics[w]) for w in lv['words'])
    return f'''<section class="lv lv--{i}{' dk' if i >= 5 else ''}" data-depth id="{slug(lv["n"])}" aria-labelledby="{slug(lv["n"])}-t"><div class="h-wrap">
  <header class="lv-head{' lv-head--word' if not lv["depth"][0].isdigit() else ''}"><span class="ft" aria-hidden="true">{e(lv["depth"])}</span><div><p class="kick">Level {lv["n"]}  /  {len(lv["words"])} words</p><h2 id="{slug(lv["n"])}-t">{headline(lv["name"], lv.get("accent"))}</h2><p class="promise">{e(lv["promise"])}</p></div></header>
  <div class="cards">{words}</div>
{f'  {MAP}' if lv["n"] == "0.6" else ""}
  {air_quiz(lv)}
</div></section>'''

def debate_card(debate, i):
    key = e(debate['id'])
    choices = ''.join(
        f'<button type="button" class="side" aria-pressed="false" aria-controls="followup-{key}" '
        f'data-option="{side}" data-followup="{e(option["followup"])}">{e(option["label"])}</button>'
        for side, option in enumerate(debate['options']))
    return (f'<article class="debate" data-debate="{key}"><span class="debate__n">{i + 1:02d}</span>'
            f'<h3 id="debate-{key}">{e(debate["question"])}</h3><div class="sides" role="group" aria-labelledby="debate-{key}">{choices}</div>'
            f'<div class="debate__followup" id="followup-{key}" aria-live="polite"></div></article>')

debates_web = '\n      '.join(debate_card(d, i) for i, d in enumerate(guide['debates']))
stuck = ''.join(f'<p><b>{e(phrase(a))}</b> {e(b)}</p>' for a, b in guide['stuck'])
nxt = ''.join(f'<a class="next" href="{html.escape(u)}" target="_blank" rel="noopener"><span class="lbl">{e(who)}</span><h3>{e(t)}</h3><p>{e(len_)}</p></a>' for t, who, len_, u in guide['next'])
US = ('<a class="next next--us" href="https://www.youtube.com/@OutOfOurDepthPod?sub_confirmation=1" target="_blank" rel="noopener">'
      '<span class="lbl">Us, obviously</span><h3>Out of Our Depth</h3><p>New episodes every week. Would it kill ya to subscribe?</p></a>')
OURS = ''.join(f'<li>{e(x)}</li>' for x in guide['ourselves'])
HELP = 'Stuck on one? Email <a href="mailto:hi@outofourdepth.com">hi@outofourdepth.com</a>, tell us which one, and we\'ll help'
NOTE = "Written by us, when we have something worth sharing"
SIGN = "Can't lie, Claude built this"
PITCH = f'{N} words and 10 debates'

# ---------- Web page: The Dive. One scroll that gets deeper, cream at 0 ft to navy at the deep end ----------
gauge = ''.join(f'<a href="#{slug(lv["n"])}"><i></i><span>{e(lv["depth"])}</span></a>' for lv in levels) + '<a href="#debates"><i></i><span>The bottom</span></a>'
PDF_URL = '/downloads/ai-0-to-1-study-guide.pdf'
SITE = 'https://outofourdepth.com'
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
  <link rel="stylesheet" href="/guide-print.css" media="print">
  <script>window.va = window.va || function () {{ (window.vaq = window.vaq || []).push(arguments); }};</script>
  <script defer src="/_vercel/insights/script.js"></script>
</head>
<body class="home guide">
  <!-- Built by scripts/build-study-guide.py from website/learning-topics.json and 03_ASSETS/study-guide/guide-levels.json. Edit those, not this file. -->
  <a class="skip-link" href="#level-0-0">Skip to the first level</a>
  <header class="h-nav">
    <div class="h-wrap h-nav__inner">
      <a class="h-wm" href="/" aria-label="Out of Our Depth home"><span class="h-wm__k">Out of our</span><span>Depth</span></a>
      <nav class="h-links" aria-label="Main"><a href="/#episodes">Episodes</a><a href="/guide" aria-current="page">Study guide</a><a href="/builds">Builds</a><a href="/#about">About</a></nav>
      <a class="h-btn h-btn--sm" href="https://www.youtube.com/@OutOfOurDepthPod" data-link="youtube" target="_blank" rel="noopener">Watch the show</a>
    </div>
  </header>
  <nav class="gauge" aria-label="How deep you are">{gauge}</nav>
  <main>
    <div class="g-opening">
      <section class="g-hero">
        <div class="h-wrap g-hero__inner">
          <p class="kick">Free study guide</p>
          <h1><span class="g-hero__kick">AI from</span> <span class="g-hero__big">0 to 1</span></h1>
          <p class="g-hero__sub">{PITCH}. <span class="g-screen-only">Keep scrolling</span><span class="g-print-only">Keep going</span>, it gets deeper</p>
          <div class="g-hero__ctas"><a class="h-btn" href="#level-0-0">Dive in</a><a class="h-btn h-btn--ghost g-screen-only" href="{PDF_URL}" download>Download the PDF</a><a class="h-btn h-btn--ghost g-print-only" href="{SITE}/guide">Read online</a></div>
          <img class="g-hero__hosts" src="/images/hosts-sticker-640.webp" width="640" height="421" alt="Mary and Josh">
          <a class="h-wm g-print-only" href="/" aria-label="Out of Our Depth home"><span class="h-wm__k">Out of our</span><span>Depth</span></a>
        </div>
      </section>
    </div>
    {''.join(level_section(lv, i) for i, lv in enumerate(levels))}
    <section class="lv lv--6 dk" data-depth id="debates"><div class="h-wrap">
      <header class="lv-head lv-head--word"><span class="ft" aria-hidden="true">The bottom</span><div><p class="kick">No right answers down here</p><h2>10 <span class="blue">debates</span></h2><p class="promise">We don't agree on half of these. Pick a side for a follow-up question</p><p class="g-small"><a class="g-print-only" href="{SITE}/guide#debates">Vote in the online guide</a><span class="g-print-only">. </span>We're tallying anonymous picks so we can share the split once enough people weigh in</p></div></header>
      <div class="debates">{debates_web}</div>
      <div class="g-ours"><p class="kick">The parts that need us</p><h3>What we still do <span class="blue">ourselves</span></h3><ul>{OURS}</ul></div>
    </div></section>
    <section class="g-end dk"><div class="h-wrap">
      <div class="g-end__cols">
        <div class="g-stuck" id="stuck"><p class="kick">Happens to the best of us</p><h3>If you get <span class="blue">stuck</span></h3>{stuck}<p class="g-help">{HELP}</p></div>
        <div class="g-next"><p class="kick">Want more?</p><h3>Where to go <span class="blue">next</span></h3><div class="next-row">{US}{nxt}</div></div>
      </div>
    </div></section>
    <section class="g-finish dk" id="notes">
      <div class="h-wrap g-finish__inner">
        <p class="kick">You hit the bottom</p>
        <h2>You're at <span class="blue">1</span></h2>
        <p class="g-finish__sub">Want what comes after 1? Get the notes: what we tried, what worked and what flopped.</p>
        <form class="h-form" action="/api/subscribe" method="post" data-notes novalidate>
          <div class="h-form__row g-screen-only">
            <label class="visually-hidden" for="notes-email">Email address</label>
            <input class="h-input" id="notes-email" name="email" type="email" inputmode="email" autocomplete="email" placeholder="Your email" required>
            <button class="h-btn" type="submit">Send me the notes</button>
          </div>
          <a class="h-btn g-print-only" href="{SITE}/guide#notes">Send me the notes</a>
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
        <nav class="h-foot__links" aria-label="Footer"><a href="/#episodes">Episodes</a><a href="/guide">Study guide</a><a href="/builds">Builds</a><a href="/#about">About</a><a href="mailto:hi@outofourdepth.com">hi@outofourdepth.com</a></nav>
        <nav class="h-foot__social topbar__social" aria-label="Find us" data-socials></nav>
      </div>
      <p class="h-foot__sign">{e(SIGN)}</p>
    </div>
  </footer>
  <section class="g-answer-key g-print-only" aria-labelledby="answer-key-title">
    <div class="h-wrap">
      <header class="sec-head"><p class="kick">Come up for air</p><h2 id="answer-key-title">Answer <span class="blue">key</span></h2></header>
      <div class="answer-key__groups">{''.join(answer_group(lv) for lv in levels)}</div>
    </div>
  </section>
  <script src="/config.js"></script>
  <script src="/main.js"></script>
  <script src="/debates.js"></script>
  <script>
    document.querySelectorAll('.mo').forEach(function (b) {{ b.addEventListener('click', function () {{ b.classList.toggle('on'); }}); }});
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

# The checked-in print preview opens locally with the site's styles and images.
# Links to other pages should still point to production in the downloaded PDF.
def local_print_url(attribute, path):
    if (WEB / path).is_file() and path != PDF_URL.lstrip('/'):
        return f'{attribute}="../../website/{path}"'
    return f'{attribute}="{SITE}/{path}"'


print_page = re.sub(r'^ *<script\b[^>]*>.*?</script>[ \t]*\n?', '', page, flags=re.M | re.S)
print_page = re.sub(r'(href|src)="/([^"]*)"', lambda m: local_print_url(*m.groups()), print_page)
(SRC / 'study-guide.html').write_text(print_page)

# ---------- Render the PDF and the matching homepage thumbnail ----------
from base64 import b64encode
from io import BytesIO
from PIL import Image
from playwright.sync_api import sync_playwright

out = WEB / PDF_URL.lstrip('/')
out.parent.mkdir(exist_ok=True)
brand_fonts = {
    'Teachers': ROOT / '03_ASSETS/brand-fonts/teachers.ttf',
    'JetBrains Mono': ROOT / '03_ASSETS/brand-fonts/jetbrains-mono.ttf',
}
with sync_playwright() as p:
    kw = {'executable_path': os.environ['CHROME']} if os.environ.get('CHROME') else {}
    with p.chromium.launch(**kw) as browser:
        pg = browser.new_page(viewport={'width': 816, 'height': 1056}, reduced_motion='reduce')
        pg.emulate_media(media='print')
        if all(path.is_file() for path in brand_fonts.values()):
            font_css = ''.join(
                f'@font-face{{font-family:"{family}";font-weight:400 800;'
                f'src:url(data:font/ttf;base64,{b64encode(path.read_bytes()).decode("ascii")}) format("truetype")}}'
                for family, path in brand_fonts.items()
            )
            pg.route('https://fonts.googleapis.com/**',
                     lambda route: route.fulfill(content_type='text/css', body=font_css))
        pg.goto((SRC / 'study-guide.html').as_uri(), wait_until='load')
        if not pg.evaluate("async () => { await document.fonts.ready; return document.fonts.check('800 36px Teachers') && [...document.fonts].some(f => f.family === 'Teachers' && f.status === 'loaded'); }"):
            sys.exit('Teachers did not load; check the Google Fonts connection before building the PDF')
        cover = pg.locator('.g-opening').screenshot()
        pg.pdf(path=str(out), print_background=True, prefer_css_page_size=True,
               tagged=True, outline=True)

Image.open(BytesIO(cover)).convert('RGB').resize((612, 792), Image.Resampling.LANCZOS).save(
    WEB / 'images' / 'guide-cover.webp', quality=88, method=6)
print(f'Built website/guide.html and {out.relative_to(ROOT)}: {N} words, {len(levels)} levels, {len(guide["debates"])} debates')
