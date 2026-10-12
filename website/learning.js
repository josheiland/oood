(function () {
 'use strict';
 var topics = JSON.parse(document.getElementById('learning-data').textContent);
 var grid = document.getElementById('learn-grid'), status = document.getElementById('learn-status');
 var retry = document.getElementById('learn-retry'), search = document.getElementById('learn-search'), sort = document.getElementById('learn-sort');
 var counts = {}, selected = new Set(), filter = 'all', ready = false, pending = new Set(), byVotes = false;
 var cards = new Map(topics.map(function(t) { return [t.id, document.getElementById(t.id)]; }));
 document.querySelector('[data-controls]').hidden = false;
 function update() {
  var query = search.value.trim().toLowerCase(), shown = 0;
  // Default order is the order in learning-topics.json (shallow end first); the toggle sorts by requests
  var ordered = byVotes ? topics.slice().sort(function(a,b) { return (counts[b.id] || 0) - (counts[a.id] || 0); }) : topics.slice();
  ordered.forEach(function(t) {
   var card = cards.get(t.id), button = card.querySelector('[data-vote]');
   var visible = (filter === 'all' || filter === t.kind) && [t.title,t.aka || '',t.description,t.exercise].join(' ').toLowerCase().includes(query);
   card.hidden = !visible; if (visible) shown++;
   button.disabled = !ready || pending.has(t.id);
   button.setAttribute('aria-pressed', String(selected.has(t.id)));
   button.querySelector('[data-count]').textContent = counts[t.id] ? counts[t.id] : '';
   button.querySelector('.learn-vote__label').textContent = pending.has(t.id) ? 'Saving' : selected.has(t.id) ? 'You asked for this' : 'Cover this';
   button.setAttribute('aria-label', (selected.has(t.id) ? 'Take back your request for ' : 'Ask for an episode on ') + t.title + (counts[t.id] ? ', ' + counts[t.id] + ' so far' : ''));
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
   status.textContent = message || '';
  } catch (_) { status.textContent = 'Votes are napping right now. Everything below still works.'; retry.hidden = false; }
  update();
 }
 document.querySelectorAll('[data-filter]').forEach(function(b) { b.addEventListener('click', function() { filter = b.dataset.filter; document.querySelectorAll('[data-filter]').forEach(function(x) { x.setAttribute('aria-pressed',String(x === b)); }); update(); }); });
 search.addEventListener('input',update); retry.addEventListener('click',function() { load(); });
 sort.addEventListener('click',function() { byVotes = !byVotes; sort.setAttribute('aria-pressed',String(byVotes)); update(); });
 grid.addEventListener('click',async function(event) {
  var b = event.target.closest('[data-vote]'); if (!b || b.disabled) return;
  var id = b.dataset.vote, want = !selected.has(id); pending.add(id); update();
  try {
   var response = await fetch('/api/learning-votes', { method: 'POST', credentials: 'same-origin', headers: { 'Content-Type':'application/json' }, body: JSON.stringify({ topic:id, voted:want }) });
   var data = await response.json();
   if (!response.ok) throw new Error(data.error || 'Vote could not be saved');
   counts[id] = data.count; if (data.voted) selected.add(id); else selected.delete(id);
   status.textContent = data.voted ? 'Got it. That one\u2019s on our list.' : 'Taken back. No hard feelings.';
  } catch (error) {
   // A timed-out write may have succeeded. Read back; never blindly send a second vote.
   await load('We refreshed the votes. Check your picks before trying again.');
   if (ready) status.textContent = error.message + ' Your picks have been refreshed.';
  } finally { pending.delete(id); update(); }
 });
 load();
})();
