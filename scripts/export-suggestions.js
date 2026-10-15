#!/usr/bin/env node
// Prints "Suggest a word" entries from the Learning page, newest first, with how many times each word
// has been asked for in total.
//
// Needs the store's credentials, which live on the Vercel project. From the repo root:
//   vercel env pull .env.newsletter --cwd website   (once; .env.* is gitignored)
//   node scripts/export-suggestions.js                 everything
//   node scripts/export-suggestions.js --since 2026-10-15   only what came in on or after that date
//   node scripts/export-suggestions.js --json          machine-readable, for jtan's review
// Reads KV_REST_API_READ_ONLY_TOKEN when present, so the export can't change anything.

const fs = require('fs');
const path = require('path');

const envFile = path.join(__dirname, '..', 'website', '.env.newsletter');
if (fs.existsSync(envFile)) {
  for (const line of fs.readFileSync(envFile, 'utf8').split('\n')) {
    const m = line.match(/^([A-Z_]+)="?(.*?)"?$/);
    if (m && !process.env[m[1]]) process.env[m[1]] = m[2];
  }
}

const args = process.argv.slice(2);
const sinceArg = args.includes('--since') ? args[args.indexOf('--since') + 1] : null;
if (sinceArg && !/^\d{4}-\d{2}-\d{2}$/.test(sinceArg)) {
  console.error('--since takes a date like 2026-10-15');
  process.exit(1);
}
const asJson = args.includes('--json');

const url = process.env.KV_REST_API_URL;
const token = process.env.KV_REST_API_READ_ONLY_TOKEN || process.env.KV_REST_API_TOKEN;
if (!url || !token) {
  console.error('No store credentials. Run: vercel env pull .env.newsletter --cwd website');
  process.exit(1);
}

async function get(cmd) {
  const r = await fetch(`${url}/${cmd}`, { headers: { Authorization: `Bearer ${token}` } });
  if (!r.ok) throw new Error(`store answered ${r.status}`);
  return (await r.json()).result || [];
}

(async () => {
  const [list, flat] = await Promise.all([get('lrange/learning:suggestions/0/-1'), get('hgetall/learning:suggestion-counts')]);
  const totals = {};
  for (let i = 0; i < flat.length; i += 2) totals[flat[i]] = Number(flat[i + 1]);
  let rows = list.map((s) => { try { return JSON.parse(s); } catch { return null; } }).filter(Boolean).reverse();
  if (sinceArg) rows = rows.filter((r) => r.at.slice(0, 10) >= sinceArg);
  rows = rows.map((r) => ({ ...r, totalAsks: totals[r.word.toLowerCase()] || 1 }));
  if (asJson) console.log(JSON.stringify(rows, null, 2));
  else for (const r of rows) console.log(`${r.at.slice(0, 16).replace('T', ' ')}  ${r.word}${r.totalAsks > 1 ? `  (asked ${r.totalAsks}x)` : ''}`);
  console.error(`${rows.length} suggestion${rows.length === 1 ? '' : 's'}${sinceArg ? ` since ${sinceArg}` : ''}`);
})().catch((err) => {
  console.error(err.message);
  process.exit(1);
});
