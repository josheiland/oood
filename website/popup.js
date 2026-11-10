// Email pop-up (Mary, 2026-11-10). Asks once, politely, for the same list as the signup band at the
// bottom of the homepage. It posts to /api/subscribe with source "popup", so the export shows which
// form each address came from.
//
// When it shows (whichever comes first, never on page load):
//   Laptops: 20 seconds on the page, scrolling half the page, or the mouse heading for the tab bar.
//   Phones: 30 seconds or half the page, as a small sheet along the bottom that never covers the
//   whole screen (Google ranks pages lower on phones when a pop-up blocks the content).
// It never shows twice in one visit, stays away 14 days after "No thanks" or the close button,
// never comes back after a signup (from either form), and waits while the signup band is on screen.
(function () {
  var KEY = 'oood.popup';
  var SNOOZE_DAYS = 14;
  var LAPTOP_DELAY = 20000;
  var PHONE_DELAY = 30000;
  var EXIT_ARMED_AFTER = 5000; // ignore the mouse leaving the window in the first 5 seconds

  function load() { try { return JSON.parse(localStorage.getItem(KEY) || '{}'); } catch (e) { return {}; } }
  function save(v) { try { localStorage.setItem(KEY, JSON.stringify(v)); } catch (e) {} }

  var state = load();
  if (/[?&]subscribed=1/.test(location.search)) { save({ subscribed: true }); return; }
  if (/[?&]popup=1/.test(location.search)) state = {}; // preview: ?popup=1 always shows it
  else {
    if (state.subscribed) return;
    if (state.dismissedAt && Date.now() - state.dismissedAt < SNOOZE_DAYS * 864e5) return;
    try { if (sessionStorage.getItem(KEY)) return; } catch (e) {}
  }
  if (!window.fetch || !document.querySelector || !window.matchMedia) return;

  var phone = window.matchMedia('(max-width: 640px)').matches;
  var preview = /[?&]popup=1/.test(location.search);
  var started = Date.now();
  var shown = false;
  var lastFocus = null;
  var timer = null;

  // Don't interrupt someone who is already looking at the signup band
  var band = document.querySelector('.notes');
  var bandOnScreen = false;
  if (band && 'IntersectionObserver' in window) {
    new IntersectionObserver(function (entries) {
      bandOnScreen = entries[0].isIntersecting;
    }).observe(band);
  }

  function track(name) { try { if (window.va) window.va('event', { name: name }); } catch (e) {} }

  var root = document.createElement('div');
  root.className = 'pop' + (phone ? ' pop--sheet' : '');
  root.hidden = true;
  root.innerHTML =
    '<div class="pop__card" role="dialog" aria-labelledby="pop-title" aria-describedby="pop-sub"' + (phone ? '' : ' aria-modal="true"') + ' tabindex="-1">' +
      '<button class="pop__close" type="button" aria-label="Close">' +
        '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/></svg>' +
      '</button>' +
      '<p class="pop__kicker">The notes</p>' +
      '<h2 class="pop__title" id="pop-title">We <s class="pop__strike" aria-hidden="true">doodle</s> take notes. Want a copy?</h2>' +
      '<p class="pop__sub" id="pop-sub">What we learned from each episode, in plain words. No more than one cute little email each month.</p>' +
      '<form class="pop__form" action="/api/subscribe" method="post" novalidate>' +
        '<label class="visually-hidden" for="pop-email">Email address</label>' +
        '<input class="pop__input" id="pop-email" name="email" type="email" inputmode="email" autocomplete="email" placeholder="you@email.com" required>' +
        '<input class="notes__hp" name="website" type="text" tabindex="-1" autocomplete="off" aria-hidden="true">' +
        '<input type="hidden" name="source" value="popup">' +
        '<button class="pop__btn" type="submit">Send me the notes</button>' +
        '<p class="pop__status" role="status" aria-live="polite"></p>' +
      '</form>' +
      '<button class="pop__no" type="button">No thanks</button>' +
    '</div>';

  var card = root.querySelector('.pop__card');
  var form = root.querySelector('form');
  var status = root.querySelector('.pop__status');
  var submit = root.querySelector('.pop__btn');

  function say(msg, ok) {
    status.textContent = msg;
    status.className = 'pop__status' + (ok ? ' pop__status--ok' : ' pop__status--err');
  }

  function stopTriggers() {
    clearTimeout(timer);
    window.removeEventListener('scroll', onScroll);
    document.removeEventListener('mouseout', onLeave);
  }

  function open(reason) {
    if (shown) return;
    if (bandOnScreen && !preview) return; // try again on the next trigger
    shown = true;
    stopTriggers();
    try { sessionStorage.setItem(KEY, '1'); } catch (e) {}
    lastFocus = document.activeElement;
    document.body.appendChild(root);
    root.hidden = false;
    requestAnimationFrame(function () { root.classList.add('pop--in'); });
    // On laptops, put the cursor in the email field. On phones that would throw up the keyboard
    // over the page, so focus stays where it was.
    if (!phone) setTimeout(function () { root.querySelector('.pop__input').focus(); }, 60);
    document.addEventListener('keydown', onKey);
    track('popup_shown_' + reason);
  }

  function close(remember) {
    root.classList.remove('pop--in');
    document.removeEventListener('keydown', onKey);
    setTimeout(function () { root.hidden = true; }, 220);
    if (remember === 'dismissed') { save({ dismissedAt: Date.now() }); track('popup_dismissed'); }
    if (lastFocus && lastFocus.focus && !phone) lastFocus.focus();
  }

  function onKey(e) {
    if (e.key === 'Escape') { close('dismissed'); return; }
    if (e.key !== 'Tab' || phone) return;
    // Keep Tab inside the pop-up on laptops, where it is modal
    var items = card.querySelectorAll('button, input:not([type=hidden]):not([tabindex="-1"])');
    var first = items[0];
    var last = items[items.length - 1];
    if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
  }

  function onScroll() {
    var seen = window.scrollY + window.innerHeight;
    if (seen >= document.documentElement.scrollHeight * 0.5) open('scroll');
  }

  function onLeave(e) {
    if (e.relatedTarget || e.clientY > 0) return;
    if (Date.now() - started < EXIT_ARMED_AFTER) return;
    open('exit');
  }

  root.querySelector('.pop__close').addEventListener('click', function () { close('dismissed'); });
  root.querySelector('.pop__no').addEventListener('click', function () { close('dismissed'); });
  root.addEventListener('click', function (e) { if (e.target === root) close('dismissed'); });

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var email = form.email.value.trim();
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      say('That email doesn’t look right. Mind checking it?', false);
      form.email.focus();
      return;
    }
    submit.disabled = true;
    fetch('/api/subscribe', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify({ email: email, website: form.website.value, source: 'popup' })
    })
      .then(function (r) { return r.json().catch(function () { return {}; }).then(function (d) { return { ok: r.ok, d: d }; }); })
      .then(function (res) {
        if (res.ok) {
          save({ subscribed: true });
          track('popup_subscribed');
          say("You're on the list. Talk soon.", true);
          form.reset();
          setTimeout(function () { close(); }, 2200);
        } else {
          say(res.d.error || 'Something broke on our end. Try again in a minute?', false);
        }
      })
      .catch(function () { say('Something broke on our end. Try again in a minute?', false); })
      .then(function () { submit.disabled = false; });
  });

  if (preview) { open('preview'); return; }
  timer = setTimeout(function () { open('timer'); }, phone ? PHONE_DELAY : LAPTOP_DELAY);
  window.addEventListener('scroll', onScroll, { passive: true });
  if (!phone) document.addEventListener('mouseout', onLeave);
})();
