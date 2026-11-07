// Newsletter pop-up (homepage only). Same endpoint and copy family as the navy bar at the bottom of
// the page, which stays as it is. Built 2026-11-06 for the 1,000-subscriber push.
//
// When it shows: after 25 seconds on the page, or once the visitor has scrolled half the page, or
// when the mouse leaves through the top of the window on a desktop. Never in the first 6 seconds.
// It skips the moment if the bottom signup bar is on screen or someone is typing in it.
// Remembered in localStorage: closing it hides it for 14 days, signing up (here or in the bar)
// hides it for a year. Add ?popup=1 to the URL to see it right away, for review.
(function () {
  var path = location.pathname.replace(/\/+$/, '');
  if (path !== '' && path !== '/index' && path !== '/index.html') return; // not on /learning or anywhere else
  if (!window.HTMLDialogElement || !HTMLDialogElement.prototype.showModal || !window.fetch) return;

  var KEY = 'oood:signup-pop';
  var DAY = 864e5;
  var DISMISS_DAYS = 14;
  var SUBSCRIBED_DAYS = 365;
  var MIN_DELAY = 6000;
  var TIME_TRIGGER = 25000;
  var SCROLL_TRIGGER = 0.5;

  var force = /[?&]popup=1(&|$)/.test(location.search);
  var memo = null; // fallback when storage is blocked: show at most once per page load

  function read() {
    try { return JSON.parse(localStorage.getItem(KEY) || 'null'); } catch (e) { return memo; }
  }
  function remember(state, days) {
    memo = { state: state, until: Date.now() + days * DAY };
    try { localStorage.setItem(KEY, JSON.stringify(memo)); } catch (e) {}
  }
  window.ooodSignupDone = function () { remember('subscribed', SUBSCRIBED_DAYS); };

  var saved = read();
  if (!force && saved && saved.until > Date.now()) return;
  if (!force && /[?&]subscribed=1/.test(location.search)) return;

  var started = Date.now();
  var shown = false;
  var dialog, form, status, submit, lastFocus;

  function barInUse() {
    var bar = document.querySelector('.notes');
    if (!bar) return false;
    if (bar.contains(document.activeElement)) return true;
    var r = bar.getBoundingClientRect();
    return r.top < window.innerHeight && r.bottom > 0;
  }

  function build() {
    dialog = document.createElement('dialog');
    dialog.className = 'signup-pop';
    dialog.setAttribute('aria-labelledby', 'signup-pop-title');
    dialog.setAttribute('aria-describedby', 'signup-pop-sub');
    dialog.setAttribute('aria-modal', 'true');
    dialog.setAttribute('data-signup-pop', '');
    dialog.innerHTML =
      '<div class="signup-pop__card">' +
        '<button class="signup-pop__x" type="button" data-pop-close aria-label="Close">' +
          '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/></svg>' +
        '</button>' +
        '<p class="signup-pop__label">The newsletter</p>' +
        '<h2 class="signup-pop__title" id="signup-pop-title">Want a copy of our notes?</h2>' +
        '<p class="signup-pop__sub" id="signup-pop-sub">We take notes as we learn AI for the show. Once a month we send them to you, in plain English. That’s the whole email.</p>' +
        '<form class="signup-pop__form" action="/api/subscribe" method="post" novalidate>' +
          '<label class="visually-hidden" for="signup-pop-email">Email address</label>' +
          '<input class="notes__input signup-pop__input" id="signup-pop-email" name="email" type="email" inputmode="email" autocomplete="email" placeholder="you@email.com" required>' +
          '<input class="notes__hp" name="website" type="text" tabindex="-1" autocomplete="off" aria-hidden="true">' +
          '<button class="notes__btn signup-pop__btn" type="submit">Send me the notes</button>' +
          '<p class="notes__status signup-pop__status" role="status" aria-live="polite"></p>' +
        '</form>' +
        '<button class="signup-pop__later" type="button" data-pop-close>Not now</button>' +
      '</div>';
    document.body.appendChild(dialog);

    form = dialog.querySelector('form');
    status = dialog.querySelector('[role="status"]');
    submit = form.querySelector('button[type="submit"]');

    dialog.querySelectorAll('[data-pop-close]').forEach(function (b) {
      b.addEventListener('click', function () { close(); });
    });
    // Esc: the browser fires cancel on a modal dialog
    dialog.addEventListener('cancel', function (e) { e.preventDefault(); close(); });
    // A click on the dimmed area lands on the dialog itself, outside the card
    dialog.addEventListener('mousedown', function (e) { dialog._downOutside = e.target === dialog; });
    dialog.addEventListener('click', function (e) {
      if (e.target === dialog && dialog._downOutside) close();
    });
    // Keep Tab inside the card
    dialog.addEventListener('keydown', function (e) {
      if (e.key !== 'Tab') return;
      var f = Array.prototype.filter.call(
        dialog.querySelectorAll('button, input:not([tabindex="-1"])'),
        function (el) { return !el.disabled && el.offsetParent !== null; }
      );
      if (!f.length) return;
      var first = f[0], last = f[f.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    });
    form.addEventListener('submit', onSubmit);
  }

  function say(msg, ok) {
    status.textContent = msg;
    status.className = 'notes__status signup-pop__status ' + (ok ? 'notes__status--ok' : 'notes__status--err');
  }

  function onSubmit(e) {
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
          remember('subscribed', SUBSCRIBED_DAYS);
          dialog.classList.add('signup-pop--done');
          form.reset();
          say('You’re on the list. Talk soon.', true);
          var later = dialog.querySelector('.signup-pop__later');
          later.textContent = 'Close';
          later.focus();
        } else {
          say(res.d.error || 'Something broke on our end. Try again in a minute?', false);
        }
      })
      .catch(function () { say('Something broke on our end. Try again in a minute?', false); })
      .then(function () { submit.disabled = false; });
  }

  function open(reason) {
    if (shown) return;
    if (!force && (Date.now() - started < MIN_DELAY || barInUse())) return;
    shown = true;
    teardown();
    build();
    lastFocus = document.activeElement;
    dialog.dataset.trigger = reason;
    dialog.showModal();
    form.email.focus({ preventScroll: true });
  }

  function close() {
    if (!dialog || !dialog.open) return;
    if (!dialog.classList.contains('signup-pop--done')) remember('dismissed', DISMISS_DAYS);
    dialog.close();
    dialog.remove();
    if (lastFocus && lastFocus.focus) lastFocus.focus({ preventScroll: true });
  }

  // Triggers
  var timer = setTimeout(function () { open('time'); }, TIME_TRIGGER);
  function onScroll() {
    var doc = document.documentElement;
    var max = doc.scrollHeight - window.innerHeight;
    if (max > 0 && window.scrollY / max >= SCROLL_TRIGGER) open('scroll');
  }
  function onExit(e) {
    if (!e.relatedTarget && e.clientY <= 0) open('exit');
  }
  var finePointer = window.matchMedia && matchMedia('(hover: hover) and (pointer: fine)').matches;
  window.addEventListener('scroll', onScroll, { passive: true });
  if (finePointer) document.documentElement.addEventListener('mouseout', onExit);

  function teardown() {
    clearTimeout(timer);
    window.removeEventListener('scroll', onScroll);
    document.documentElement.removeEventListener('mouseout', onExit);
  }

  if (force) open('preview');
})();
