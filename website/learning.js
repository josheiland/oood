// Learning page: upvotes (shared, through /api/learning-votes), search, "Shallow to deep" / "Most wanted"
// sort, and "Suggest a word" (stored through /api/learning-suggest). The rows are already in the HTML
// (scripts/build-learning.js), so this only enhances them.
(function () {
  'use strict';
  var $ = function (id) { return document.getElementById(id); };
  var words = JSON.parse($('learning-data').textContent);
  var list = $('learn-list'), q = $('learn-q'), status = $('learn-status'), retry = $('learn-retry');
  var rows = {}; words.forEach(function (t) { rows[t.id] = $('w-' + t.id); });
  var counts = {}, selected = {}, pending = {}, ready = false, sort = 'shallow', query = '';
  document.querySelector('[data-controls]').hidden = false;

  function paint(t) {
    var b = rows[t.id].querySelector('[data-vote]'), n = counts[t.id] || 0, mine = !!selected[t.id];
    b.disabled = !ready || !!pending[t.id];
    b.setAttribute('aria-pressed', String(mine));
    b.querySelector('[data-count]').textContent = n ? n : '';
    b.querySelector('.w').textContent = pending[t.id] ? 'Saving' : mine ? 'Upvoted' : 'Upvote';
    b.setAttribute('aria-label', (mine ? 'Remove your upvote for ' : 'Upvote ') + t.title + (n ? ', ' + n + ' so far' : ''));
  }
  function render() {
    // The JSON order is simplest first; "Most wanted" sorts by upvotes and keeps that order for ties
    var order = sort === 'wanted' ? words.slice().sort(function (a, b) { return (counts[b.id] || 0) - (counts[a.id] || 0); }) : words;
    var shown = 0;
    list.classList.toggle('is-ranked', sort === 'wanted');
    order.forEach(function (t) {
      var row = rows[t.id], text = [t.title, t.aka || '', t.definition, t.think].join(' ').toLowerCase();
      var visible = !query || text.indexOf(query) >= 0;
      row.hidden = !visible;
      if (visible) shown++;
      row.querySelector('.learn-row__rank').textContent = visible ? shown : '';
      paint(t);
      list.appendChild(row);
    });
    $('learn-empty').hidden = shown > 0;
    if (!shown) $('learn-empty-text').textContent = 'Nothing for "' + q.value.trim() + '" yet.';
  }

  async function load(message) {
    ready = false; retry.hidden = true; words.forEach(paint);
    try {
      var r = await fetch('/api/learning-votes', { cache: 'no-store', credentials: 'same-origin' });
      if (!r.ok) throw new Error('votes unavailable');
      var data = await r.json();
      counts = data.counts || {}; selected = {};
      (data.selected || []).forEach(function (id) { selected[id] = true; });
      ready = true; status.textContent = message || '';
    } catch (_) {
      status.textContent = 'Upvotes are napping right now. Everything else still works.';
      retry.hidden = false;
    }
    render();
  }

  var toastEl = $('learn-toast'), toastTimer;
  function toast(s) { toastEl.textContent = s; toastEl.classList.add('is-on'); clearTimeout(toastTimer); toastTimer = setTimeout(function () { toastEl.classList.remove('is-on'); }, 2400); }

  list.addEventListener('click', async function (e) {
    var b = e.target.closest('[data-vote]'); if (!b || b.disabled) return;
    var id = b.dataset.vote, t = words.filter(function (w) { return w.id === id; })[0], want = !selected[id];
    pending[id] = true; paint(t);
    try {
      var r = await fetch('/api/learning-votes', { method: 'POST', credentials: 'same-origin', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ topic: id, voted: want }) });
      var data = await r.json();
      if (!r.ok) throw new Error(data.error || 'That upvote didn’t save.');
      counts[id] = data.count;
      if (data.voted) selected[id] = true; else delete selected[id];
      delete pending[id]; paint(t);  // update in place so the row doesn't jump while you're reading
      b.classList.remove('is-bump'); void b.offsetWidth; if (data.voted) b.classList.add('is-bump');
      toast(data.voted ? t.title + ' is on our list. Thanks!' : 'Upvote removed. No hard feelings.');
    } catch (err) {
      // A timed-out write may still have landed. Read back instead of sending the vote again.
      delete pending[id];
      await load(err.message + ' We refreshed the upvotes, so check yours before trying again.');
    }
  });

  function setSort(s) {
    sort = s;
    $('learn-sort-shallow').setAttribute('aria-pressed', String(s === 'shallow'));
    $('learn-sort-wanted').setAttribute('aria-pressed', String(s === 'wanted'));
    render();
  }
  $('learn-sort-shallow').addEventListener('click', function () { setSort('shallow'); });
  $('learn-sort-wanted').addEventListener('click', function () { setSort('wanted'); });
  q.addEventListener('input', function () { query = q.value.trim().toLowerCase(); render(); });
  retry.addEventListener('click', function () { load(); });

  // Suggest a word. Without JavaScript the form posts normally and the API redirects back with ?suggested=1.
  var form = $('learn-suggest-form'), input = $('learn-suggest-input'), done = $('learn-suggest-done');
  if (/[?&]suggested=1/.test(location.search)) done.textContent = 'Got it. Thanks for the suggestion!';
  form.addEventListener('submit', async function (e) {
    e.preventDefault();
    var w = input.value.replace(/\s+/g, ' ').trim(), btn = form.querySelector('button');
    if (w.length < 2) { done.textContent = 'Type a word or a question first.'; input.focus(); return; }
    btn.disabled = true; done.textContent = 'Sending';
    try {
      var r = await fetch('/api/learning-suggest', { method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'application/json' }, body: JSON.stringify({ word: w, website: form.website.value }) });
      var data = await r.json().catch(function () { return {}; });
      if (!r.ok) { done.textContent = data.error || 'That didn’t send. Try again in a minute?'; return; }
      done.textContent = 'Got it. "' + w + '" is on our list to look at.';
      input.value = '';
    } catch (_) {
      done.textContent = 'That didn’t send. Check your connection and try again?';
    } finally { btn.disabled = false; }
  });
  $('learn-empty-suggest').addEventListener('click', function () {
    input.value = q.value.trim(); $('suggest').scrollIntoView({ block: 'center' }); input.focus({ preventScroll: true });
  });

  render();
  load();
})();
