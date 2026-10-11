#!/usr/bin/env node
// Prints the newsletter list as CSV (email, subscribedAt, source), oldest first.
//
// Needs the store's credentials, which live on the Vercel project. From the repo root:
//   vercel env pull .env.newsletter --cwd website   (once; .env.* is gitignored)
//   node scripts/export-subscribers.js > subscribers.csv
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

const url = process.env.KV_REST_API_URL;
const token = process.env.KV_REST_API_READ_ONLY_TOKEN || process.env.KV_REST_API_TOKEN;
if (!url || !token) {
  console.error('No store credentials. Run: vercel env pull .env.newsletter --cwd website');
  process.exit(1);
}

(async () => {
  const r = await fetch(`${url}/hgetall/newsletter:subscribers`, { headers: { Authorization: `Bearer ${token}` } });
  if (!r.ok) throw new Error(`store answered ${r.status}`);
  const flat = (await r.json()).result || [];
  const rows = [];
  for (let i = 1; i < flat.length; i += 2) rows.push(JSON.parse(flat[i]));
  rows.sort((a, b) => a.subscribedAt.localeCompare(b.subscribedAt));
  const csv = (v) => `"${String(v ?? '').replace(/"/g, '""')}"`;
  console.log('email,subscribedAt,source');
  for (const row of rows) console.log([row.email, row.subscribedAt, row.source].map(csv).join(','));
  console.error(`${rows.length} subscribers`);
})().catch((err) => {
  console.error(err.message);
  process.exit(1);
});
