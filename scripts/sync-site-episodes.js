#!/usr/bin/env node
// Keeps the website's saved episode list in step with YouTube, so nobody edits it by hand.
//
// Reads the saved list in website/config.js and the channel's long-form uploads feed, then:
//   - adds new long-form uploads
//   - updates titles that were renamed on YouTube
//   - drops a saved video only when YouTube says it no longer exists (oEmbed 404),
//     and refuses to drop more than one per run
//   - numbers episodes in public order from 000 (videos in `hiddenVideos` don't count)
//   - shows `siteTitles` in place of YouTube's title on the no-JS cards (config.js keeps YouTube's)
//   - rewrites the list between the episodes:start / episodes:end markers in website/config.js
//     and the no-JS cards between the same markers in website/index.html
//
// Run by .github/workflows/sync-site-episodes.yml. Locally: node scripts/sync-site-episodes.js
// Add --dry-run to print the result without writing. Exits 0 with no changes when YouTube can't be
// reached, and 1 when a safety check fails, so the GitHub run shows as failed and emails the owner.

const fs = require('fs');
const path = require('path');
const vm = require('vm');
const { parseFeed } = require('../website/api/latest.js');

const ROOT = path.join(__dirname, '..');
const CONFIG = path.join(ROOT, 'website', 'config.js');
const HTML = path.join(ROOT, 'website', 'index.html');
const CHANNEL_ID = 'UCr2sdn2AwHyhjm5SUtWUNGQ';
const FEEDS = [
  `https://www.youtube.com/feeds/videos.xml?playlist_id=UULF${CHANNEL_ID.slice(2)}`,
  `https://www.youtube.com/feeds/videos.xml?channel_id=${CHANNEL_ID}`,
];
const UA = 'Mozilla/5.0 (compatible; oood-site-sync/1.0; +https://outofourdepth.com)';
const DRY_RUN = process.argv.includes('--dry-run');
const FIELD_ORDER = ['id', 'number', 'title', 'blurb', 'published', 'url', 'thumbnail'];

function fail(message) {
  console.error(`sync-site-episodes: ${message}`);
  process.exit(1);
}

function readConfig(source) {
  const sandbox = { window: {} };
  vm.runInNewContext(source, sandbox, { filename: 'config.js' });
  return sandbox.window.OOOD || {};
}

async function fetchLive() {
  for (const url of FEEDS) {
    try {
      const r = await fetch(url, { headers: { 'User-Agent': UA } });
      if (!r.ok) continue;
      const xml = await r.text();
      if (!xml.includes('<feed')) continue;
      const videos = parseFeed(xml);
      if (videos.length) return videos;
    } catch (err) {
      // try the next feed
    }
  }
  return null;
}

// 'gone' only for a definite 404. Anything else (private, embedding off, network trouble) keeps it.
async function videoStatus(id) {
  try {
    const url = `https://www.youtube.com/oembed?format=json&url=${encodeURIComponent(`https://www.youtube.com/watch?v=${id}`)}`;
    const r = await fetch(url, { headers: { 'User-Agent': UA } });
    return r.status === 404 ? 'gone' : 'keep';
  } catch (err) {
    return 'keep';
  }
}

async function bestThumbnail(id) {
  const maxres = `https://i.ytimg.com/vi/${id}/maxresdefault.jpg`;
  try {
    const r = await fetch(maxres, { method: 'HEAD' });
    if (r.ok) return maxres;
  } catch (err) {
    // fall through
  }
  return `https://i.ytimg.com/vi/${id}/hqdefault.jpg`;
}

function lit(value) {
  const s = String(value);
  return /['\\\n]/.test(s) ? JSON.stringify(s) : `'${s}'`;
}

function configBlock(episodes) {
  const entries = episodes.map((ep) => {
    const keys = FIELD_ORDER.filter((k) => ep[k] != null).concat(
      Object.keys(ep).filter((k) => !FIELD_ORDER.includes(k) && ep[k] != null)
    );
    const lines = [];
    // Keep the first line compact, as the hand-written entries were.
    lines.push(`      id: ${lit(ep.id)}, number: ${lit(ep.number)}, title: ${lit(ep.title)},`);
    for (const k of keys) {
      if (k === 'id' || k === 'number' || k === 'title') continue;
      lines.push(`      ${k}: ${lit(ep[k])},`);
    }
    lines[lines.length - 1] = lines[lines.length - 1].replace(/,$/, '');
    return `    {\n${lines.join('\n')}\n    }`;
  });
  return entries.join(',\n');
}

function esc(s) {
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function htmlBlock(episodes, siteTitles = {}) {
  const wave = '<span class="wave" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i></span>';
  return episodes
    .map((ep, i) => {
      const latest = i === 0;
      const meta = latest ? `${wave}New episode ${ep.number}` : `Episode ${ep.number}`;
      return [
        `        <a class="ep${latest ? ' ep--latest' : ''}" href="${esc(ep.url)}" target="_blank" rel="noopener">`,
        `          <span class="ep__thumb"><img src="${esc(ep.thumbnail)}" alt="" width="1280" height="720"${latest ? '' : ' loading="lazy"'}></span>`,
        `          <span class="ep__meta label">${meta}</span>`,
        `          <h3 class="ep__title">${esc(siteTitles[ep.id] || ep.title)}</h3>`,
        `        </a>`,
      ].join('\n');
    })
    .join('\n');
}

function replaceBetween(source, startMarker, endMarker, body, label) {
  const start = source.indexOf(startMarker);
  const end = source.indexOf(endMarker);
  if (start < 0 || end < 0 || end < start || source.indexOf(startMarker, start + 1) >= 0) {
    fail(`${label}: the episodes:start / episodes:end markers are missing or duplicated`);
  }
  const lineEnd = source.indexOf('\n', start) + 1;
  const endLineStart = source.lastIndexOf('\n', end) + 1;
  return source.slice(0, lineEnd) + body + '\n' + source.slice(endLineStart);
}

async function main() {
  const configSource = fs.readFileSync(CONFIG, 'utf8');
  const htmlSource = fs.readFileSync(HTML, 'utf8');
  const cfg = readConfig(configSource);
  const hidden = new Set(cfg.hiddenVideos || []);
  const saved = (cfg.episodes || []).filter((ep) => ep && ep.id && !hidden.has(ep.id));

  const live = await fetchLive();
  if (!live) {
    console.log('sync-site-episodes: YouTube feeds unreachable, leaving the site as it is');
    return;
  }

  const byId = new Map(saved.map((ep) => [ep.id, { ...ep }]));
  const liveIds = new Set();
  const changes = [];
  for (const v of live) {
    if (hidden.has(v.id)) continue;
    liveIds.add(v.id);
    const known = byId.get(v.id);
    if (!known) {
      byId.set(v.id, { id: v.id, title: v.title, published: v.published, url: v.url });
      changes.push(`added ${v.id} "${v.title}"`);
    } else {
      if (known.title !== v.title) changes.push(`renamed ${v.id}: "${known.title}" -> "${v.title}"`);
      known.title = v.title;
      if (!known.published) known.published = v.published;
    }
  }

  // Saved videos missing from the feed are usually just older than its newest 15. Ask YouTube directly.
  const gone = [];
  for (const ep of saved) {
    if (!liveIds.has(ep.id) && (await videoStatus(ep.id)) === 'gone') gone.push(ep);
  }
  if (gone.length > 1) {
    fail(`YouTube reports ${gone.length} saved videos as gone (${gone.map((e) => e.id).join(', ')}). ` +
      'Refusing to drop more than one at once; check the channel, then remove them from config.js by hand.');
  }
  for (const ep of gone) {
    byId.delete(ep.id);
    changes.push(`dropped ${ep.id} "${ep.title}" (YouTube says it no longer exists)`);
  }

  const episodes = [...byId.values()];
  for (const ep of episodes) {
    if (!ep.url) ep.url = `https://www.youtube.com/watch?v=${ep.id}`;
    if (!ep.thumbnail || !ep.thumbnail.includes('maxresdefault')) ep.thumbnail = await bestThumbnail(ep.id);
    if (!ep.published || isNaN(Date.parse(ep.published))) fail(`no publish date for ${ep.id}`);
  }
  episodes.sort((a, b) => Date.parse(a.published) - Date.parse(b.published));
  episodes.forEach((ep, n) => {
    const number = String(n).padStart(3, '0');
    if (ep.number && ep.number !== number) changes.push(`renumbered ${ep.id}: ${ep.number} -> ${number}`);
    ep.number = number;
  });
  episodes.reverse();
  if (!episodes.length) fail('the merged list is empty');

  const nextConfig = replaceBetween(configSource, '// episodes:start', '// episodes:end', configBlock(episodes), 'config.js');
  const nextHtml = replaceBetween(htmlSource, '<!-- episodes:start', '<!-- episodes:end', htmlBlock(episodes, cfg.siteTitles || {}), 'index.html');

  // The rewritten config must load and say exactly what we meant.
  const check = readConfig(nextConfig).episodes || [];
  const same = check.length === episodes.length &&
    check.every((ep, i) => ep.id === episodes[i].id && ep.title === episodes[i].title && ep.number === episodes[i].number);
  if (!same) fail('the rewritten config.js does not round-trip; not writing it');

  const configChanged = nextConfig !== configSource;
  const htmlChanged = nextHtml !== htmlSource;
  console.log(`sync-site-episodes: ${episodes.length} episodes, newest ${episodes[0].number} "${episodes[0].title}"`);
  for (const c of changes) console.log(`  ${c}`);
  if (!configChanged && !htmlChanged) {
    console.log('  no changes');
    return;
  }
  if (DRY_RUN) {
    console.log('  (dry run: nothing written)');
    return;
  }
  if (configChanged) fs.writeFileSync(CONFIG, nextConfig);
  if (htmlChanged) fs.writeFileSync(HTML, nextHtml);
}

main().catch((err) => fail(err.stack || String(err)));
