#!/usr/bin/env node
// Builds the Learning page from website/learning-topics.json, so the word list lives in one place.
// Rewrites, in website/learning.html:
//   - the rows between <!-- learn-rows:start --> and <!-- learn-rows:end --> (word, explainer, drawing,
//     upvote), drawn here so the page works without JavaScript
//   - the inline copy of the words inside <script id="learning-data"> that learning.js uses for search
// The drawings come from scripts/learning-art.js (one pool scene per word id).
// Run after editing the JSON: node scripts/build-learning.js
// Keep word ids stable once people have voted; votes are stored by id. The order in the JSON is the
// "Shallow to deep" order on the page, simplest first.

const fs = require('fs');
const path = require('path');
const ART = require('./learning-art.js');

const ROOT = path.join(__dirname, '..', 'website');
const topics = JSON.parse(fs.readFileSync(path.join(ROOT, 'learning-topics.json'), 'utf8'));
const htmlPath = path.join(ROOT, 'learning.html');
let html = fs.readFileSync(htmlPath, 'utf8');

// Public episodes the page can link to (YouTube ids). Add an episode only after it is public.
const YT = { '000': 'y0NH_zvAdEo', '001': 'd-ykZl4WHjo', '002': 'cp4P_2t5rRQ', '003': 'rxethT04zMY', '004': 'Fby7CJC9i-Q', '005': '_d-hzc6Lt5c', '006': 'NiEnSBPe158' };

const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const ARROW = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 19V5M5 12l7-7 7 7"/></svg>';
const PLAY = '<svg viewBox="0 0 10 10" aria-hidden="true"><path d="M2 1 L9 5 L2 9 Z" fill="currentColor"/></svg>';

const ids = new Set();
for (const t of topics) {
  for (const k of ['id', 'title', 'definition', 'think']) if (!t[k]) throw new Error(`word ${t.id || '?'} is missing ${k}`);
  if (!/^[a-z0-9-]+$/.test(t.id) || ids.has(t.id)) throw new Error(`bad or duplicate id ${t.id}`);
  ids.add(t.id);
  const text = [t.title, t.aka, t.definition, t.think].join(' ');
  if (/[\u2014\u2013\u00b7\u2026\u2018\u2019\u201c\u201d]/.test(text)) throw new Error(`word ${t.id} has an em dash, en dash, dot, ellipsis or curly quote`);
  if (t.episode) {
    if (!YT[t.episode.number]) throw new Error(`word ${t.id} links to episode ${t.episode.number}, which isn't in the public list`);
    if (!/^\d\d:\d\d$/.test(t.episode.time)) throw new Error(`word ${t.id} has a bad time ${t.episode.time}`);
  }
  if (!ART(t.id).startsWith('<svg')) throw new Error(`word ${t.id} has no drawing in scripts/learning-art.js`);
}

function tag(t) {
  if (!t.episode) return '<span class="learn-tag learn-tag--off">Not on the show yet</span>';
  const [m, s] = t.episode.time.split(':').map(Number), secs = m * 60 + s;
  const label = secs ? `Ep ${t.episode.number} at ${t.episode.time}` : `All of ep ${t.episode.number}`;
  return `<a class="learn-tag learn-tag--on" href="https://www.youtube.com/watch?v=${YT[t.episode.number]}${secs ? `&amp;t=${secs}` : ''}" target="_blank" rel="noopener">${PLAY}${label}</a>`;
}

const rows = topics.map((t) => [
  `<li class="learn-row" id="w-${t.id}" data-topic="${t.id}">`,
  `<div class="learn-row__term"><span class="learn-row__rank" aria-hidden="true"></span><h3>${esc(t.title)}</h3>${t.aka ? `<p class="learn-row__aka">${esc(t.aka)}</p>` : ''}${tag(t)}</div>`,
  `<div class="learn-row__body"><p class="learn-row__def">${esc(t.definition)}</p><p class="learn-row__think"><b>Think</b>${esc(t.think)}</p></div>`,
  `<div class="learn-art" aria-hidden="true">${ART(t.id)}</div>`,
  `<button class="learn-upv" type="button" data-vote="${t.id}" aria-pressed="false" aria-label="Upvote ${esc(t.title)}" disabled>${ARROW}<span class="n" data-count></span><span class="w">Upvote</span></button>`,
  '</li>',
].join('')).join('\n');

const START = '<!-- learn-rows:start -->', END = '<!-- learn-rows:end -->';
const a = html.indexOf(START), b = html.indexOf(END);
if (a < 0 || b < a) throw new Error('learning.html is missing the learn-rows markers');
html = html.slice(0, a + START.length) + '\n' + rows + '\n' + html.slice(b);

const data = JSON.stringify(topics.map(({ id, title, aka, definition, think }) => ({ id, title, aka, definition, think }))).replace(/</g, '\\u003c');
const dataRe = /<script id="learning-data" type="application\/json">[\s\S]*?<\/script>/;
if (!dataRe.test(html)) throw new Error('learning.html is missing <script id="learning-data">');
html = html.replace(dataRe, () => `<script id="learning-data" type="application/json">${data}</script>`);

fs.writeFileSync(htmlPath, html);
console.log(`Built ${topics.length} words (${topics.filter((t) => t.episode).length} on the show) into website/learning.html`);
