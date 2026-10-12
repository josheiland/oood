(function () {
 'use strict';
 var topics = JSON.parse(document.getElementById('learning-data').textContent);
 var grid = document.getElementById('learn-grid'), status = document.getElementById('learn-status');
 var retry = document.getElementById('learn-retry'), search = document.getElementById('learn-search'), sort = document.getElementById('learn-sort');
 var counts = {}, selected = new Set(), filter = 'all', ready = false, pending = new Set();
 var cards = new Map(topics.map(function(t) { return [t.id, document.getElementById(t.id)]; }));
 document.querySelector('[data-controls]').hidden = false;
 function update() {
  var query = search.value.trim().toLowerCase(), shown = 0;
  var ordered = topics.slice().sort(function(a,b) { return sort.value === 'votes' ? (counts[b.id] || 0) - (counts[a.id] || 0) : Number(b.starter) - Number(a.starter); });
  ordered.forEach(function(t) {
   var card = cards.get(t.id), button = card.querySelector('[data-vote]');
   var visible = (filter === 'all' || filter === t.kind) && [t.title,t.description,t.pillar,t.exercise].join(' ').toLowerCase().includes(query);
   card.hidden = !visible; if (visible) shown++;
   button.disabled = !ready || pending.has(t.id);
   button.setAttribute('aria-pressed', String(selected.has(t.id)));
   button.querySelector('[data-count]').textContent = Object.prototype.hasOwnProperty.call(counts,t.id) ? counts[t.id] : '';
   button.querySelector('.learn-vote__label').textContent = pending.has(t.id) ? 'Saving' : selected.has(t.id) ? 'Requested' : 'Explore next';
   button.setAttribute('aria-label', (selected.has(t.id) ? 'Remove your request for ' : 'Explore ') + t.title + (selected.has(t.id) ? '' : ' in a future episode'));
   grid.appendChild(card);
  });
  document.getElementById('learn-empty').hidden = shown !== 0;
 }
 async function load(message) {
  ready = false; update(); retry.hidden = true;
  try {
   var response = await fetch('/api/learning-votes', { cache: 'no-store', credentials: 'same-origin' });
   if (!response.ok) throw new Error('Could not load votes');
   var data = await response.json(); counts = data.counts; selected = new Set(data.selected); ready = true;
   status.textContent = message || 'Your picks help shape future episodes.';
  } catch (_) { status.textContent = 'Votes are unavailable right now. You can still explore everything below.'; retry.hidden = false; }
  update();
 }
 document.querySelectorAll('[data-filter]').forEach(function(b) { b.addEventListener('click', function() { filter = b.dataset.filter; document.querySelectorAll('[data-filter]').forEach(function(x) { x.setAttribute('aria-pressed',String(x === b)); }); update(); }); });
 search.addEventListener('input',update); sort.addEventListener('change',update); retry.addEventListener('click',function() { load(); });
 grid.addEventListener('click',async function(event) {
  var b = event.target.closest('[data-vote]'); if (!b || b.disabled) return;
  var id = b.dataset.vote, want = !selected.has(id); pending.add(id); update();
  try {
   var response = await fetch('/api/learning-votes', { method: 'POST', credentials: 'same-origin', headers: { 'Content-Type':'application/json' }, body: JSON.stringify({ topic:id, voted:want }) });
   var data = await response.json();
   if (!response.ok) throw new Error(data.error || 'Vote could not be saved');
   counts[id] = data.count; if (data.voted) selected.add(id); else selected.delete(id);
   status.textContent = data.voted ? 'Requested! Thanks for helping us pick our next deep dive.' : 'Your request was removed.';
  } catch (error) {
   // A timed-out write may have succeeded. Read back; never blindly send a second vote.
   await load('Votes refreshed. Check your picks before trying again.');
   if (ready) status.textContent = error.message + ' Your picks have been refreshed.';
  } finally { pending.delete(id); update(); }
 });
 load();
})();
