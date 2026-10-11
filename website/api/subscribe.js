// Newsletter signup. Saves an email address to the site's Upstash Redis store (Vercel Marketplace
// resource "oood-newsletter"; Vercel sets KV_REST_API_URL and KV_REST_API_TOKEN on the project).
//
// Addresses live in one Redis hash, `newsletter:subscribers`, keyed by the lowercased address. Each
// value is JSON: { email, subscribedAt, source }. Signing up twice keeps the first record. Export
// the list with `node scripts/export-subscribers.js`.
//
// Accepts JSON (the page's fetch) or a plain form post (no JS). Form posts redirect back to
// /?subscribed=1#notes. A hidden `website` field catches bots: when it's filled in, the request
// looks successful and nothing is saved. Each IP gets 30 signups an hour (a room on one wifi can all sign up).

const HASH = 'newsletter:subscribers';
const LIMIT_PER_HOUR = 30;
const EMAIL = /^[^\s@<>()[\]\\,;:"]+@[^\s@<>()[\]\\,;:"]+\.[a-z]{2,}$/i;

async function redis(commands) {
  const url = process.env.KV_REST_API_URL;
  const token = process.env.KV_REST_API_TOKEN;
  if (!url || !token) throw new Error('newsletter store is not configured');
  const r = await fetch(`${url}/pipeline`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(commands),
  });
  if (!r.ok) throw new Error(`newsletter store answered ${r.status}`);
  const out = await r.json();
  const bad = out.find((x) => x.error);
  if (bad) throw new Error(bad.error);
  return out.map((x) => x.result);
}

async function readBody(req) {
  if (req.body && typeof req.body === 'object') return req.body;
  const raw = typeof req.body === 'string' ? req.body : '';
  const type = req.headers['content-type'] || '';
  if (type.includes('application/json')) {
    try { return JSON.parse(raw || '{}'); } catch { return {}; }
  }
  return Object.fromEntries(new URLSearchParams(raw));
}

module.exports = async (req, res) => {
  const wantsJson = (req.headers.accept || '').includes('application/json');
  const reply = (status, body) => {
    if (wantsJson) return res.status(status).json(body);
    if (status === 200) return res.redirect(303, '/?subscribed=1#notes');
    return res.status(status).send(body.error || 'Something went wrong.');
  };

  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return reply(405, { error: 'Use the form on outofourdepth.com.' });
  }

  const body = await readBody(req);
  if (body.website) return reply(200, { ok: true }); // honeypot

  const email = String(body.email || '').trim().toLowerCase();
  if (email.length > 254 || !EMAIL.test(email)) {
    return reply(400, { error: 'That email doesn’t look right. Mind checking it?' });
  }

  try {
    const ip = String(req.headers['x-forwarded-for'] || '').split(',')[0].trim() || 'unknown';
    const hourKey = `newsletter:rate:${ip}:${Math.floor(Date.now() / 3600000)}`;
    const [count] = await redis([['INCR', hourKey], ['EXPIRE', hourKey, 3600]]);
    if (count > LIMIT_PER_HOUR) {
      return reply(429, { error: 'Too many tries from here. Give it an hour?' });
    }
    const record = JSON.stringify({ email, subscribedAt: new Date().toISOString(), source: 'website' });
    await redis([['HSETNX', HASH, email, record]]);
    return reply(200, { ok: true });
  } catch (err) {
    console.error('subscribe failed:', err.message);
    return reply(500, { error: 'Something broke on our end. Try again in a minute?' });
  }
};
