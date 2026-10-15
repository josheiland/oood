// Exercise the live shared-vote API, restoring the temporary test vote in finally.
// No subscriber access. No accounts or identity are stored; output contains no cookies.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const crypto = require('node:crypto');
const base = process.argv[2] || 'https://outofourdepth.com';
const output = process.argv[3] || '/private/tmp/oood-learning-live-check.json';
const report = { checkedAt: new Date().toISOString(), base, checks: [] };
async function snapshot(cookie) {
 const r = await fetch(base+'/api/learning-votes', { headers: cookie ? {Cookie:cookie} : {} });
 assert.equal(r.status,200); assert.match(r.headers.get('cache-control'),/no-store/);
 const data=await r.json();return {data,cookie:cookie || r.headers.get('set-cookie').split(';')[0]};
}
async function vote(cookie,topic,voted,origin=base) {
 const r=await fetch(base+'/api/learning-votes',{method:'POST',headers:{Cookie:cookie,Origin:origin,'Content-Type':'application/json'},body:JSON.stringify({topic,voted})});return {status:r.status,data:await r.json()};
}
(async()=>{
 for (const [url,path] of [['/learning','website/learning.html'],['/learning.js','website/learning.js'],['/learning.css','website/learning.css'],['/learning-topics.json','website/learning-topics.json'],['/main.js','website/main.js'],['/styles.css','website/styles.css'],['/','website/index.html']]) {
  const r=await fetch(base+url);assert.equal(r.status,200,url);const b=Buffer.from(await r.arrayBuffer());assert.equal(crypto.createHash('sha256').update(b).digest('hex'),crypto.createHash('sha256').update(fs.readFileSync(path)).digest('hex'),url);report.checks.push({asset:url,exactLocalMatch:true});
 }
 const one=await snapshot(); const two=await snapshot();
 assert.equal(Object.keys(one.data.counts).length,JSON.parse(fs.readFileSync('website/learning-topics.json','utf8')).length);assert.equal(one.data.selected.length,0);assert.equal(two.data.selected.length,0);
 const topic='token', before=one.data.counts[topic];let wrote=false;
 try {
  const bad=await vote(one.cookie,topic,true,'https://invalid.example');assert.equal(bad.status,403);
  const unknown=await vote(one.cookie,'invented-topic',true);assert.equal(unknown.status,400);
  const tamper=await vote(one.cookie.slice(0,-1)+(one.cookie.endsWith('A')?'B':'A'),topic,true);assert.equal(tamper.status,409);
  // Same desired state, concurrently: a request must not be counted twice.
  wrote=true;const pair=await Promise.all([vote(one.cookie,topic,true),vote(one.cookie,topic,true)]);
  pair.forEach(r=>{assert.equal(r.status,200);assert.equal(r.data.count,before+1);});
  const reload=await snapshot(one.cookie);assert.ok(reload.data.selected.includes(topic));
  const shared=await snapshot(two.cookie);assert.equal(shared.data.counts[topic],before+1);assert.ok(!shared.data.selected.includes(topic));
  report.checks.push({sharedAcrossVisitors:true,persistsOnReload:true,concurrentDuplicateCountedOnce:true,invalidOriginRejected:true,unknownTopicRejected:true,tamperedCookieRejected:true});
 } finally {
  if(wrote){const remove=await vote(one.cookie,topic,false);assert.equal(remove.status,200);const restored=await snapshot(one.cookie);assert.ok(!restored.data.selected.includes(topic));assert.equal(restored.data.counts[topic],before);report.checks.push({temporaryTestVoteRemoved:true,topic,baselineCount:before});}
 }
 report.passed=true;fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
})().catch(err=>{report.passed=false;report.error=err.message;fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n');console.error(err.message);process.exitCode=1;});
