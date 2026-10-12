#!/usr/bin/env node
// Builds the Learning tab's cards from website/learning-topics.json, so the topic list lives in one
// place. Rewrites, in website/learning.html:
//   - the no-JS cards between <!-- learn-cards:start --> and <!-- learn-cards:end -->
//   - the inline copy of the topics inside <script id="learning-data">
// Run after editing the JSON: node scripts/build-learning.js
// Keep topic IDs stable once people have voted; votes are stored by ID.

const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..', 'website');
const topics = JSON.parse(fs.readFileSync(path.join(ROOT, 'learning-topics.json'), 'utf8'));
const htmlPath = path.join(ROOT, 'learning.html');
let html = fs.readFileSync(htmlPath, 'utf8');

// Pool depths: words are the shallow end, the big questions are the deep end
const DEPTH = {
  term: { ft: '3 FT', name: 'Word to know' },
  tool: { ft: '6 FT', name: 'Tool to try' },
  topic: { ft: '9 FT', name: 'Big question' },
};

const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

const ids = new Set();
for (const t of topics) {
  for (const k of ['id', 'kind', 'title', 'description', 'exercise', 'url', 'source']) {
    if (!t[k]) throw new Error(`topic ${t.id || '?'} is missing ${k}`);
  }
  if (!DEPTH[t.kind]) throw new Error(`topic ${t.id} has unknown kind ${t.kind}`);
  if (!/^[a-z0-9-]+$/.test(t.id) || ids.has(t.id)) throw new Error(`bad or duplicate id ${t.id}`);
  ids.add(t.id);
  const text = [t.title, t.aka, t.description, t.exercise, t.source].join(' ');
  if (/[—–·…]/.test(text)) throw new Error(`topic ${t.id} has an em dash, dot or ellipsis`);
}

const cards = topics.map((t) => {
  const d = DEPTH[t.kind];
  return [
    `<article class="learn-card learn-card--${t.kind}" id="${esc(t.id)}" data-topic="${esc(t.id)}">`,
    `<div class="learn-card__top"><span class="depth">${d.ft}</span><span class="learn-card__kind">${d.name}</span></div>`,
    `<h3>${esc(t.title)}</h3>`,
    t.aka ? `<p class="learn-card__aka">${esc(t.aka)}</p>` : '',
    `<p class="learn-card__desc">${esc(t.description)}</p>`,
    `<p class="learn-card__try"><span>Try this</span>${esc(t.exercise)}</p>`,
    `<div class="learn-card__foot"><a href="${esc(t.url)}" target="_blank" rel="noopener">${esc(t.source)} <span aria-hidden="true">&#8599;</span></a>`,
    `<button class="learn-vote" type="button" data-vote="${esc(t.id)}" aria-pressed="false" disabled><span aria-hidden="true">&#8593;</span><span data-count></span><span class="learn-vote__label">Cover this</span></button></div>`,
    `</article>`,
  ].filter(Boolean).join('');
}).join('\n');

function between(src, start, end, body, label) {
  const a = src.indexOf(start), b = src.indexOf(end);
  if (a < 0 || b < a) throw new Error(`markers for ${label} not found in learning.html`);
  return src.slice(0, a + start.length) + '\n' + body + '\n' + src.slice(b);
}

html = between(html, '<!-- learn-cards:start -->', '<!-- learn-cards:end -->', cards, 'cards');
const data = JSON.stringify(topics).replace(/</g, '\\u003c');
html = html.replace(/(<script id="learning-data" type="application\/json">)[\s\S]*?(<\/script>)/, (_, a, b) => a + data + b);
fs.writeFileSync(htmlPath, html);
const by = Object.fromEntries(Object.keys(DEPTH).map((k) => [k, topics.filter((t) => t.kind === k).length]));
console.log(`build-learning: ${topics.length} cards (${by.term} words, ${by.tool} tools, ${by.topic} big questions)`);
