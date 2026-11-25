const { createHmac } = require('node:crypto');
const ids = new Set([
  'apology', 'homework', 'better-or-faster', 'feeling-understood', 'disclosure',
  'authorship', 'jobs', 'rules', 'credit-card', 'superintelligence'
]);

// Keep one choice per browser and debate. A switch moves the existing vote.
const VOTE = `
local requests = redis.call('INCR', KEYS[3])
if requests == 1 then redis.call('EXPIRE', KEYS[3], 60) end
if requests > 60 then return 0 end
local previous = redis.call('HGET', KEYS[1], ARGV[1])
if previous == ARGV[2] then return 1 end
if previous then redis.call('HINCRBY', KEYS[2], previous, -1) end
redis.call('HSET', KEYS[1], ARGV[1], ARGV[2])
redis.call('HINCRBY', KEYS[2], ARGV[2], 1)
return 1
`;

module.exports = async function debateVote(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return res.status(405).end();
  }

  if (req.headers.origin !== `https://${req.headers.host}` ||
      !/^application\/json(?:;|$)/i.test(req.headers['content-type'] || '')) {
    return res.status(403).end();
  }

  let body = req.body;
  if (typeof body === 'string' && body.length <= 512) {
    try { body = JSON.parse(body); } catch { return res.status(400).end(); }
  }
  if (!body || !ids.has(body.debate) || ![0, 1].includes(body.choice) ||
      typeof body.browser !== 'string' ||
      !/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(body.browser)) {
    return res.status(400).end();
  }

  const url = process.env.KV_REST_API_URL;
  const token = process.env.KV_REST_API_TOKEN;
  if (!url || !token) return res.status(503).end();

  const hash = (value) => createHmac('sha256', token).update(value).digest('hex');
  const voter = hash(`debate:${body.debate}:${body.browser}`);
  const address = String(req.headers['x-forwarded-for'] || '').split(',')[0].trim();
  const rate = hash(`debate-rate:${address || body.browser}`);
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify(['EVAL', VOTE, 3, `debate:v1:${body.debate}:choices`,
        `debate:v1:${body.debate}:counts`, `debate:v1:rate:${rate}`, voter, String(body.choice)]),
      signal: AbortSignal.timeout(5000)
    });
    if (!response.ok) return res.status(503).end();
    const data = await response.json();
    if (data.result === 0) return res.status(429).end();
    return res.status(data.result === 1 ? 204 : 503).end();
  } catch {
    return res.status(503).end();
  }
};
