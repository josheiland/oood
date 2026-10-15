// "Suggest a word" on the Learning page. Saves what people type to the site's Upstash Redis store
// (the same "oood-newsletter" resource the signup and votes use). Nothing is emailed.
//
// Every suggestion is appended to the list `learning:suggestions` as JSON: { word, at }. A hash,
// `learning:suggestion-counts`, counts repeats by lowercased word, so "RAG" asked for 9 times shows
// as 9. Read them with `node scripts/export-suggestions.js` (add --since 2026-10-15 for new ones only).
//
// Accepts JSON (the page's fetch) or a plain form post (no JS), which redirects back to
// /learning?suggested=1#suggest. A hidden `website` field catches bots: when it's filled in, the request
// looks successful and nothing is saved. Each network gets 10 suggestions an hour. Links are refused,
// because a real word never needs one and spam always has one.

const LIST = 'learning:suggestions';
const COUNTS = 'learning:suggestion-counts';
const KEEP = 5000;
const LIMIT_PER_HOUR = 10;

async function redis(commands) {
  const url = process.env.KV_REST_API_URL;
  const token = process.env.KV_REST_API_TOKEN;
  if (!url || !token) throw new Error('suggestion store is not configured');
  const r = await fetch(`${url}/pipeline`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(commands),
    signal: AbortSignal.timeout(8000),
  });
  if (!r.ok) throw new Error(`suggestion store answered ${r.status}`);
  const out = await r.json();
  const bad = out.find((x) => x.error);
  if (bad) throw new Error(bad.error);
  return out.map((x) => x.result);
}

async function readBody(req) {
  if (req.body && typeof req.body === 'object') return req.body;
  const raw = typeof req.body === 'string' ? req.body : '';
  if (raw.length > 2048) return {};
  const type = req.headers['content-type'] || '';
  if (type.includes('application/json')) {
    try { return JSON.parse(raw || '{}'); } catch { return {}; }
  }
  return Object.fromEntries(new URLSearchParams(raw));
}

module.exports = async (req, res) => {
  res.setHeader('Cache-Control', 'no-store');
  const wantsJson = (req.headers.accept || '').includes('application/json');
  const reply = (status, body) => {
    if (wantsJson) return res.status(status).json(body);
    if (status === 200) return res.redirect(303, '/learning?suggested=1#suggest');
    return res.status(status).send(body.error || 'Something went wrong.');
  };

  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return reply(405, { error: 'Use the box on the Learning page.' });
  }

  const body = await readBody(req);
  if (body.website) return reply(200, { ok: true }); // honeypot

  const word = String(body.word || '').replace(/\s+/g, ' ').trim();
  if (word.length < 2) return reply(400, { error: 'Type a word or a question first.' });
  if (word.length > 120) return reply(400, { error: 'Shorter, please. A word or a quick question works best.' });
  if (/https?:|www\.|\.(com|net|org|io|ru|xyz)\b/i.test(word)) return reply(400, { error: 'No links, just the word.' });

  try {
    const ip = String(req.headers['x-forwarded-for'] || '').split(',')[0].trim() || 'unknown';
    const hourKey = `learning:suggest-rate:${ip}:${Math.floor(Date.now() / 3600000)}`;
    const [count] = await redis([['INCR', hourKey], ['EXPIRE', hourKey, 3600]]);
    if (count > LIMIT_PER_HOUR) return reply(429, { error: 'That\'s a lot of words! Give it an hour?' });
    const record = JSON.stringify({ word, at: new Date().toISOString() });
    await redis([['RPUSH', LIST, record], ['LTRIM', LIST, -KEEP, -1], ['HINCRBY', COUNTS, word.toLowerCase(), 1]]);
    return reply(200, { ok: true });
  } catch (err) {
    console.error('learning suggestion failed:', err.message);
    return reply(500, { error: 'Something broke on our end. Try again in a minute?' });
  }
};
