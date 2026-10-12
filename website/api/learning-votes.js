// Shared, anonymous topic requests. Uses the existing site Redis; no emails or accounts.
const { randomUUID, createHmac, timingSafeEqual } = require('node:crypto');
const topics = require('../learning-topics.json');
const ids = topics.map(t => t.id);
const COOKIE = 'oood_learning';
const COUNTS = 'learning:v1:counts';
const CHANGE_VOTE = `
local rate = redis.call('INCR', KEYS[3])
if rate == 1 then redis.call('EXPIRE', KEYS[3], 3600) end
if rate > 120 then return {-1, 0} end
local had = redis.call('SISMEMBER', KEYS[2], ARGV[1])
local want = tonumber(ARGV[2])
if had ~= want then
 if want == 1 then redis.call('SADD', KEYS[2], ARGV[1])
 else redis.call('SREM', KEYS[2], ARGV[1]) end
 redis.call('HINCRBY', KEYS[1], ARGV[1], want - had)
end
return {want, tonumber(redis.call('HGET', KEYS[1], ARGV[1]) or '0')}
`;
async function redis(commands) {
 const url = process.env.KV_REST_API_URL, token = process.env.KV_REST_API_TOKEN;
 if (!url || !token) throw new Error('Learning votes store is not configured');
 const response = await fetch(`${url}/pipeline`, { method: 'POST', headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' }, body: JSON.stringify(commands), signal: AbortSignal.timeout(8000) });
 if (!response.ok) throw new Error(`Learning store returned ${response.status}`);
 const results = await response.json();
 if (!Array.isArray(results) || results.some(x => x.error)) throw new Error('Learning store request failed');
 return results.map(x => x.result);
}
function sign(value) { return createHmac('sha256', process.env.KV_REST_API_TOKEN).update(`learning:v1:${value}`).digest('base64url'); }
function visitor(req) {
 const raw = String(req.headers.cookie || '').split(';').map(x => x.trim()).find(x => x.startsWith(COOKIE + '='));
 if (!raw) return null;
 const value = raw.slice(COOKIE.length + 1), dot = value.indexOf('.');
 const id = value.slice(0, dot), signature = value.slice(dot + 1);
 if (!/^[0-9a-f-]{36}$/.test(id) || !/^[A-Za-z0-9_-]{43}$/.test(signature)) return null;
 const expected = sign(id);
 return timingSafeEqual(Buffer.from(signature), Buffer.from(expected)) ? id : null;
}
module.exports = async (req, res) => {
 res.setHeader('Cache-Control', 'private, no-store');
 res.setHeader('Vary', 'Cookie');
 if (!['GET','POST'].includes(req.method)) { res.setHeader('Allow','GET, POST'); return res.status(405).json({ error: 'Use the Learning page to vote.' }); }
 if (!process.env.KV_REST_API_TOKEN) return res.status(503).json({ error: 'Votes are taking a break. Please try again soon.' });
 try {
  let id = visitor(req);
  if (req.method === 'GET') {
   if (!id) { id = randomUUID(); res.setHeader('Set-Cookie', `${COOKIE}=${id}.${sign(id)}; Path=/api/learning-votes; HttpOnly; Secure; SameSite=Lax; Max-Age=31536000`); }
   const [counts, selected] = await redis([['HMGET', COUNTS, ...ids], ['SMEMBERS', `learning:v1:voter:${id}`]]);
   return res.status(200).json({ counts: Object.fromEntries(ids.map((key,i) => [key, Math.max(0, Number(counts[i] || 0))])), selected: selected.filter(key => ids.includes(key)) });
  }
  let origin; try { origin = new URL(req.headers.origin).host; } catch { origin = null; }
  if (origin !== req.headers.host || !(req.headers['content-type'] || '').includes('application/json')) return res.status(403).json({ error: 'Please vote from the Learning page.' });
  if (!id) return res.status(409).json({ error: 'Enable cookies, then reconnect votes.' });
  let body = req.body;
  if (typeof body === 'string') { if (body.length > 1024) return res.status(400).json({ error: 'Invalid vote.' }); try { body = JSON.parse(body); } catch { body = null; } }
  if (!body || !ids.includes(body.topic) || typeof body.voted !== 'boolean') return res.status(400).json({ error: 'Choose a topic from the Learning page.' });
  const ip = String(req.headers['x-forwarded-for'] || '').split(',')[0].trim();
  const rate = `learning:v1:rate:${sign(ip || id)}:${Math.floor(Date.now()/3600000)}`;
  const [result] = await redis([['EVAL', CHANGE_VOTE, 3, COUNTS, `learning:v1:voter:${id}`, rate, body.topic, body.voted ? 1 : 0]]);
  if (result[0] === -1) return res.status(429).json({ error: 'Lots of votes from here. Give it a little time and try again.' });
  return res.status(200).json({ topic: body.topic, voted: Boolean(result[0]), count: Math.max(0, Number(result[1])) });
 } catch (error) { console.error('Learning votes failed:', error.message); return res.status(503).json({ error: 'We could not reach the votes. Reconnect to check your picks.' }); }
};
